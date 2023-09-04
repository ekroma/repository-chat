from sqlalchemy.orm import relationship
from sqlalchemy import Column, String
import uuid

from config.db import Base


SECRET = "SECRET"
ALGORITHM = "HS256"


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    photo_url = Column(String(), nullable=True)
    password = Column(String, nullable=False)
    messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    chats = relationship("Chat", secondary="userchats", back_populates="users")


