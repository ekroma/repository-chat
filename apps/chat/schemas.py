from pydantic import BaseModel

from apps.user.schemas import UserRead

class ChatBase(BaseModel):
    name: str


class ChatCreate(ChatBase):
    status: int
    users: list[str]
    

class ChatOut(ChatBase):
    id:int
    status:int
    users: list[UserRead]

    class Config:
        from_attributes = True