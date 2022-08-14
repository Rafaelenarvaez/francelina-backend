from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from models.user import users
from schemas.user import User 
from config.db import conn
from cryptography.fernet import Fernet  
from models.user import users
from schemas.user import User 
from cryptography.fernet import Fernet 

key =Fernet.generate_key()
f=Fernet(key)


auth_routes = APIRouter()


@auth_routes.post("/admin")
def admin(admin:User, id:str):
    print(admin.dict())
    return "success"

@auth_routes.get("/Admin/{id}")
def Admin(id: str):
    print(id)
    return

