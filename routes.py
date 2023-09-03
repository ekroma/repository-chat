from fastapi import APIRouter

from apps.user.views import user_routes
from apps.chat.views import chat_router
from apps.message.views import message_router

routes = APIRouter()


routes.include_router(user_routes, prefix="/auth", tags=["users"])
routes.include_router(chat_router, prefix="/chat", tags=["chats"])
routes.include_router(message_router, prefix="/messages", tags=["messages"])