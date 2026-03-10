from fastapi import FastAPI
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


app = FastAPI()

app.include_router(voice_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # 前端地址
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
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
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    )

    return response.choices[0].message.content

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

