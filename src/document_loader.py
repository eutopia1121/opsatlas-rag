from pathlib import Path

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
SUPPORTED_SUFFIXES = {".md", ".txt", ".pdf"}


def load_text_document(file_path: Path) -> list[dict]:
    """读取一份 Markdown 或 TXT 文档。"""
    return [
        {
            "source": file_path.name,
            "page_number": None,
            "content": file_path.read_text(encoding="utf-8"),
        }
    ]


def load_pdf_document(file_path: Path) -> list[dict]:
    """逐页读取 PDF，并去除后续页面重复的页眉标题。"""
    reader = PdfReader(file_path)
    documents = []
    document_title = None

    for page_number, page in enumerate(reader.pages, start=1):
        lines = [
            line.strip()
            for line in page.extract_text().splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        if page_number == 1:
            document_title = lines[0]
        elif lines[0] == document_title:
            lines = lines[1:]

        content = "\n".join(lines)

        documents.append(
            {
                "source": file_path.name,
                "page_number": page_number,
                "content": content,
            }
        )

    return documents


def load_documents(data_dir: Path) -> list[dict]:
    """批量读取目录中的 Markdown、TXT 与 PDF 文档。"""
    documents = []

    for file_path in sorted(data_dir.iterdir()):
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()

        if suffix not in SUPPORTED_SUFFIXES:
            continue

        if suffix == ".pdf":
            documents.extend(load_pdf_document(file_path))
        else:
            documents.extend(load_text_document(file_path))

    return documents


if __name__ == "__main__":
    documents = load_documents(RAW_DATA_DIR)

    print(f"读取到 {len(documents)} 条文档记录\n")

    for document in documents:
        print(f"来源：{document['source']}")
        print(f"页码：{document['page_number']}")
        print(f"内容前 80 个字：{document['content'][:80]}")
        print("-" * 40)