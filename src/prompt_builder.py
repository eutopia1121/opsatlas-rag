def build_context(results: list[dict]) -> str:
    """将检索结果整理为可放入 Prompt 的参考资料。"""
    sections = []

    for index, result in enumerate(results, start=1):
        section = (
            f"[资料 {index}]\n"
            f"来源：{result['source']}\n"
            f"标题：{result['title']}\n"
            f"内容：\n{result['content']}"
        )

        sections.append(section)

    return "\n\n".join(sections)


def build_prompt(question: str, context: str) -> str:
    """将用户问题和检索资料组成 RAG Prompt。"""
    return f"""你是 OpsAtlas 设备运维知识库助手。

请严格依据“参考资料”回答用户问题。

回答要求：
1. 只能使用参考资料中的信息，不要补充资料外的事实。
2. 如果参考资料不足以回答，请明确说“根据当前知识库资料无法确定”。
3. 回答应简洁、清晰；涉及操作步骤时按顺序说明。

参考资料：
{context}

用户问题：
{question}
"""

if __name__ == "__main__":
    from retriever import search_knowledge

    question = "设备出现 E205 时应如何处理？"

    results = search_knowledge(question, top_k=3)
    context = build_context(results)
    prompt = build_prompt(question, context)

    print(prompt)