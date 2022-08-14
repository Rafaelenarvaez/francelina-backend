from lib2to3.pgen2.token import OP
from pydantic import BaseModel
from typing import Optional
class Reserva(BaseModel):
    id:Optional[str]
    nombre:str
    email:str
    telefono:str
    hora:str
    fecha:str