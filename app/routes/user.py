from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import timedelta
from config.db import conn 
from models.user import users
from schemas.user import User, UserCreate
from cryptography.fernet import Fernet 

from datetime import timedelta, datetime
from typing import Union, Any, List

from jose import jwt
from passlib.context import CryptContext


key =Fernet.generate_key()
f=Fernet(key)

user = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

def create_access_token(
    subject: Union[str, Any], 
    expires_delta: timedelta = None,
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=60
        )
    to_encode = {
        "exp": expire, 
        "sub": str(subject), 
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



@user.get("/user")
def get_user():
        qr = users.select().where(users.c.id )
        return conn.execute(users.select()).fetchall()

@user.post("/user")
def create_user(user:User):
        new_user={"name": user.name, "email":user.email}
        new_user["password"]= f.encrypt(user.password.encode("utf-8"))
        result = conn.execute(users.insert().values(new_user))
        return 


@user.post(
    "/register"
)
async def create_user( 
    *,
    user_in: UserCreate,
):
    
    qr = users.select().where(users.c.email == user_in.email)
    user = conn.execute(qr).fetchone()

    if user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content={
                'msg': f"El correo '{user_in.email}' ya está siendo utilizado", 
            })
    new_user = conn.execute(users.insert().values(user_in.dict(exclude={'password2'}))).inserted_primary_key[0]
   
    if new_user:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, 
            content={
                'msg': f"Usuario creado exitosamente! Autenticar para ingresar", 
            })
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content={
                'msg': f"El servicio no está disponible actualmente. Intente mas tarde", 
            })


@user.post(
    "/access-token"
)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    
    qr = users.select().where(
        users.c.email == form_data.username, 
        users.c.password == form_data.password
    )
    user = conn.execute(qr).fetchone()
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content={
                'msg': 'Email o contraseña incorrectos', 
            })

    access_token_expires = timedelta(minutes=60)
    return {
        "access_token": create_access_token(
            user['id'], expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user_id": user['id'],
        'username': user['name'],
        "ttl": access_token_expires
    }