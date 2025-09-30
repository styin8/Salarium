from fastapi import APIRouter, HTTPException, Depends
from tortoise.exceptions import IntegrityError, DoesNotExist

from ..models import User
from ..schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from ..utils.auth import verify_password, hash_password, create_access_token, get_current_user


router = APIRouter()


@router.post("/register", response_model=UserOut)
async def register(payload: RegisterRequest):
    try:
        user = await User.create(username=payload.username, password_hash=hash_password(payload.password))
        return UserOut(id=user.id, username=user.username)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="用户名已存在")


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    try:
        user = await User.get(username=payload.username)
    except DoesNotExist:
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(user=Depends(get_current_user)):
    return UserOut(id=user.id, username=user.username)