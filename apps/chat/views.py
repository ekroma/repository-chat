from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from fastapi import Depends, APIRouter, HTTPException
from typing import Annotated

from apps.user.auth import User
from apps.user.views import get_current_user
from config.db import get_async_session
from .schemas import ChatOut, ChatCreate
from .models import Chat, UserChat


chat_router = APIRouter()


@chat_router.post("/create_chat", description="вводить UUID юзера можно полyчить из /auth/users/")
async def create_chat(chat_data: ChatCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        chat = Chat()
        chat.name = chat_data.name
        chat.status = chat_data.status
        
        users = await db.execute(select(User).where(User.id.in_(chat_data.users)))
        users = users.scalars().all()
        
        chat.users = users
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        
        return chat
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))



@chat_router.get("/user_chats/{user_id}", response_model=list[ChatOut])
async def get_user_chats(
    user_id: str, db: AsyncSession = Depends(get_async_session)
):
    try:
        query = (
            select(Chat)
            .join(UserChat)
            .join(User)
            .filter(User.id == user_id)
            .options(selectinload(Chat.users))
        )
        
        result = await db.execute(query)

        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@chat_router.get("/my_chats/{status}")
async def get_my_chats(
    current_user: Annotated[User, Depends(get_current_user)],  
    db: AsyncSession = Depends(get_async_session),
):
    try:
        query = (
            select(Chat)
            .join(UserChat)
            .join(User)
            .filter(User.id == current_user.id)
            .options(selectinload(Chat.users))
        )

        result = await db.execute(query)
        chats = result.scalars().all()

        chat_partners = []

        for chat in chats:
            partner_users = [user for user in chat.users if user.id != current_user.id]
            chat_partners.append(
                {
                    "chat_id": chat.id,
                    "chat_name": chat.name,
                    "status": chat.status,
                    "partners": [
                        {"user_id": partner.id, "username": partner.username}
                        for partner in partner_users
                    ],
                }
            )

        return chat_partners
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@chat_router.get("/all_chats/{status}", response_model=list[ChatOut])
async def get_all_chats(
    db: AsyncSession = Depends(get_async_session),
):
    try:
        query = select(Chat).options(selectinload(Chat.users))

        result = await db.execute(query)

        return result.unique().scalars().all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))