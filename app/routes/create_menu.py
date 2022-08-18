from email.mime import image
from hashlib import new
import imp
import random
from os import getcwd
from turtle import update
from fastapi import APIRouter, Depends, Security, UploadFile, File, Form, status
from pydantic import FilePath
from fastapi.responses import JSONResponse
from models.user import menu1
from models.user import platillos
from config.db import conn 
from models.user import galeria
from schemas.menu import Menu


ide = []
create_menu = APIRouter()

@create_menu.post("/menu")
async def create_categorias(menu:Menu):
    new_categoria={"nombre":menu.nombre,"descripcion":menu.descripcion}
    result =conn.execute(menu1.insert().values(new_categoria))
    print(result)
    return "success"


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
def get_images():
        return conn.execute(galeria.select()).fetchall()


@create_menu.put("/admin/update_menu")
async def update_menu(
    categoria: str =Form(...),
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

    qr = menu1.select().where(menu1.c.nombre == categoria)
    reserv = conn.execute(qr).fetchone()
    
    if not reserv:
         return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': 'Esta categoria no existe'
            })

    qr = platillos.select().where(platillos.c.categoria_id == reserv['id'])
    reserv_exists = conn.execute(qr).fetchone()

    if reserv_exists:
        new_menu={
        "nombre": nombre, 
        "precio": precio,
        "descripcion": descripcion, 
        "imagen":generated_name, 
        "categoria_id": reserv['id']
        }
        rp = conn.execute(platillos.update().values(new_menu))
        print(rp)
   
        with open (generated_name, "wb") as file:
            file.write(file_content)
    
    return print("success")

@create_menu.delete("/admin/delate")
def borrar_categoria(nombre_categoria:str):
    conn.execute(menu1.delete().where(menu1.c.nombre == nombre_categoria))
    return "success"