from pydantic import BaseModel
from datetime import datetime


class MessageBase(BaseModel):
    text: str


class MessageCreate(MessageBase):
    chat_id: int


class MessageOutput(MessageBase):
    id: int
    receiver_id: str|None = None
    time_delivered: datetime|None = None
    chat_id: int
    text: str

    class ConfigDict:
        from_attributes = True

