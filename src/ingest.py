from document_loader import RAW_DATA_DIR, load_documents
from embedding import embed_chunks
from milvus_client import clear_records, ensure_collection, upsert_records
from text_splitter import split_documents


def ingest() -> dict:
    """执行 OpsAtlas 知识库入库流程，并返回入库统计信息。"""
    documents = load_documents(RAW_DATA_DIR)
    chunks = split_documents(documents)
    records = embed_chunks(chunks)

    ensure_collection()
    clear_records()
    upsert_records(records)

    summary = {
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "record_count": len(records),
    }

    return summary


if __name__ == "__main__":
    summary = ingest()

    print("\n入库完成")
    print(f"文档数量：{summary['document_count']}")
    print(f"Chunk 数量：{summary['chunk_count']}")
    print(f"向量记录数量：{summary['record_count']}")