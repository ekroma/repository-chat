from fastapi import Depends, APIRouter, Query
from .schemas import MessageCreate, MessageOutput
from repositories import MessageRepository, get_message_repository
from apps.user.auth import User, get_current_user

message_router = APIRouter()

@message_router.get("/messages", response_model=list[MessageOutput])
async def get_messages(
    sender_id: str = Query(None),
    time_delivered: str = Query(None),
    message_repository: MessageRepository = Depends(get_message_repository),
):
    messages_data = await message_repository.get_messages(sender_id, time_delivered)
    return messages_data

@message_router.post("/send_message", response_model=MessageOutput)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    message_repository: MessageRepository = Depends(get_message_repository),
):
    new_message = await message_repository.send_message(message_data, current_user.id)
    return new_message

@message_router.post("/get_chat_messages", response_model=list[MessageOutput])
async def get_messages_in_chat(
    chat_id: int = Query(description="Chat id"),
    message_repository: MessageRepository = Depends(get_message_repository),
):
    chat_messages = await message_repository.get_messages_in_chat(chat_id)
    return chat_messages
