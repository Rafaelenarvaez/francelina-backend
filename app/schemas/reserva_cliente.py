from lib2to3.pgen2.token import OP
from pydantic import BaseModel
from typing import Optional
class Reserva(BaseModel):
    id:Optional[str]
    nombre:str
    apellido : str
    cedula:str
    email:str
    telefono:str
    hora:str
    fecha:str
    fecha_de_cumpleaños: str
    numero_de_personas: int
    