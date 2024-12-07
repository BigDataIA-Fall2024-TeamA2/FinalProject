from fastapi import APIRouter

from backend.views.articles import articles_router
from backend.views.auth import auth_router
from backend.views.chat import chat_router
from backend.views.users import users_router

central_router = APIRouter()

central_router.include_router(articles_router)
central_router.include_router(auth_router)
central_router.include_router(chat_router)
central_router.include_router(users_router)
