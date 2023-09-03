from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from fastapi import Depends, APIRouter, Query, HTTPException
from typing import Annotated
from jose import JWTError, jwt
import bcrypt
import uuid

from apps.user.auth import User
from config.db import get_async_session
from .schemas import UserCreate, UserRead
from .auth import SECRET, ALGORITHM

user_routes = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/jwt/login")


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


async def get_user_by_username(username: str, db: AsyncSession):
    async with db.begin():
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalars().one_or_none()


@user_routes.post("/jwt/login")
async def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_session)):

    db_user = await get_user_by_username(form_data.username, db)
    if db_user is None or not bcrypt.checkpw(form_data.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    user_dict = {
        "sub": str(db_user.id),
        "username": db_user.username,
    }

    access_token = jwt.encode(user_dict, SECRET, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}


@user_routes.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    existing_user = await get_user_by_username(user.username, db)
    
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Username already in use")

    try:
        user_id = str(uuid.uuid4())

        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

        user = User(
            id=user_id,  
            username=user.username,
            password=hashed_password.decode('utf-8'),
            photo_url=user.photo_url
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@user_routes.get("/users/",)
async def get_users(db: AsyncSession = Depends(get_async_session)):
    results = await db.execute(select(User))
    users = results.scalars().all()
    return {"users": users}


@user_routes.get("/user/",)
async def get_user(
        identifier: str = Query(description="UUID or username to search"),
        db: AsyncSession = Depends(get_async_session)):

    is_uuid = False
    try:
        uuid.UUID(identifier)
        is_uuid = True
    except ValueError:
        pass

    if is_uuid:
        result = await db.execute(select(User).where(User.id == identifier))
    else:
        result = await db.execute(select(User).where(User.username == identifier))

    user = result.scalars().one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@user_routes.delete("/user/")
async def delete_user(
        identifier: str = Query(description="UUID or username to delete"),
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)):  

    is_uuid = False
    try:
        uuid.UUID(identifier)
        is_uuid = True
    except ValueError:
        pass

    if is_uuid:
        result = await db.execute(select(User).where(User.id == identifier))
    else:
        result = await db.execute(select(User).where(User.username == identifier))

    user = result.scalars().one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")


    await db.delete(user) 
    await db.commit()  
    return {"message": "User deleted successfully"}