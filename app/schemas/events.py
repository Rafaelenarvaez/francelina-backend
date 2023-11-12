from pydantic import BaseModel
from typing import Optional
from datetime import  time
from pydantic import BaseModel, EmailStr, validator


class Events(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    fecha: Optional[str] = None
    hour: Optional[time] = None
    zone: Optional[str] = None
    

class EventsBase(BaseModel):
    title: str
    description: str
    fecha: str
    hour: time
    zone: str