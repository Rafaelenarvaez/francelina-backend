from lib2to3.pgen2.token import OP
from pydantic import BaseModel
from typing import Optional
class User(BaseModel):
    id:Optional[str]
    name:str
    email:str
    password:str

