from typing import List

from fastapi import APIRouter, status, HTTPException, Depends

from backend.schemas.articles import (
    ArticleResponse,
)
from backend.services.articles import _get_article, _get_all_articles
from backend.services.auth_bearer import security_scheme

articles_router = APIRouter(prefix="/articles", tags=["articles"])


@articles_router.get(
    "/",
    response_model=List[ArticleResponse],
)
async def get_all_articles(
    # token: str = Depends(security_scheme),
) -> List[ArticleResponse]:
    articles = await _get_all_articles()
    return articles


@articles_router.get(
    "/{article_id}",
    response_model=ArticleResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": None}},
)
async def get_article( article_id: str,
                      token: str = Depends(security_scheme)
                      ) -> ArticleResponse:
    if article := await _get_article(article_id=article_id):
        return article
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Article with id {article_id} not found",
    )
