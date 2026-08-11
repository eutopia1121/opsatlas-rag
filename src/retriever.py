from embedding import embed_texts
from milvus_client import COLLECTION_NAME, client
MIN_SCORE = 0.55

def embed_question(question: str) -> list[float]:
    """将用户问题转换为单个检索向量。"""
    if not question.strip():
        raise ValueError("问题不能为空")

    return embed_texts([question])[0]


def search_knowledge(question: str, top_k: int = 3) -> list[dict]:
    """在 Milvus 中检索与问题最相近的前 top_k 条记录。"""
    question_vector = embed_question(question)

    search_results = client.search(
        collection_name=COLLECTION_NAME,
        data=[question_vector],
        limit=top_k,
        output_fields=["source", "title", "content"],
    )

    hits = search_results[0]
    results = []

    for hit in hits:
        entity = hit["entity"]

        results.append(
            {
                "chunk_id": hit["chunk_id"],
                "score": hit["distance"],
                "source": entity["source"],
                "title": entity["title"],
                "content": entity["content"],
            }
        )

    filtered_results = [
        result
        for result in results
        if result["score"] >= MIN_SCORE
    ]

    return filtered_results

if __name__ == "__main__":
    question = "设备采购价格是多少？"

    results = search_knowledge(question, top_k=3)
    print(f"符合阈值的资料数量：{len(results)}\n")
    print(f"用户问题：{question}\n")

    for index, result in enumerate(results, start=1):
        print(f"Top {index}")
        print(f"相似度分数：{result['score']:.4f}")
        print(f"标题：{result['title']}")
        print(f"来源：{result['source']}")
        print(f"内容：{result['content']}")
        print("-" * 40)