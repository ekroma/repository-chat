from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    photo_url:str|None = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: str

    class Config:
        from_attributes = True