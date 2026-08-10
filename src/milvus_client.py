from pymilvus import MilvusClient


MILVUS_URI = "http://localhost:19530"

client = MilvusClient(uri=MILVUS_URI)

COLLECTION_NAME = "opsatlas_knowledge"
VECTOR_DIMENSION = 512


def ensure_collection() -> None:
    """不存在则创建 OpsAtlas 知识库 Collection。"""
    if client.has_collection(COLLECTION_NAME):
        print(f"Collection 已存在：{COLLECTION_NAME}")
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=VECTOR_DIMENSION,
        primary_field_name="chunk_id",
        id_type="int",
        vector_field_name="vector",
        metric_type="COSINE",
        auto_id=False,
        enable_dynamic_field=True,
    )

    print(f"Collection 创建成功：{COLLECTION_NAME}")


def upsert_records(records: list[dict]) -> None:
    """将带向量的 Chunk 记录写入 Milvus。"""
    if not records:
        print("没有需要写入的记录")
        return

    client.upsert(
        collection_name=COLLECTION_NAME,
        data=records,
    )

    print(f"已写入或更新 {len(records)} 条记录")


def get_record_count() -> int:
    """返回当前可查询的知识记录数量。"""
    results = client.query(
        collection_name=COLLECTION_NAME,
        filter="chunk_id >= 0",
        output_fields=["count(*)"],
    )

    return results[0]["count(*)"]

if __name__ == "__main__":
    ensure_collection()

    count = get_record_count()

    print(f"当前 Collection：{COLLECTION_NAME}")
    print(f"当前记录数量：{count}")


if __name__ == "__main__":
    question = "设备出现 E205 时应如何处理？"

    results = search_knowledge(question, top_k=3)

    print(f"用户问题：{question}\n")

    for index, result in enumerate(results, start=1):
        print(f"Top {index}")
        print(f"相似度分数：{result['score']:.4f}")
        print(f"标题：{result['title']}")
        print(f"来源：{result['source']}")
        print(f"内容：{result['content']}")
        print("-" * 40)