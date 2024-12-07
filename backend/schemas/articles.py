from datetime import datetime

from pydantic import BaseModel


class ArticleBase(BaseModel):
    filename: str
    sourcepdf_url: str | None
    processeds3_url: str | None


class ArticleResponse(ArticleBase):
    a_id: str | None
