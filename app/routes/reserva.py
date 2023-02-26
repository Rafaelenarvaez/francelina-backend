from pathlib import Path
from typing import List, Any
from fastapi import APIRouter, status, Security
from fastapi.responses import JSONResponse
from sqlalchemy import desc
from pydantic import FilePath, BaseModel
from config.db import conn
from models.user import reservas_admin, reservas, zonas, reservasdia
from schemas.reserva_admin import Reserva_admin
from schemas.reserva_cliente import Reserva
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from dotenv import dotenv_values
from models.user import zonas 

from functions.deps import get_current_active_user

credenciales = dotenv_values(".env")

class Nombre_zona(BaseModel):
    nombre: str
    capacidad: int

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

    max = conn.execute(zonas.select().where(zonas.c.id_reservas_admin == id)).fetchone()
    
    if not reserv:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': 'Esta reserva admin no existe'
            })

    if max['max_capacity'] ==  True:
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


    qr = reservas.select().where(reservas.c.reservas_id == reserv['id'], reservas.c.fecha == reserva.fecha)
    reserv_exists = conn.execute(qr).fetchall()

    
    dia_reserva = conn.execute(reservasdia.insert().values( {"fecha":reserva.fecha , "reservas_admin_id":reserv['id']})).inserted_primary_key

    print("dia",dia_reserva)

    reserves_count = 0
    
    if reserv_exists:
        for r in reserv_exists:
            reserves_count += r['numero_de_personas']

        reserves_count += reserva.numero_de_personas

    else:
        reserves_count = reserva.numero_de_personas

    print('reservs count: ' + str(reserves_count))
    print(reserves_count, max['capacidad'])

    if reserves_count >= max['capacidad']:

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
            "zona_id":max['id'],
            "numero_de_personas": reserva.numero_de_personas, 
            "hora": reserva.hora, 
            "fecha": reserva.fecha,
            "fecha_de_cumpleaños":reserva.fecha_de_cumpleaños,
            "nota":reserva.nota,
            "reservas_id": reserv['id'],
            "dia_reserva_id":dia_reserva['id']
        }
        result = conn.execute(reservas.insert().values(new_reserv))
        
    if (reserves_count) >= max['capacidad']:
        conn.execute(reservas_admin.update().values(max_capacity=True))

    message = MessageSchema(
           subject="Confirmacion de reserva",
           recipients=[reserva.email, credenciales["EMAIL"]],   #List of recipients, as many as you can pass 
          template_body=new_reserv,
       )
   
    fm = FastMail(conf)
    await fm.send_message(message, template_name="email.html")
    return {"message" : "reserva creada exitosamente" }

@create_reserva.get("/max_capacity")
async def reserva(
        id: int,
        fecha: str,
        numero_de_personas: int
):
    qr = reservas_admin.select().where(reservas_admin.c.id == id)
    reserv = conn.execute(qr).fetchone()

    if not reserv:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': 'Esta reserva admin no existe'
            })
    
    max = conn.execute(zonas.select().where(zonas.c.id_reservas_admin == id)).fetchone()

    if max['max_capacity'] ==  True:
        return {
            "max_capacity": True
        }

    
    qr = reservas.select().where(reservas.c.reservas_id == reserv['id'], reservas.c.fecha == fecha )
    reserv_exists = conn.execute(qr).fetchall()
    
    reserves_count = 0
    
    if reserv_exists:
        for r in reserv_exists:
            reserves_count += r['numero_de_personas']

        reserves_count += numero_de_personas

    else:
        reserves_count = numero_de_personas

    if reserves_count >= max['capacidad']:
        return {
            "max_capacity": True,
            "capacidad": max['capacidad'],
            "reserves_count": reserves_count,
        }
    else:
        return {
            "max_capacity": False,
            "capacidad": max['capacidad'],
            "reserves_count": reserves_count,
        }

