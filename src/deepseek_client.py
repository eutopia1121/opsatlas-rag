import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

if not DEEPSEEK_API_KEY:
    raise ValueError("未读取到 DEEPSEEK_API_KEY，请检查 .env 文件")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
)


def ask_deepseek(prompt: str) -> str:
    """将 RAG Prompt 发给 DeepSeek，返回模型回答。"""
    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {
                "role": "system",
                "content": "你是严谨的设备运维知识库助手。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content