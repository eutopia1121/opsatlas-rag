from deepseek_client import ask_deepseek
from prompt_builder import build_context, build_prompt
from retriever import search_knowledge
from logger_config import setup_logger

logger = setup_logger()


def ask_knowledge_base(question: str) -> tuple[str, list[dict]]:
    """执行完整 RAG 问答流程。"""
    logger.info("收到知识库问答请求：%s", question)
    results = search_knowledge(question, top_k=3)

    logger.info("检索完成，符合阈值的资料数量：%s", len(results))

    if not results:
        logger.warning("未检索到可靠资料：%s", question)
        return "根据当前知识库资料无法确定。", []

    context = build_context(results)

    prompt = build_prompt(
        question=question,
        context=context,
    )

    logger.info("准备调用 DeepSeek 生成回答")

    answer = ask_deepseek(prompt)

    logger.info("回答生成完成，返回资料数量：%s", len(results))

    return answer, results


if __name__ == "__main__":
    question = "设备采购价格是多少？"

    answer, results = ask_knowledge_base(question)

    print("回答：")
    print(answer)
    print("\n参考来源：")

    if results:
        for index, result in enumerate(results, start=1):
            print(
                f"[{index}] "
                f"{result['source']} - "
                f"{result['title']} "
                f"(Chunk {result['chunk_id']})"
            )
    else:
        print("无（未检索到达到阈值的可靠资料）")