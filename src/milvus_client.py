import os

from pymilvus import MilvusClient


MILVUS_URI = os.getenv(
    "MILVUS_URI",
    "http://localhost:19530",
)

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

def clear_records() -> None:
    """删除当前知识库中的全部有效记录，用于全量重新入库。"""
    client.delete(
        collection_name=COLLECTION_NAME,
        filter="chunk_id >= 0",
    )

    print("已清空旧知识记录")

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

