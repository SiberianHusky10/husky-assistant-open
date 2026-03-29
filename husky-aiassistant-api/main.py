from fastapi import FastAPI, Query
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import uuid
from fastapi.responses import FileResponse
from fastapi import BackgroundTasks
import time
from routers.voice import router as voice_router
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
import sqlite3
import json
from langchain_community.tools import TavilySearchResults
from langchain_core.utils.function_calling import convert_to_openai_tool
import uvicorn
import datetime
import httpx


app = FastAPI()

# 允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 允许所有域名
    allow_credentials=True,    # 是否允许发送 Cookie
    allow_methods=["*"],       # 允许所有请求方法
    allow_headers=["*"],       # 允许所有请求头
)

app.include_router(voice_router)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# 1. 定义请求体格式
class ChatRequest(BaseModel):
    text: str
    session_id: str | None = "default"

# 2. 定义接口
@app.post("/chat")
def chat(req: ChatRequest):
    user_text = req.text
    session_id = req.session_id or "default"

    reply = call_llm(user_text, session_id)   # 传入 session_id
    print(reply)

    return {
        "code": 0,
        "reply": reply
    }

def call_llm(user_text: str, session_id: str) -> str:
    load_dotenv()
    client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        http_client=httpx.Client(verify=False)
    )
    #可选模型密钥DEEPSEEK_API_KEY，https://api.deepseek.com
    #可选模型密钥STEP_API_KEY，https://api.stepfun.com/v1
    #可选模型密钥OPENROUTER_API_KEY，https://openrouter.ai/api/v1

# 1 创建 SQLite 聊天历史
    history = SQLChatMessageHistory(
        session_id=session_id,
        connection_string=f"sqlite:///{os.path.join(BASE_DIR, 'data', 'chat_memory.db').replace(os.sep, '/')}"
    )

    # 新增： Tavily Search Tool（
    search_tool = TavilySearchResults(
        max_results=3,                    # 返回结果数量
        search_depth="advanced",          # "basic" 或 "advanced"，推荐 advanced（对实时信息如天气更好）
        include_answer=True,              # 让 Tavily 自动生成一个简洁的 AI 总结（极大提升答案质量）
        include_raw_content=False,        # 如果不需要整页原始文本，可设为 False 节省 token
        # include_images=False,           # 如需图片可打开
    )

    # 把 LangChain Tool 转换为 OpenAI 兼容的 tool 格式
    tools = [convert_to_openai_tool(search_tool)]

    # 获取当前香港时间（UTC+8）
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    current_time_str = now.strftime("%Y年%m月%d日 %A %H:%M:%S")
    # 2 获取历史消息
    messages = [
        {
            "role": "system",
            "content": (
            f"你是一个严谨、正式的 AI 助手。\n"
            f"当前时间是：{current_time_str}（香港时间）。\n\n"
            "输出规则：\n"
            "1. 不要使用任何 Markdown 语法\n"
            "2. 不要使用星号（*）\n"
            "3. 不要使用表情符号或 Emoji\n"
            "4. 不要使用列表符号\n"
            "5. 只使用自然的纯文本回答\n\n"
            "请在回答任何涉及日期、时间、时效性的问题时，严格使用上面提供的当前时间。"
        )
        }
    ]

    # 把历史记录加入 messages
    for msg in history.messages:
        if msg.type == "human":
            messages.append({"role": "user", "content": msg.content})
        else:
            messages.append({"role": "assistant", "content": msg.content})

    # 加入当前用户消息
    messages.append({"role": "user", "content": user_text})

    # 3. 第一次调用 LLM（让模型决定是否使用工具）
    response = client.chat.completions.create(
        model="minimax/minimax-m2.5",   # 或你想用的其他模型
        messages=messages,
        tools=tools,
        tool_choice="auto",             # 推荐改成 "auto"，让模型智能决定是否调用工具（比强制调用更好）
        temperature=0.0,
        max_tokens=1024
    )
    #deepseek模型 deepseek-chat
    #step模型 step-3.5-flash

    # 处理可能的 tool calls（这是实现实时查询的核心）
    message = response.choices[0].message
    reply = message.content

    # 如果模型决定调用工具
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = tool_call.function.arguments  # JSON 字符串

        if tool_name == search_tool.name:
            # 执行 Tavily 搜索（Tavily 的 run/invoke 都支持）
            search_result = search_tool.run(tool_args)   # 或 search_tool.invoke(json.loads(tool_args))

            #测试输出结果
            print("TAVILY RAW:", repr(search_result))
            # 把工具调用和结果塞回消息列表
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call.model_dump()]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(search_result)   # Tavily 返回的是结构化字符串或 dict，转 str 即可
            })

            print("second message:", repr(messages))
            # 第二次调用 LLM，生成最终回答
            second_response = client.chat.completions.create(
                model="minimax/minimax-m2.5",
                messages=messages,
                temperature=0.0,
                max_tokens=1024
            )
            reply = second_response.choices[0].message.content

    # 4 保存到 SQLite
    history.add_message(HumanMessage(content=user_text))
    history.add_message(AIMessage(content=reply))

    return reply

async def text_to_speech(text: str) -> str:
    filename = f"audio_{uuid.uuid4()}.mp3"

    communicate = edge_tts.Communicate(
        text=text,
        voice="zh-CN-XiaoxiaoNeural",
        rate="+0%",
        volume="+0%"
    )

    await communicate.save(filename)
    return filename

@app.post("/voicechat")
async def voice_chat(req: ChatRequest, background_tasks: BackgroundTasks):
    # 1. LLM
    reply = call_llm(req.text)

    # 2. TTS
    audio_path = await text_to_speech(reply)

    # 3. 返回后自动删除文件
    background_tasks.add_task(delete_file_later, audio_path, 30)

    return {
        "code": 0,
        "reply": reply,
        "audio_url": f"http://localhost:8000/audio/{audio_path}"
    }

def delete_file_later(path: str, delay: int = 30):
    time.sleep(delay)
    if os.path.exists(path):
        os.remove(path)


@app.get("/audio/{filename}")
def get_audio(filename: str):
    return FileResponse(
        path=filename,
        media_type="audio/mpeg",
        filename="reply.mp3"
    )

DB_PATH = os.path.join(BASE_DIR, "data", "chat_memory.db")

@app.get("/getmessages")
def get_messages(session_id: str = Query(..., description="会话 ID")):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, message FROM message_store WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    messages = []
    for row in rows:
        raw_msg = row[1]  # message 字段是 JSON 字符串
        try:
            msg_obj = json.loads(raw_msg)  # JSON 解析
            # 你可以把前端需要的字段提取出来
            messages.append({
                "role": msg_obj.get("type"),  # human/assistant
                "content": msg_obj.get("data", {}).get("content"),
                "timestamp": msg_obj.get("data", {}).get("timestamp")  # 如果你有 timestamp 字段
            })
        except Exception as e:
            print("JSON解析失败:", e)
            continue

    return messages


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
