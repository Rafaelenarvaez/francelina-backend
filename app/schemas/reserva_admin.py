from lib2to3.pgen2.token import OP
from pydantic import BaseModel
from typing import Optional
from datetime import  time
class Reserva_admin(BaseModel):
    id:Optional[str]
    zona:str
    horas:time
    capacidad:int