import imp
from fastapi import APIRouter
from config.db import conn 
from models.user import users
from schemas.user import User 
from cryptography.fernet import Fernet 

key =Fernet.generate_key()
f=Fernet(key)

user = APIRouter()

@user.get("/user")
def get_user():
        qr = users.select().where(users.c.id )
        return conn.execute(users.select()).fetchall()

@user.post("/user")
def create_user(user:User):
        new_user={"name": user.name, "email":user.email}
        new_user["password"]= f.encrypt(user.password.encode("utf-8"))
        result = conn.execute(users.insert().values(new_user))
        print (result)
        return 