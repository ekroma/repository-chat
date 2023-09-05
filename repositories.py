from datetime import datetime
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi import HTTPException, Depends
from jose import jwt
import bcrypt
from apps.chat.models import Chat, UserChat
from apps.chat.schemas import ChatCreate
from apps.message.models import Message
from apps.message.schemas import MessageCreate

from apps.user.schemas import UserCreate, UserRead
from apps.user.auth import User, ALGORITHM, SECRET
from config.db import get_async_session



class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: UserCreate) -> UserRead:
        try:
            hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

            user_db = User(
                username=user.username,
                password=hashed_password.decode('utf-8'),
                photo_url=user.photo_url,
            )

            self.db.add(user_db)
            await self.db.commit()
            await self.db.refresh(user_db)

            return UserRead.from_orm(user_db)
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Username already in use")

    async def login_user(self, form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
        db_user = await self.get_user_by_username(form_data.username)

        if db_user is None or not bcrypt.checkpw(form_data.password.encode('utf-8'), db_user.password.encode('utf-8')):
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        
        user_dict = {
        "sub": str(db_user.id),
        "username": db_user.username,
        }

        access_token = jwt.encode(user_dict, SECRET, algorithm=ALGORITHM)

        return {"access_token": access_token, "token_type": "bearer"}


    async def get_users(self) -> list[dict]:
        query = select(User).options(selectinload(User.messages))
        result = await self.db.execute(query)
        users = result.scalars().all()
        return users

    async def get_user_by_id(self, user_id: str):
        query = select(User).where(User.id == user_id).options(selectinload(User.messages))
        result = await self.db.execute(query)
        user = result.scalars().one_or_none()
        return user

    async def get_user_by_username(self, username: str):
        query = select(User).where(User.username == username).options(selectinload(User.messages))
        result = await self.db.execute(query)
        user = result.scalars().one_or_none()
        return user

    async def delete_user(self, user_id: str):
        user = await self.get_user_by_id(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()

    async def update_user(self, user_id: str, user_update: UserCreate) -> UserRead|None:
        user = await self.get_user_by_id(user_id)
        if user:
            user.username = user_update.username
            user.password = user_update.password
            user.photo_url = user_update.photo_url
            async with self.db.begin():
                await self.db.commit()
                await self.db.refresh(user)
            return UserRead.from_orm(user)
        return None



class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self, chat_data: ChatCreate):
        try:
            chat = Chat()
            chat.name = chat_data.name
            chat.status = chat_data.status
            
            users = await self.db.execute(select(User).where(User.id.in_(chat_data.users)))
            users = users.scalars().all()
            
            chat.users = users
            self.db.add(chat)
            await self.db.commit()
            await self.db.refresh(chat)
            
            return chat
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))


    async def get_user_chats(self, user_id: str):
        query = (
            select(Chat)
            .join(UserChat)
            .join(User)
            .filter(User.id == user_id)
            .options(selectinload(Chat.users))
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_my_chats(self, current_user: User):
        query = (
            select(Chat)
            .join(UserChat)
            .join(User)
            .filter(User.id == current_user.id)
            .options(selectinload(Chat.users))
        )
        result = await self.db.execute(query)
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

    async def get_all_chats(self):
        query = select(Chat).options(selectinload(Chat.users))
        result = await self.db.execute(query)
        return result.unique().scalars().all()


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_messages(
        self, sender_id: str = None, time_delivered: datetime = None
    ):
        try:
            query = select(Message)

            if sender_id:
                query = query.where(Message.sender_id == sender_id)
            if time_delivered:
                query = query.where(Message.time_delivered == time_delivered)

            messages = await self.db.execute(query)
            messages_data = messages.scalars().all()

            return messages_data
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def send_message(
        self, message_data: MessageCreate, current_user_id: str
    ):
        try:
            new_message = Message(
                text=message_data.text,
                sender_id=current_user_id,
                chat_id=message_data.chat_id,
            )

            self.db.add(new_message)
            await self.db.commit()
            await self.db.refresh(new_message)

            return new_message
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get_messages_in_chat(
        self, chat_id: int
    ):
        try:
            query = select(Message).where(Message.chat_id == chat_id)
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


async def get_message_repository(db: AsyncSession = Depends(get_async_session)):
    async with db:
        yield MessageRepository(db)

async def get_user_repository(db: AsyncSession = Depends(get_async_session)):
    async with db:
        yield UserRepository(db)

async def get_chat_repository(db: AsyncSession = Depends(get_async_session)):
    async with db:
        yield ChatRepository(db)

