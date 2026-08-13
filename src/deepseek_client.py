import os
import time

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)

from logger_config import setup_logger


load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

if not DEEPSEEK_API_KEY:
    raise ValueError("未读取到 DEEPSEEK_API_KEY，请检查 .env 文件")


client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
)

logger = setup_logger()

MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 2


def ask_deepseek(prompt: str) -> str:
    """将 RAG Prompt 发给 DeepSeek，失败时自动重试。"""
    total_attempts = MAX_RETRIES + 1

    for attempt in range(1, total_attempts + 1):
        try:
            logger.info(
                "开始调用 DeepSeek：第 %s/%s 次",
                attempt,
                total_attempts,
            )

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

            answer = response.choices[0].message.content

            logger.info("DeepSeek 调用成功：第 %s 次", attempt)

            return answer

        except (
            APIConnectionError,
            InternalServerError,
            RateLimitError,
        ) as error:
            if attempt == total_attempts:
                logger.exception(
                    "DeepSeek 调用最终失败，已尝试 %s 次：%s",
                    total_attempts,
                    error,
                )
                raise

            wait_seconds = RETRY_DELAY_SECONDS * attempt

            logger.warning(
                "DeepSeek 调用失败：第 %s/%s 次，%s 秒后重试：%s",
                attempt,
                total_attempts,
                wait_seconds,
                error,
            )

            time.sleep(wait_seconds)