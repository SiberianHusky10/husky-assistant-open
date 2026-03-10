# llm.py（建议单独文件）
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

_SYSTEM_PROMPT = (
    "你是一个严谨、正式的 AI 助手。\n"
    "输出规则：\n"
    "1. 不要使用任何 Markdown 语法\n"
    "2. 不要使用星号\n"
    "3. 不要使用表情符号\n"
    "4. 不要使用列表符号\n"
    "5. 只使用自然的纯文本回答\n"
)

_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def call_llm(user_text: str) -> str:
    response = _client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        timeout=30,
    )

    return response.choices[0].message.content.strip()
