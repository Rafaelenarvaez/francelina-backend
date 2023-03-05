from ast import Try
from asyncio import exceptions
from logging import exception
from jwt import encode, decode
from datetime import datetime, timedelta
from os import getenv
from fastapi.responses import JSONResponse

from typing import Any

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import (
    OAuth2PasswordBearer, 
    SecurityScopes,
    )
from jose import jwt
from pydantic import ValidationError

def expire_data(days: int):
    date = datetime.now()
    new_date= date+timedelta(days)
    return new_date


def write_token(data:dict):
    token=encode(payload={**data, "exp": expire_data(2) }, key=getenv("SECRET"), algorithm="HS256")
    return token 

def validate_toke (token, output=False):

    try:
        if output:
            decode(token, key=getenv("SECRET"), algorithms= ["HS256"])
        decode(token, key=getenv("SECRET"), algorithms= ["HS256"])
    except exceptions.DecodeError:
        return JSONResponse (content={"message": "Invalid token"}, status_code= 401)
    except exceptions.ExpiredSingtureError:
        return JSONResponse (content={"message": "Token Expired"}, status_code= 401)    


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"localhost:8000/login/access-token",
    scopes={
        "me": "Read information about the current user.", 
        "cashier_admin": "Only make orders.",
        "franchise_admin": "Products and categories CRUD and Cashier permissions.",
        "general_admin": "Cashiers CRUD and Franchise permisions."}
)

async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(reusable_oauth2)
) -> Any:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Error validando las credenciales.",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = token_sch.TokenPayload(**payload)
        user_id = int(token_data.sub)
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
    user = await crud_user.user.get(id=user_id)
    if not user:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Permisos insuficientes.",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: user_sch.UserSch = Security(get_current_user, scopes=["me"])
) -> user_sch.UserSch:
    if not await crud_user.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
