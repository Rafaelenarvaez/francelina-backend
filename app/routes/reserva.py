from ctypes import Union
from datetime import datetime, time, date
from pathlib import Path
import re
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import FilePath
from config.db import conn
from models.user import reservas
from models.user import reservas_admin
from schemas.reserva_admin import Reserva_admin
from schemas.reserva_cliente import Reserva
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from dotenv import dotenv_values


credenciales = dotenv_values(".env")


conf = ConnectionConfig(
    MAIL_USERNAME = credenciales["EMAIL"],
    MAIL_PASSWORD = credenciales["PASS"],
    MAIL_FROM = "rafaelnarvaez1510@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER = Path(__file__).parent / 'templates',
)



create_reserva = APIRouter()




@create_reserva.post("/reserva")
async def reserva(
        id: int,
        reserva: Reserva,
        ):
    qr = reservas_admin.select().where(reservas_admin.c.id == id)
    reserv = conn.execute(qr).fetchone()

    if not reserv:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': 'Esta reserva ya existe'
            })

    qr = reservas.select().where(reservas.c.reservas_id == reserv['id'], reservas.c.fecha == reserva.fecha)
    reserv_exists = conn.execute(qr).fetchall()
    
     

    if len(reserv_exists) >= reserv['capacidad']:
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={
                'msg': 'Capacidad maxima'
            })
    else:
        new_reserv = {
            "nombre": reserva.nombre,
            "apellido":reserva.apellido,
            "cedula":reserva.cedula,
            "email": reserva.email,
            "telefeno": reserva.telefono, 
            "hora": reserva.hora, 
            "fecha": reserva.fecha,
            "fecha_de_cumpleaños":reserva.fecha_de_cumpleaños,
            "reservas_id": reserv['id']
        }
        result = conn.execute(reservas.insert().values(new_reserv))
        

    message = MessageSchema(
        subject="Confirmacion de reserva",
        recipients=[reserva.email],  # List of recipients, as many as you can pass 
        template_body=new_reserv,
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="email.html")
    return {"message" : "reserva creada exitosamente" }


@create_reserva.post("/admin/reserva") 
def create_reserva_admin(reserva: Reserva_admin):
    new_reserva = {"zona": reserva.zona,
                   "horas": reserva.horas, 
                   "capacidad": reserva.capacidad}
    conn.execute(reservas_admin.insert().values(new_reserva))
    return {"message" : 'reserva creada'}

@create_reserva.delete("/admin/delete_reserva")
def delete_reserva(cedula:str):
    conn.execute(reservas.delete().where(reservas.c.cedula == cedula))
    return "success"



@create_reserva.get("/reservas")
def get_reservas():
    return conn.execute(reservas_admin.select()).fetchall()

@create_reserva.post("/validar_fecha")
def validar(fecha: datetime,
            id:str):

    qr = reservas_admin.select().where(reservas_admin.c.id == id)
    reserv = conn.execute(qr).fetchone()

    if not reserv:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': 'Esta reserva no existe'
            })

    qr = reservas.select().where(reservas.c.reservas_id == reserv['id'], reservas.c.fecha == fecha)
    reserv_exists = conn.execute(qr).fetchall()

    if len(reserv_exists) > reserv['capacidad']:
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={
                'msg': 'Capacidad maxima'
                
            })
        print(reserv)
    return