@create_reserva.get("/capacity_count")
async def reserva(
        id: int,
        fecha: str,
):
    qr = reservas_admin.select().where(reservas_admin.c.id == id)
    reserv = conn.execute(qr).fetchone()

    if not reserv:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': 'Esta reserva admin no existe'
            })
    
    
    dia_reserva = conn.execute(reservasdia.select().where(reservasdia.c.fecha == fecha, reservasdia.c.reservas_admin_id == id )).fetchone()

    if dia_reserva:
        zonas = conn.execute(zonas.select().where(zonas.c.id_reservas_admin == reserv)).fetchall()

        capacidad_zonas= []

        for n in zonas:
            raw_reserves = conn.execute(reservas.select().where(reservas.c.zonas_id == zonas, reservas.c.dia_reserva_id == dia_reserva["id"]))

            reserves_count = 0

            if raw_reserves :
                for r in raw_reserves:
                    reserves_count += r['numero_de_personas']

                capacidad_zonas.append({
                    "id": n["id"],
                    "nombre": n["nombre"],
                    "capacidad": n["capacidad"],
                    "num_reserves" : reserves_count,
                    "disponibilidad": True if reserves_count > n["capacidad"] else False
                })
            else:
                capacidad_zonas.append({
                    "id": n["id"],
                    "nombre": n["nombre"],
                    "capacidad": n["capacidad"],
                    "num_reserves" : reserves_count,
                    "disponibilidad": True 
                })
    else:
        capacidad_zonas= []

        for n in capacidad_zonas:
            capacidad_zonas.append({
                "id": n["id"],
                "nombre": n["nombre"],
                "capacidad": 0,
                "num_reserves" : reserves_count,
                "disponibilidad": True 
            })



    return capacidad_zonas    
    

@create_reserva.post("/admin/reserva") 
def create_reserva_admin(
    reserva: Reserva_admin, 
    nombre_zona:List[Nombre_zona],
    #current_user: Any = Security(get_current_active_user)
):
    
    new_reserva = {
        "hora1": reserva.hora1,
        "hora2":reserva.hora2,
        "nombre": reserva.nombre,
     }

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
            result=conn.execute(zonas.insert().values({ 'nombre': n.nombre ,"capacidad":n.capacidad, 'id_reservas_admin':reser_id})).inserted_primary_key[0]
            print(result)
            zona_id = conn.execute(zonas.select().where(zonas.c.id == result )).fetchone()
            zonas_ids.append(zona_id['id'])

    

    return {"message" : 'reserva creada'}

@create_reserva.delete("/admin/delete_reserva")
def delete_reserva(
    id: int,
    current_user: Any = Security(get_current_active_user)
):
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
def delete_reserva(
    id: int,
    current_user: Any = Security(get_current_active_user)
):
    reserve_exists = conn.execute(reservas_admin.select().where(reservas_admin.c.id == id))
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
    nested: bool,
    paginate: bool,
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Security(get_current_active_user),
):
    if nested:
        if paginate:
            query = reservas_admin.select().order_by(desc(reservas_admin.c.id)).offset(skip).limit(limit)
        else:
            query = reservas_admin.select().order_by(desc(reservas_admin.c.id))

        reservs_admin = conn.execute(query).fetchall()

        if not reservs_admin:
            return []
        
        reserv_admin_lst = []

        for r in reservs_admin:

            reservs = conn.execute(reservas.select().where(reservas.c.reservas_id == r['id']))
            zones = conn.execute(reservas_zona_aso.select().where(reservas_zona_aso.c.id_reservas_admin == r['id']))

            if reservs:
                reserv_obj = {**dict(r), 'reservas': [{**dict(i)} for i in reservs], 'zones': []}
            else:
                reserv_obj = {**dict(r), 'reservas': [], 'zones': []}

            for zoneAsso in zones:
                 #print(zoneAsso)
                zone = conn.execute(zonas.select().where(zonas.c.id == zoneAsso['id_zonas'])).fetchone()
                print(zone)
                reserv_obj['zones'].append(dict(zone))

            reserv_admin_lst.append(reserv_obj)

        return reserv_admin_lst
    
    else:
        if paginate:
            query = reservas.select().order_by(desc(reservas.c.id)).offset(skip).limit(limit)
        else:
            query = reservas.select().order_by(desc(reservas.c.id))
        return conn.execute(query).fetchall()

@create_reserva.get("/mostrar_horas")
def get_horas():
     #qr = reservas_admin.select().where(reservas_admin.c.max_capacity == False)
    qr = reservas_admin.select()


    reservs_admin = conn.execute(qr).fetchall()

    if not reservs_admin:
        return []
    
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