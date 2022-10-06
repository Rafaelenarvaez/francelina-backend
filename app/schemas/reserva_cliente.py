from lib2to3.pgen2.token import OP
from sqlite3 import Time
from pydantic import BaseModel
from typing import Optional
from datetime import  time

class Reserva(BaseModel):
    id:Optional[str]
    nombre:str
    apellido : str
    cedula:str
    email:str
    telefono:str
    hora: time 
    zona:str
    fecha:str
    fecha_de_cumpleaños: str
    numero_de_personas: int
    