from email.mime import image
from hashlib import new
import imp
import os
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

@create_menu.post("/create_platillo")
async def create( 
    categoria: str,
    nombre: str,
    precio: str,
    descripcion: str,
    file:UploadFile=File(...)
    ):
    
    
    FILEPATH= "./imagenes/menu/"
    filename=file.filename
    extencion = filename.split(".")[1]

    if extencion not in ["png","JPG","jpg","PNG"]:
        return {"status": "error" , "detail": "Extencion no permitida"}

    ide = random.randint(1,100)

    id= str(ide) + "." + extencion
    generated_name = FILEPATH + id
    db_file_name = "/imagenes/menu/" + id
    file_content = await file.read()
    

    qr = menu1.select().where(menu1.c.nombre == categoria)
    menu = conn.execute(qr).fetchone()
    
    if not menu:
         return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': 'Esta categoria no existe'
            })

    qr = platillos.select().where(platillos.c.categoria_id == menu['id'])

    new_menu={
        "nombre": nombre, 
        "precio": precio,
        "descripcion": descripcion, 
        "imagen": db_file_name, 
        "categoria_id": menu['id']
    }

    rp = conn.execute(platillos.insert().values(new_menu))
    print(rp)

    with open (generated_name, "wb") as file:
        file.write(file_content)
    
    return {'msg': 'platillo creado con exito'}


@create_menu.delete("/img/delete")
async def remove_img(
    id: int
):
    qr = galeria.select().where(galeria.c.id == id)
    img = conn.execute(qr).fetchone()
    
    if not img:
         return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': 'Esta imagen no existe'
            })

    
    if os.path.isfile('.' + img['ruta']):
        os.remove('.' + img['ruta'])

    conn.execute(galeria.delete().where(galeria.c.id == id))

    return {
        'msg': 'imagen eliminada exitosamente'
    }
    



@create_menu.post("/uploadfile/galeria")
async def uploadfile_post(file:UploadFile=File(...)):

    FILEPATH= "./imagenes/galery/"
    filename=file.filename
    extencion = filename.split(".")[1]

    

    if extencion not in ["png","jpg"]:

       return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'message': 'Extension no permitida'
        })

    ide = random.randint(1,100)
    id= str(ide) + "." + extencion
    generated_name = FILEPATH + id
    db_file_name = "/imagenes/galery/" + id
    file_content = await file.read()

    new_foto={"ruta":db_file_name}
    conn.execute(galeria.insert().values(new_foto))


    with open (generated_name, "wb") as file:
        file.write(file_content)

    return {
        'msg': 'success'
    }


@create_menu.get("/get_img")
def get_images():
        return [dict(i) for i in conn.execute(galeria.select()).fetchall()]


@create_menu.get("/platos")
def get_platos(
    nested: bool
):
    if nested:
        menus = conn.execute(menu1.select()).fetchall()

        if not menus:
            return []
        
        platillos_obj = {}

        platillos_lst = []

        for m in menus:
            platos = conn.execute(platillos.select().where(platillos.c.categoria_id == m['id']))

            if platos:
                platillos_obj.__setitem__(m['nombre'], [dict(i) for i in platos])
            else:
                platillos_obj.__setitem__(m['nombre'], [])

        platillos_lst.append(platillos_obj)

        return platillos_lst
    
    else:
        return conn.execute(platillos.select()).fetchall()



@create_menu.put("/admin/update_menu")
async def update_menu(
    ides: str = Form(...),
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
        "imagen": generated_name, 
    }

    rp = conn.execute(platillos.update().values(new_menu).where(platillos.c.id == ides))
    print(rp)

    with open (generated_name, "wb") as file:
        file.write(file_content)
    
    return {'msg': 'Platillo actualizado'}

@create_menu.delete("/admin/delate")
def borrar_categoria(nombre_categoria:str):
    conn.execute(menu1.delete().where(menu1.c.nombre == nombre_categoria))
    return "success"