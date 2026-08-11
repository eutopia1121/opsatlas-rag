from fastapi import FastAPI
from pydantic import BaseModel, Field
from rag_chat import ask_knowledge_base
app = FastAPI(
    title="OpsAtlas API",
    version="0.1.0",
)

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