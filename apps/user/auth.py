from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, select
from fastapi import HTTPException, Depends
from typing import Annotated
from jose import jwt, JWTError
import uuid

from config.db import get_async_session, Base





SECRET = "SECRET"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/jwt/login")

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    photo_url = Column(String(), nullable=True)
    password = Column(String, nullable=False)
    messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    chats = relationship("Chat", secondary="userchats", back_populates="users")



async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_async_session)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username = payload.get("username")

        user = await db.execute(select(User).where(User.username == username))
        user = user.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
