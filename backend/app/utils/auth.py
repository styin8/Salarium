from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from tortoise.exceptions import DoesNotExist

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from ..models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Note: We apply the same truncation logic as in hash_password
    to ensure consistency during verification.
    """
    # Apply the same truncation logic as in hash_password
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        truncated_bytes = password_bytes[:72]
        try:
            plain_password = truncated_bytes.decode('utf-8')
        except UnicodeDecodeError:
            for i in range(71, 0, -1):
                try:
                    plain_password = password_bytes[:i].decode('utf-8')
                    break
                except UnicodeDecodeError:
                    continue
    
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Note: bcrypt has a maximum password length of 72 bytes. 
    We truncate the password to ensure it doesn't exceed this limit
    while preserving UTF-8 encoding integrity.
    """
    try:
        # Truncate password to 72 bytes to comply with bcrypt limitations
        # Use encode/decode to ensure we don't break UTF-8 character boundaries
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            # Find the last valid UTF-8 character boundary within 72 bytes
            truncated_bytes = password_bytes[:72]
            # Decode and re-encode to ensure we don't have partial UTF-8 characters
            try:
                password = truncated_bytes.decode('utf-8')
            except UnicodeDecodeError:
                # If we cut in the middle of a UTF-8 character, find the last valid boundary
                for i in range(71, 0, -1):
                    try:
                        password = password_bytes[:i].decode('utf-8')
                        break
                    except UnicodeDecodeError:
                        continue
        
        # Ensure password is still within bcrypt limits after processing
        final_password_bytes = password.encode('utf-8')
        if len(final_password_bytes) > 72:
            # If still too long, use a simple byte truncation
            password = password[:72]
        
        return pwd_context.hash(password)
    except Exception as e:
        print(f"DEBUG: Error in hash_password: {type(e).__name__}: {str(e)}")
        # Fallback: simple truncation
        if len(password) > 72:
            password = password[:72]
        return pwd_context.hash(password)


def create_access_token(subject: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode = {"exp": expire, **subject}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user = await User.get(username=username)
        return user
    except DoesNotExist:
        raise credentials_exception