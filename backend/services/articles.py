import logging
from typing import Optional, List

from sqlalchemy import select

from backend.database import db_session
from backend.database.articles import ArticleModel

logger = logging.getLogger(__name__)


async def _get_article(article_id: str) -> Optional[ArticleModel]:
    try:
        with db_session() as session:
            stmt = select(ArticleModel).where(ArticleModel.a_id == article_id)
            result = session.execute(stmt)
            article = result.scalar_one_or_none()
            if article:
                session.refresh(article)
            return article
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {str(e)}", exc_info=True)
        return None


async def _get_all_articles() -> List[ArticleModel]:
    try:
        with db_session() as session:
            stmt = select(ArticleModel)
            result = session.execute(stmt)
            articles = result.scalars().all()
            return list(articles)
    except Exception as e:
        logger.error(f"Error fetching all articles: {str(e)}", exc_info=True)
        return []


