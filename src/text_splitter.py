import re
"""1. 封装两套标题识别函数，分别匹配Markdown二级标题与中文序号式TXT标题，用来识别文本章节分隔标记。
2. 实现通用按标题分割文档的底层函数，再封装md、txt专用分割方法，自动按章节拆分文档生成带来源、章节名的文本块。
3. 批量分割函数自动区分文件类型处理全部文档，为每个文本块生成全局唯一编号，直接运行脚本可加载本地文档并打印所有分块预览信息。"""

def get_markdown_heading(line: str) -> str | None:
    """如果一行是 Markdown 二级标题，返回标题文字；否则返回 None。"""
    if line.startswith("## "):
        return line[3:].strip()

    return None


def get_text_heading(line: str) -> str | None:
    """如果一行是“一、标题”形式的文本标题，返回标题文字。"""
    if re.match(r"^[一二三四五六七八九十]+、", line):
        return line.strip()

    return None

def split_document_by_heading(document: dict, heading_getter) -> list[dict]:
    """按指定的标题识别规则，把一份文档切成多个 Chunk。"""
    source = document["source"]
    current_title = source.rsplit(".", maxsplit=1)[0]
    current_lines = []
    chunks = []

    for line in document["content"].splitlines():
        heading = heading_getter(line)

        if heading is not None:
            if current_lines:
                chunks.append(
                    {
                        "source": source,
                        "title": current_title,
                        "content": "\n".join(current_lines).strip(),
                    }
                )

            current_title = heading
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        chunks.append(
            {
                "source": source,
                "title": current_title,
                "content": "\n".join(current_lines).strip(),
            }
        )

    return chunks


def split_markdown_document(document: dict) -> list[dict]:
    return split_document_by_heading(document, get_markdown_heading)


def split_text_document(document: dict) -> list[dict]:
    return split_document_by_heading(document, get_text_heading)


def split_documents(documents: list[dict]) -> list[dict]:
    """批量切分全部支持的文档，并给每个 Chunk 分配唯一编号。"""
    all_chunks = []

    for document in documents:
        source = document["source"]

        if source.endswith(".md"):
            document_chunks = split_markdown_document(document)
        elif source.endswith(".txt"):
            document_chunks = split_text_document(document)
        else:
            continue

        for chunk in document_chunks:
            chunk["chunk_id"] = len(all_chunks) + 1
            all_chunks.append(chunk)

    return all_chunks

if __name__ == "__main__":
    from document_loader import RAW_DATA_DIR, load_documents

    documents = load_documents(RAW_DATA_DIR)
    chunks = split_documents(documents)

    print(f"共读取 {len(documents)} 份文档")
    print(f"共切出 {len(chunks)} 个 Chunk\n")

    for chunk in chunks:
        print(f"Chunk {chunk['chunk_id']}：{chunk['title']}")
        print(f"来源：{chunk['source']}")
        print(f"正文前 80 个字：{chunk['content'][:80]}")
        print("-" * 40)