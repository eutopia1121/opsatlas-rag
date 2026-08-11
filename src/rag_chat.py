from deepseek_client import ask_deepseek
from prompt_builder import build_context, build_prompt
from retriever import search_knowledge


def ask_knowledge_base(question: str) -> tuple[str, list[dict]]:
    """执行完整 RAG 问答流程。"""
    results = search_knowledge(question, top_k=3)
    if not results:
        return "根据当前知识库资料无法确定。", []

    context = build_context(results)

    prompt = build_prompt(
        question=question,
        context=context,
    )

    answer = ask_deepseek(prompt)

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