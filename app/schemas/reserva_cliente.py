from lib2to3.pgen2.token import OP
from sqlite3 import Time
from pydantic import BaseModel
from typing import Optional, Union
from datetime import  time

class Reserva(BaseModel):
    id:Optional[str]  = None
    nombre:str
    apellido : str
    cedula:str
    email:str
    telefono:str
    hora: str
    zona:str
    fecha:str
    fecha_de_cumpleaños: str
    numero_de_personas: int
    nota: str
    