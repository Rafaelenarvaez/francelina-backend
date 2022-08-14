from email.mime import image
from hashlib import new
import imp
import random
from os import getcwd
from turtle import update
from fastapi import APIRouter, Depends, Security, UploadFile, File, Form
from pydantic import FilePath

from models.user import platillos
from config.db import conn 
from models.user import galeria
from schemas.menu import Menu


ide = []
create_menu = APIRouter()

@create_menu.post("/menu")
async def create(
    id:str = Form(...),
    nombre: str = Form(...),
    precio: str = Form(...),
    descripcion: str = Form(...),
    file:UploadFile=File(...)
    ):
    
    FILEPATH= "./imagenes/menu/"
    filename=file.filename
    extencion = filename.split(".")[1]

    if extencion not in ["png","jpg"]:
        return {"status": "error" , "detail": "Extencion no permitida"}

    ide = random.randint(1,100)

    id= str(ide) + "." + extencion
    generated_name = FILEPATH + id
    file_content = await file.read()

    new_menu={"nombre": nombre, "precio": precio,"descripcion": descripcion, "imagen":generated_name, "categoria_id": 1}

    rp = conn.execute(platillos.insert().values(new_menu))
    print(rp)

    with open (generated_name, "wb") as file:
        file.write(file_content)
    
    return print("success")


@create_menu.post("/uploadfile/galeria")
async def uploadfile_post(file:UploadFile=File(...)):

    FILEPATH= "./imagenes/"
    filename=file.filename
    extencion = filename.split(".")[1]

    if extencion not in ["png","jpg"]:
        return {"status": "error" , "detail": "Extencion no permitida"}

    ide = random.randint(1,100)
    id= str(ide) + "." + extencion
    generated_name = FILEPATH + id
    file_content = await file.read()

    new_foto={"ruta":generated_name}
    conn.execute(galeria.insert().values(new_foto))


    with open (generated_name, "wb") as file:
        file.write(file_content)
    return"success"


@create_menu.get("/get_img")
def get_user():
        return conn.execute(galeria.select()).fetchall()


@create_menu.put("/admin/update_menu")
async def update_menu(
    nombre: str = Form(...),
    precio: str = Form(...),
    descripcion: str = Form(...),
    file:UploadFile=File(...)
    ):
    FILEPATH= "./imagenes/menu/"
    filename=file.filename
    extencion = filename.split(".")[1]

    if extencion not in ["png","jpg"]:
        return {"status": "error" , "detail": "Extencion no permitida"}

    ide = random.randint(1,100)

    id= str(ide) + "." + extencion
    generated_name = FILEPATH + id
    file_content = await file.read()

    new_menu={
    "nombre": nombre, 
    "precio": precio,
    "descripcion": descripcion, 
    "imagen":generated_name, 
    "categoria_id": id
    }

    rp = conn.execute(platillos.update().values(new_menu).where(platillos.c.nombre == nombre))
    print(rp)

    with open (generated_name, "wb") as file:
        file.write(file_content)
    
    return print("success")