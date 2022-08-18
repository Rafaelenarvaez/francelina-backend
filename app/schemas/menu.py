from lib2to3.pgen2.token import OP
from pydantic import BaseModel
from typing import Optional

class Menu(BaseModel):
    nombre:str
    descripcion:str
    
    
    