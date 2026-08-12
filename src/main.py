from fastapi import FastAPI
from pydantic import BaseModel, Field
from rag_chat import ask_knowledge_base
from pathlib import Path
from ingest import ingest
from fastapi.staticfiles import StaticFiles
app = FastAPI(
    title="OpsAtlas API",
    version="0.1.0",
)

STATIC_DIR = Path(__file__).resolve().parent / "static"

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
@app.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "opsatlas",
    }

@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest) -> AskResponse:
    """接收用户问题，执行完整 RAG 问答流程。"""
    answer, raw_sources = ask_knowledge_base(request.question)

    sources = []

    for raw_source in raw_sources:
        sources.append(
            SourceItem(
                chunk_id=raw_source["chunk_id"],
                source=raw_source["source"],
                title=raw_source["title"],
                score=raw_source["score"],
            )
        )

    return AskResponse(
        answer=answer,
        sources=sources,
    )

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