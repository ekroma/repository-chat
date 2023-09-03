from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from datetime import datetime

from config.db import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    is_delivered = Column(Boolean, default=True)
    time_delivered = Column(DateTime, default=datetime.utcnow)
    
    chat_id = Column(Integer, ForeignKey('chats.id'))
    sender_id = Column(String(36), ForeignKey('users.id'))
    receiver_id = Column(String(36), ForeignKey('users.id'), nullable=True)

    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="messages")