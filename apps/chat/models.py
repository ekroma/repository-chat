from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey,SmallInteger , Integer, String, DateTime
from datetime import datetime
import uuid

from config.db import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(SmallInteger, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    users = relationship("User", secondary="userchats", back_populates="chats")
    messages = relationship("Message", back_populates="chat")


class UserChat(Base):
    __tablename__ = "userchats"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey('chats.id'))
    user_id = Column(String(36), ForeignKey('users.id'), default=str(uuid.uuid4()))