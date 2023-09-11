from pydantic import BaseModel
from typing import Optional
from datetime import  time
from pydantic import BaseModel, EmailStr, validator


class Events(BaseModel):
    id: Optional[str]
    title: Optional[str]
    description: Optional[str]
    fecha: Optional[str]
    hour: Optional[time]
    zone: Optional[str]
    

class EventsBase(BaseModel):
    title: str
    description: str
    fecha: str
    hour: time
    zone: str