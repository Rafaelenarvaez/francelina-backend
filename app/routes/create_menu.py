

import os
import random
from typing import Any, Union
from fastapi import APIRouter, Depends, Security, UploadFile, File, Form, status
from sqlalchemy import desc
from pydantic import FilePath
from fastapi.responses import JSONResponse
from models.user import menu1
from models.user import platillos
from config.db import conn 
from models.user import galeria
from schemas.menu import Menu

from functions.deps import get_current_active_user

from uuid import uuid4


ide = []
create_menu = APIRouter()

@create_menu.post("/menu")
async def create_categorias(
    menu:Menu,
    ##current_user: Any = Security(get_current_active_user)
):
    new_categoria={
        "nombre": menu.nombre,
        "descripcion": menu.descripcion
    }
    result =conn.execute(menu1.insert().values(new_categoria))
    return "success"

@create_menu.post("/create_platillo")
async def create( 
    categoria: str,
    nombre: str,
    precio: str,
    descripcion: str,
    ##current_user: Any = Security(get_current_active_user)
):

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
        "categoria_id": menu['id']
    }

    new_dish_id = conn.execute(platillos.insert().values(new_menu)).inserted_primary_key[0]
    new_dish = conn.execute(platillos.select().where(platillos.c.id == new_dish_id)).fetchone()
   
    
    return new_dish

@create_menu.delete("/img/delete")
async def remove_img(
    id: int,
   ## current_user: Any = Security(get_current_active_user)
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
async def uploadfile_post(
    file:UploadFile=File(...),
   ## current_user: Any = Security(get_current_active_user)
):

    FILEPATH= "./imagenes/galery/"
    filename=file.filename
    extencion = filename.split(".")[1]


    if extencion not in ["png","jpg"]:

       return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'message': 'Extension no permitida'
        })

    ide = uuid4()
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
    nested: bool,
    paginate: bool,
    skip: int = 0,
    limit: int = 100,
):
    if nested:
        if paginate:
            query = menu1.select().offset(skip).limit(limit)
        else:
            query = menu1.select()

        menu = conn.execute(query).fetchall()

        if not menu:
            return []
        
        menu_lst = []

        for r in menu:

            dishes = conn.execute(platillos.select().where(platillos.c.categoria_id == r['id']))
            
            if dishes:
                dish_obj = {**dict(r), 'platillos': [{**dict(i)} for i in dishes]}
            else:
                dish_obj = {**dict(r), 'platillos': []}

            menu_lst.append(dish_obj)

        return menu_lst
    
    else:
        if paginate:
            query = platillos.select().order_by(desc(platillos.c.id)).offset(skip).limit(limit)
        else:
            query = platillos.select().order_by(desc(platillos.c.id))
        return conn.execute(query).fetchall()


@create_menu.put("/admin/update_menu")
async def update_menu(
    ides: int,
    nombre: str,
    precio: str,
    descripcion: str,
   ## current_user: Any = Security(get_current_active_user)
):
    new_menu = {
        "nombre": nombre, 
        "precio": precio,
        "descripcion": descripcion, 
    }

    rp = conn.execute(platillos.update().values(new_menu).where(platillos.c.id == ides))

    
    return rp


@create_menu.delete("/admin/delate")
def borrar_categoria(
    id:str,
   ## current_user: Any = Security(get_current_active_user)
):
    conn.execute(menu1.delete().where(menu1.c.id == id))
    return { 'message': "success"}


@create_menu.delete("/platos/delete")
def borrar_plato(
    id: int,
   ## current_user: Any = Security(get_current_active_user)
):
    conn.execute(platillos.delete().where(platillos.c.id == id))
    return { 'message': "success" }
