from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-small-zh-v1.5"

model = SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """把多段文本转换为归一化向量。"""
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
    )

    return vectors.tolist()

def embed_chunks(chunks: list[dict]) -> list[dict]:
    """将 Chunk 文本向量化，并保留原有元数据。"""
    texts = [chunk["content"] for chunk in chunks]

    vectors = embed_texts(texts)

    records = []

    for chunk, vector in zip(chunks, vectors):
        record = dict(chunk)
        record["vector"] = vector
        records.append(record)

    return records

if __name__ == "__main__":
    from document_loader import RAW_DATA_DIR, load_documents
    from text_splitter import split_documents

    documents = load_documents(RAW_DATA_DIR)
    chunks = split_documents(documents)
    records = embed_chunks(chunks)

    print(f"文档数量：{len(documents)}")
    print(f"Chunk 数量：{len(chunks)}")
    print(f"向量记录数量：{len(records)}\n")

    first_record = records[0]

    print(f"Chunk 编号：{first_record['chunk_id']}")
    print(f"来源：{first_record['source']}")
    print(f"标题：{first_record['title']}")
    print(f"向量维度：{len(first_record['vector'])}")
    print(f"向量前 5 个值：{first_record['vector'][:5]}")