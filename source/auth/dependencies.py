from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from source.database.database import get_db
from sqlalchemy.orm import Session
from source.database.models import User
from source.core.config import settings
from jose import JWTError, jwt


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms = [settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise credentials_exception
        
    return user