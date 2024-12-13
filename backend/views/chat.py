from fastapi import APIRouter

from backend.schemas.chat import QARequest
from backend.services.chat import (
    process_qa_query,
)

chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post(
    "/{article_id}/qa",
)
async def question_answer(
    article_id: str, request: QARequest,
        # user_id: int = Depends(get_current_user_id)
):
    """
    Process a Q/A query for a specific article using multi-modal RAG
    """
    return await process_qa_query(
            article_id, request.question, request.model, 1
        )
