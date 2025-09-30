from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"