from document_loader import RAW_DATA_DIR, load_documents
from embedding import embed_chunks
from milvus_client import ensure_collection, upsert_records
from text_splitter import split_documents


def ingest() -> None:
    """执行 OpsAtlas 知识库入库流程。"""
    documents = load_documents(RAW_DATA_DIR)
    chunks = split_documents(documents)
    records = embed_chunks(chunks)

    ensure_collection()
    upsert_records(records)

    print("\n入库完成")
    print(f"文档数量：{len(documents)}")
    print(f"Chunk 数量：{len(chunks)}")
    print(f"向量记录数量：{len(records)}")


if __name__ == "__main__":
    ingest()