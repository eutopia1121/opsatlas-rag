from pathlib import Path
##定义文档目录路径常量，批量读取指定目
# 录下md/txt文件并返回包含文件名与全文的文档列表，直接运行时打印读取到的文档数量与内容预览。

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
SUPPORTED_SUFFIXES = {".md", ".txt"}


def load_documents(data_dir: Path) -> list[dict]:
    """读取目录中的 Markdown 和 TXT 文档。"""
    documents = []

    for file_path in data_dir.iterdir():
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue

        documents.append(
            {
                "source": file_path.name,
                "content": file_path.read_text(encoding="utf-8"),
            }
        )

    return documents


if __name__ == "__main__":
    documents = load_documents(RAW_DATA_DIR)

    print(f"读取到 {len(documents)} 份文档\n")

    for document in documents:
        print(f"来源：{document['source']}")
        print(f"内容前 80 个字：{document['content'][:80]}")
        print("-" * 40)