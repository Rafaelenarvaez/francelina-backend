from typing import Any
from config.db import conn 
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import (
    OAuth2PasswordBearer, 
    SecurityScopes,
    )
from jose import jwt
from pydantic import ValidationError
from models.user import users


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"api/access-token",
)

async def get_current_user(
    token: str = Depends(reusable_oauth2)
):
    authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Error validando las credenciales.",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id = int(payload['sub'])
        if not user_id:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sesion expirada, inicie sesion nuevamente.",
        )

    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Error validando las credenciales.",
        )

    qr = users.select().where(users.c.id == user_id)
    user = conn.execute(qr).fetchone()
    if not user:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Any = Security(get_current_user)
) -> Any:
    return current_user
