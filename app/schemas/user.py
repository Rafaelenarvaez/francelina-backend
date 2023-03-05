from lib2to3.pgen2.token import OP
from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class User(BaseModel):
    id:Optional[str]
    name:str
    email:str
    password:str

class UserBaseRequired(BaseModel):
    name: str

class UserCreate(UserBaseRequired):
    email: EmailStr
    password: str
    password2: str

    @validator('password2')
    def password_match(cls, v, values, **kwargs):
        if v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v