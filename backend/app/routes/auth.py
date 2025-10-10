from fastapi import APIRouter, HTTPException, Depends
from tortoise.exceptions import IntegrityError, DoesNotExist

from ..models import User
from ..schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from ..utils.auth import verify_password, hash_password, create_access_token, get_current_user


router = APIRouter()


@router.post("/register", response_model=UserOut)
async def register(payload: RegisterRequest):
    try:
        # Debug: Print password info before hashing
        print(f"DEBUG: Original password: '{payload.password}', length: {len(payload.password)}")
        print(f"DEBUG: Password bytes length: {len(payload.password.encode('utf-8'))}")
        
        hashed_password = hash_password(payload.password)
        print(f"DEBUG: Password hashed successfully")
        
        user = await User.create(username=payload.username, password_hash=hashed_password)
        return UserOut(id=user.id, username=user.username)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="用户名已存在")
    except Exception as e:
        print(f"DEBUG: Error during registration: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


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