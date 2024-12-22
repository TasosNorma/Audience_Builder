from datetime import datetime, timedelta
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from source.core.config import settings
from jose import jwt

# Generate Password Hash
def get_password_hash(password: str) -> str:
    return generate_password_hash(password, method=settings.HASH_METHOD)

# Verify password against hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return check_password_hash(hashed_password, plain_password)

#Create access token
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt