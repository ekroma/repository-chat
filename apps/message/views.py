from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, APIRouter, HTTPException, Query

from apps.user.views import get_current_user
from apps.user.auth import User
from config.db import get_async_session
from .schemas import MessageCreate, MessageOutput
from .models import Message

message_router = APIRouter()


@message_router.get("/messages", response_model=list[MessageOutput])
async def get_messages(
    sender_id: str = Query(None),
    receiver_id: str = Query(None),
    time_delivered: str = Query(None),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        async with db.begin():
            query = select(Message)

            if sender_id:
                query = query.where(Message.sender_id == sender_id)
            if receiver_id:
                query = query.where(Message.receiver_id == receiver_id)
            if time_delivered:
                query = query.where(Message.time_delivered == time_delivered)

            messages = await db.execute(query)
            messages_data = messages.scalars().all()

            messages_data = [
                MessageOutput(
                    id=message.id,
                    sender_id=message.sender_id,
                    receiver_id=message.receiver_id,
                    time_delivered=message.time_delivered,
                    text=message.text,
                )
                for message in messages_data
            ]

            return messages_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@message_router.post("/send_message", response_model=MessageOutput)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        new_message = Message(
            text=message_data.text,  
            sender_id=current_user.id,
            chat_id=message_data.chat_id
        )
        
        db.add(new_message)
        await db.commit()
        await db.refresh(new_message)

        return new_message
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@message_router.post("/get_chat_messages", response_model=list[MessageOutput])
async def get_messages_in_chat(
    chat_id: int = Query(description="Chat id"),
    db: AsyncSession = Depends(get_async_session),
):
    async with db.begin():
        query = select(Message).where(Message.chat_id == chat_id)
        result = await db.execute(query)
        return result.scalars().all()