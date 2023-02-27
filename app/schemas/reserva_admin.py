from lib2to3.pgen2.token import OP
from pydantic import BaseModel
from typing import Optional
from datetime import  time
class Reserva_admin(BaseModel):
    id:Optional[str]
    hora1:time
    hora2:time
    nombre: str
   