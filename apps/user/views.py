from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from .schemas import UserCreate, UserRead
from repositories import UserRepository, get_user_repository

user_routes = APIRouter()


@user_routes.post("/register", response_model=UserRead)
async def register(user: UserCreate, user_repository: UserRepository = Depends(get_user_repository)):
    existing_user = await user_repository.get_user_by_username(user.username)
    
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Username already in use")

    try:
        new_user = await user_repository.create_user(user)
        return new_user
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username already in use")


@user_routes.get("/users/", response_model=list[UserRead])
async def get_users(user_repository: UserRepository = Depends(get_user_repository)):
    users = await user_repository.get_users()
    return users


@user_routes.get("/user/", response_model=UserRead)
async def get_user(
        username: Annotated[str|None, Query(description="username to search")] = None,
        uuid: Annotated[str|None, Query(description="UUID to search")] = None,
        user_repository: UserRepository = Depends(get_user_repository)):

    if uuid:
        user = await user_repository.get_user_by_id(uuid)
    elif username:
        user = await user_repository.get_user_by_username(username)
    else:
        raise HTTPException(status_code=400, detail="Username or UUID to delete")

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@user_routes.delete("/user/")
async def delete_user(
        username: Annotated[str|None, Query(description="username to search")] = None,
        uuid: Annotated[str|None, Query(description="UUID to search")] = None,
        user_repository: UserRepository = Depends(get_user_repository),
        ):

    if uuid:
        user = await user_repository.get_user_by_id(uuid)
    elif username:
        user = await user_repository.get_user_by_username(username)
    else:
        raise HTTPException(status_code=400, detail="Username or UUID to delete")

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    await user_repository.delete_user(user.id)
    return {"message": "User deleted successfully"}


@user_routes.post("/jwt/login")
async def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_repository: UserRepository = Depends(get_user_repository)
        ):

    response = await user_repository.login_user(form_data)

    return response