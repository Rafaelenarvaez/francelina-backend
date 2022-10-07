from ctypes import Union
from datetime import datetime, time, date
from pathlib import Path
import re
from typing import List
from unittest import result
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
from models.user import zonas 
from models.user import reservas_zona_aso


credenciales = dotenv_values(".env")


conf = ConnectionConfig(
    MAIL_USERNAME = credenciales["EMAIL"],
    MAIL_PASSWORD = credenciales["PASS"],
    MAIL_FROM = credenciales["EMAIL"],
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
                'msg': 'Esta reserva admin no existe'
            })

    if reserv['max_capacity'] ==  True:
        print('aca 1')
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={
                'msg': 'Capacidad maxima'
            })

    if reserva.hora > reserv['hora2'] or reserva.hora < reserv['hora1']:
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={
                'msg': 'Hora fuera de rango'
            })

    
    qr = reservas.select().where(reservas.c.reservas_id == reserv['id'], reservas.c.fecha == reserva.fecha, reservas.c.zona == reserva.zona )
    reserv_exists = conn.execute(qr).fetchall()
    
    reserves_count = 0
    
    if reserv_exists:
        for r in reserv_exists:
            reserves_count += r['numero_de_personas']

        reserves_count += reserva.numero_de_personas

    else:
        reserves_count = reserva.numero_de_personas

    print(reserves_count)

    if reserves_count > reserv['capacidad']:
        print('aca 2')

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
            "zona": reserva.zona,
            "numero_de_personas": reserva.numero_de_personas, 
            "hora": reserva.hora, 
            "fecha": reserva.fecha,
            "fecha_de_cumpleaños":reserva.fecha_de_cumpleaños,
            "nota":reserva.nota,
            "reservas_id": reserv['id']
        }
        print('hasta aqui')
        result = conn.execute(reservas.insert().values(new_reserv))
        
    if (reserves_count + new_reserv['numero_de_personas']) > reserv['capacidad']:
        conn.execute(reservas_admin.update().values(max_capacity=True))

    message = MessageSchema(
          subject="Confirmacion de reserva",
          recipients=[reserva.email, credenciales["EMAIL"]],  # List of recipients, as many as you can pass 
         template_body=new_reserv,
      )
   
    fm = FastMail(conf)
    await fm.send_message(message, template_name="email.html")
    return {"message" : "reserva creada exitosamente" }


@create_reserva.post("/admin/reserva") 
def create_reserva_admin(reserva: Reserva_admin, nombre_zona:List[str]):

    new_reserva = {
                   "hora1": reserva.hora1,
                   "hora2":reserva.hora2,
                   "capacidad": reserva.capacidad}

    reser_id = conn.execute(reservas_admin.insert().values(new_reserva)).inserted_primary_key[0]

    zonas_ids = []

    if len(nombre_zona) == 0:
         return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={
                'msg': 'Zonas vacias'
            })
    else: 
        for n in nombre_zona: 
            result = conn.execute(zonas.select().where(zonas.c.nombre == n )).fetchone()
            if result:
                zonas_ids.append(result['id'])
            if not result:
                conn.execute(zonas.insert().values({ 'nombre': n})).inserted_primary_key
                zona_id = conn.execute(zonas.select().where(zonas.c.nombre == n )).fetchone()
                zonas_ids.append(zona_id['id'])
    for id in zonas_ids:
        new_ids={
            "id_reservas_admin":reser_id,
            "id_zonas":id
        }
        conn.execute(reservas_zona_aso.insert().values(new_ids))
  

    return {"message" : 'reserva creada'}

@create_reserva.delete("/admin/delete_reserva")
def delete_reserva(id: int):
    reserve_exists = conn.execute(reservas.select().where(reservas.c.reservas_id == id))
    if not reserve_exists: 
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'message': 'Esta reserva no existe'
            })
    else:
        conn.execute(reservas.delete().where(reservas.c.id == id))

        return {'message': 'Reserva eliminada correctamente'}

@create_reserva.delete("/admin/delete_reserva_admin")
def delete_reserva(id: int):
    reserve_exists = conn.execute(reservas_admin.select().where(reservas_admin.c.id == id))
    print(reserve_exists)
    if not reserve_exists: 
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'message': 'Esta reserva no existe'
            })
    conn.execute(reservas_admin.delete().where(reservas_admin.c.id == id))
    return {'message': 'Reserva eliminada correctamente'}
        

@create_reserva.get("/reservas")
def get_reservas(
  
    nested: bool
):
    if nested:
        reservs_admin = conn.execute(reservas_admin.select()).fetchall()

        if not reservs_admin:
            return []
        
        reserv_obj = {}

        reserv_lst = []

        for r in reservs_admin:
            reservs = conn.execute(reservas.select().where(reservas.c.reservas_id == r['id']))
            

            if reservs:
                reserv_obj.__setitem__(str(r['hora1']) + ' a ' + str(r['hora2']), [{**dict(i)} for i in reservs])
            else:
                reserv_obj.__setitem__(str(r['hora1']) + ' a ' + str(r['hora2']), [])

        reserv_lst.append(reserv_obj)

        return reserv_lst
    
    else:
        return conn.execute(reservas.select()).fetchall()



@create_reserva.get("/mostrar_horas")
def get_horas():
    # qr = reservas_admin.select().where(reservas_admin.c.max_capacity == False)
    qr = reservas_admin.select()


    reservs_admin = conn.execute(qr).fetchall()

    if not reservs_admin:
        return []
    
    reserv_admin_obj = {}

    reserv_admin_lst = []


    for r in reservs_admin:
        qr = reservas_zona_aso.select().where(reservas_zona_aso.c.id_reservas_admin == r['id'])
        asso_data = [ dict(i) for i in conn.execute(qr).fetchall()]

        reser_admin = {
            'horas': r,
            'zonas': []
        }

        for asso in asso_data:
            zonas_raw = conn.execute(zonas.select().where(zonas.c.id == asso['id_zonas'])).fetchone()
            if zonas_raw:
                reser_admin['zonas'].append(zonas_raw)

        reserv_admin_lst.append(reser_admin)

    return reserv_admin_lst