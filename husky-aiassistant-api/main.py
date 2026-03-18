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


# 1. 定义请求体格式
class ChatRequest(BaseModel):
    text: str

# 2. 定义接口
@app.post("/chat")
def chat(req: ChatRequest):
    user_text = req.text

    reply = call_llm(user_text)
    print(reply)

    return {
        "code": 0,
        "reply": reply
    }

def call_llm(user_text: str) -> str:
    load_dotenv()
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )

# 1 创建 SQLite 聊天历史
    history = SQLChatMessageHistory(
        session_id="default_user",
        connection_string = "sqlite:///data/chat_memory.db"
    )

    # 2 获取历史消息
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个严谨、正式的 AI 助手。\n"
                "输出规则：\n"
                "1. 不要使用任何 Markdown 语法\n"
                "2. 不要使用星号（*）\n"
                "3. 不要使用表情符号或 Emoji\n"
                "4. 不要使用列表符号\n"
                "5. 只使用自然的纯文本回答\n"
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

    # 3 调用 LLM
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )

    reply = response.choices[0].message.content

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

DB_PATH = "./data/chat_memory.db"

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
