from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from rag_chat import ask_knowledge_base
from pathlib import Path
from ingest import ingest
from fastapi.staticfiles import StaticFiles
from logger_config import setup_logger


logger = setup_logger()
app = FastAPI(
    title="OpsAtlas API",
    version="0.1.0",
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

SUPPORTED_UPLOAD_SUFFIXES = {".md", ".txt", ".pdf"}
class AskRequest(BaseModel):
    """POST /ask 的请求体。"""
    question: str = Field(
        min_length=1,
        description="用户要询问的问题",
    )

class SourceItem(BaseModel):
    """单条引用来源。"""
    chunk_id: int
    source: str
    title: str
    page_number: int | None
    score: float

class AskResponse(BaseModel):
        """POST /ask 的响应体。"""
        answer: str
        sources: list[SourceItem]
class IngestResponse(BaseModel):
    """POST /ingest 的响应体。"""
    message: str
    document_count: int
    chunk_count: int
    record_count: int


class UploadResponse(BaseModel):
    """POST /upload 的响应体。"""
    message: str
    filename: str
    document_count: int
    chunk_count: int
    record_count: int
@app.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "opsatlas",
    }

@app.post("/ask", response_model=AskResponse)
@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest) -> AskResponse:
    """接收用户问题，执行完整 RAG 问答流程。"""
    try:
        answer, raw_sources = ask_knowledge_base(request.question)

        sources = []

        for raw_source in raw_sources:
            sources.append(
                SourceItem(
                    chunk_id=raw_source["chunk_id"],
                    source=raw_source["source"],
                    page_number=raw_source["page_number"],
                    title=raw_source["title"],
                    score=raw_source["score"],
                )
            )

        return AskResponse(
            answer=answer,
            sources=sources,
        )

    except Exception as error:
        logger.exception("知识库问答失败：%s", error)

        raise HTTPException(
            status_code=503,
            detail="问答服务暂时不可用，请稍后再试。",
        ) from error


@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
) -> UploadResponse:
    """上传一个知识文档，并重新执行入库。"""
    filename = Path(file.filename or "").name
    suffix = Path(filename).suffix.lower()

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="请选择要上传的文件。",
        )

    if suffix not in SUPPORTED_UPLOAD_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail="仅支持 .md、.txt、.pdf 文件。",
        )

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    save_path = RAW_DATA_DIR / filename
    file_content = await file.read()
    save_path.write_bytes(file_content)

    logger.info("收到上传文件：%s", filename)

    try:
        summary = ingest()

        logger.info(
            "上传文件入库完成：%s，Chunk 数量：%s",
            filename,
            summary["chunk_count"],
        )

        return UploadResponse(
            message="文件上传并入库完成",
            filename=filename,
            document_count=summary["document_count"],
            chunk_count=summary["chunk_count"],
            record_count=summary["record_count"],
        )

    except Exception as error:
        logger.exception("上传文件入库失败：%s", error)

        raise HTTPException(
            status_code=503,
            detail="文件已上传，但知识库入库暂时失败，请稍后重试。",
        ) from error


@app.post("/ingest", response_model=IngestResponse)
def ingest_knowledge_base() -> IngestResponse:
    """重新处理 data/raw 中的文档并写入 Milvus。"""
    summary = ingest()

    return IngestResponse(
        message="知识库入库完成",
        document_count=summary["document_count"],
        chunk_count=summary["chunk_count"],
        record_count=summary["record_count"],
    )

app.mount(
    "/",
    StaticFiles(directory=STATIC_DIR, html=True),
    name="static",
)