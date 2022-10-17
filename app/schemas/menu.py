from pydantic import BaseModel

class Menu(BaseModel):
    nombre:str
    descripcion: str
    
    
    