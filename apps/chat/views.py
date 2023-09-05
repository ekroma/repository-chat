from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from apps.user.auth import User, get_current_user
from repositories import ChatRepository, get_chat_repository
from .schemas import ChatOut, ChatCreate
from .models import Chat, UserChat

chat_router = APIRouter()

@chat_router.post("/create_chat", description="вводить UUID юзера можно полyчить из /auth/users/")
async def create_chat(
    chat_data: ChatCreate, 
    chat_repository: ChatRepository = Depends(get_chat_repository)
):
    chat = await chat_repository.create_chat(chat_data)
    return chat

@chat_router.get("/user_chats/{user_id}", response_model=list[ChatOut])
async def get_user_chats(
    user_id: str, 
    chat_repository: ChatRepository = Depends(get_chat_repository)
):
    try:
        query = (
            select(Chat)
            .join(UserChat)
            .join(User)
            .filter(User.id == user_id)
            .options(selectinload(Chat.users))
        )
        
        result = await chat_repository.db.execute(query)

        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@chat_router.get("/my_chats/{status}")
async def get_my_chats(
    current_user: User = Depends(get_current_user),  
    chat_repository: ChatRepository = Depends(get_chat_repository),
):
    try:
        query = (
            select(Chat)
            .join(UserChat)
            .join(User)
            .filter(User.id == current_user.id)
            .options(selectinload(Chat.users))
        )

        result = await chat_repository.db.execute(query)
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
    chat_repository: ChatRepository = Depends(get_chat_repository),
):
    try:
        query = select(Chat).options(selectinload(Chat.users))

        result = await chat_repository.db.execute(query)

        return result.unique().scalars().all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
