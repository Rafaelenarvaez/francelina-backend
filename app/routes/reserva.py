from pathlib import Path
from typing import List, Any
from fastapi import APIRouter, status, Security, Query
from fastapi.responses import JSONResponse
from sqlalchemy import desc, select, func
from pydantic import FilePath, BaseModel
from config.db import conn
from models.user import reservas_admin, reservas, zonas, reservasdia
from schemas.reserva_admin import Reserva_admin
from schemas.reserva_cliente import Reserva
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import dotenv_values
from models.user import zonas

from functions.deps import get_current_active_user
from datetime import timedelta, datetime

credenciales = dotenv_values(".env")


class Nombre_zona(BaseModel):
    nombre: str
    capacidad: int


""" conf = ConnectionConfig(
    MAIL_USERNAME=credenciales["EMAIL"],
    MAIL_PASSWORD=credenciales["PASS"],
    MAIL_FROM=credenciales["EMAIL"],
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
) """

create_reserva = APIRouter()


@create_reserva.post("/reserva")
async def reserva(
    admin_id: int,
    zone_id: int,
    reserva: Reserva,
):
    qr = reservas_admin.select().where(reservas_admin.c.id == admin_id)
    reserver_admin = conn.execute(qr).fetchone()

    zone = conn.execute(zonas.select().where(
        zonas.c.id == zone_id
    )).fetchone()

    if not reserver_admin or not zone:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': 'Esta reserva admin no existe'
            })

    hour_limit = datetime.strptime(
        reserva.fecha + ' ' + reserva.hora, '%d-%m-%Y %H:%M:%S') - timedelta(hours=4)

    if datetime.now() > hour_limit:
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={
                'msg': 'Debe reservar cuatro horas antes de la hora señalada'
            })
    date_stripd = reserva.fecha + ' ' + reserva.hora
    date_time = datetime.strptime(date_stripd, '%d-%m-%Y %H:%M:%S')

    if date_time > datetime.combine(datetime.now(), reserver_admin['hora2']) and date_time < datetime.combine(datetime.now(), reserver_admin['hora1']):
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={
                'msg': 'Hora fuera de rango'
            })

    dia_reserva = conn.execute(reservasdia.select().where(
        reservasdia.c.reservas_admin_id == admin_id,
        reservasdia.c.fecha == reserva.fecha
    )).fetchone()

    reserves_count = 0

    if not dia_reserva:
        dia_reserva = conn.execute(reservasdia.insert().values({
            "fecha": reserva.fecha,
            "reservas_admin_id": reserver_admin['id']
        })).inserted_primary_key[0]

    else:
        qr = reservas.select().where(
            reservas.c.reservas_id == reserver_admin['id'],
            reservas.c.dia_reserva_id == dia_reserva['id'],
            reservas.c.hora == reserva.hora
        )

        dia_reserva = dia_reserva['id']
        reserves_all = conn.execute(qr).fetchall()

        if reserves_all:
            for r in reserves_all:
                reserves_count += r["numero_de_personas"]

    if reserves_count + reserva.numero_de_personas > zone['capacidad']:
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={
                'msg': 'Capacidad maxima alcanzada'
            })

    new_reserve = {
        "nombre": reserva.nombre,
        "apellido": reserva.apellido,
        "cedula": reserva.cedula,
        "email": reserva.email,
        "telefeno": reserva.telefono,
        "zona": reserva.zona,
        "zona_id": zone['id'],
        "numero_de_personas": reserva.numero_de_personas,
        "hora": reserva.hora,
        "fecha": reserva.fecha,
        "fecha_de_cumpleaños": reserva.fecha_de_cumpleaños,
        "nota": reserva.nota,
        "reservas_id": reserver_admin['id'],
        "dia_reserva_id": dia_reserva
    }

    conn.execute(reservas.insert().values(new_reserve))

    message = MessageSchema(
         subject="Confirmacion de reserva",
         recipients=[reserva.email, credenciales["EMAIL"]],
        template_body=new_reserve,
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="email.html")

    return {"message": "reserva creada exitosamente"}


@create_reserva.get("/max_capacity")
async def reserva(
    id: int,
    id_zone: int,
    fecha: str,
    hora: str,
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

    zone = conn.execute(zonas.select().where(
        zonas.c.id == id_zone,
    )).fetchone()

    if not zone:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': 'Esta zona no existe'
            })

    dia_reserva = conn.execute(reservasdia.select().where(
        reservasdia.c.fecha == fecha,
        reservasdia.c.reservas_admin_id == id
    )).fetchone()

    reserves_count = 0

    if dia_reserva:
        reserves = conn.execute(reservas.select().where(
            reservas.c.zona_id == id_zone,
            reservas.c.dia_reserva_id == dia_reserva["id"],
            reservas.c.hora == hora
        )).fetchall()
        if reserves:
            for r in reserves:
                reserves_count += r["numero_de_personas"]

    return {
        "zone_id": zone["id"],
        "nombre": zone["nombre"],
        "capacidad_maxima": zone["capacidad"],
        "actual_reserve": reserves_count,
        "disponibilidad": False if (reserves_count + numero_de_personas) > zone["capacidad"] else True
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

    dia_reserva = conn.execute(reservasdia.select().where(
        reservasdia.c.fecha == fecha,
        reservasdia.c.reservas_admin_id == id
    )).fetchone()

    if dia_reserva:
        zones = conn.execute(zonas.select().where(
            zonas.c.id_reservas_admin == reserv['id'])).fetchall()

        capacidad_zonas = []

        for n in zones:
            raw_reserves = conn.execute(reservas.select().where(
                reservas.c.zona_id == n['id'],
                reservas.c.dia_reserva_id == dia_reserva["id"]
            )).fetchall()

            reserves_count = 0

            if raw_reserves:
                for r in raw_reserves:
                    reserves_count += r['numero_de_personas']

                capacidad_zonas.append({
                    "id": n["id"],
                    "nombre": n["nombre"],
                    "capacidad_maxima": n["capacidad"],
                    "num_reserves": reserves_count,
                    "disponibilidad": True if reserves_count > n["capacidad"] else False
                })
            else:
                capacidad_zonas.append({
                    "id": n["id"],
                    "nombre": n["nombre"],
                    "capacidad_maxima": n["capacidad"],
                    "num_reserves": reserves_count,
                    "disponibilidad": True
                })
    else:

        zones = conn.execute(zonas.select().where(
            zonas.c.id_reservas_admin == reserv['id'])).fetchall()

        capacidad_zonas = []

        for n in zones:
            capacidad_zonas.append({
                "id": n["id"],
                "nombre": n["nombre"],
                "capacidad_maxima": n["capacidad"],
                "num_reserves": 0,
                "disponibilidad": True
            })

    return capacidad_zonas


@create_reserva.post("/admin/reserva")
def create_reserva_admin(
    reserva: Reserva_admin,
    nombre_zona: List[Nombre_zona],
    ##current_user: Any = Security(get_current_active_user)
):

    new_reserva = {
        "hora1": reserva.hora1,
        "hora2": reserva.hora2,
        "nombre": reserva.nombre,
    }

    reser_id = conn.execute(reservas_admin.insert().values(
        new_reserva)).inserted_primary_key[0]

    zonas_ids = []

    if len(nombre_zona) == 0:
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={
                'msg': 'Zonas vacias'
            })
    else:
        for n in nombre_zona:
            result = conn.execute(zonas.insert().values(
                {'nombre': n.nombre, "capacidad": n.capacidad, 'id_reservas_admin': reser_id})).inserted_primary_key[0]
            zona_id = conn.execute(zonas.select().where(
                zonas.c.id == result)).fetchone()
            zonas_ids.append(zona_id['id'])

    return {"message": 'reserva creada'}


@create_reserva.delete("/admin/delete_reserva")
def delete_reserva(
    id_reserve: int,
    ##current_user: Any = Security(get_current_active_user)
):
    reserve = conn.execute(reservas.select().where(
        reservas.c.id == id_reserve
    )).fetchone()

    if not reserve:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'message': 'Esta reserva no existe'
            })
    else:

        conn.execute(reservas.delete().where(reservas.c.id == id_reserve))

        qr = select([func.count(reservas.c.id).label('reserves_count')]).where(
            reservas.c.fecha == reserve['fecha'],
            reservas.c.reservas_id == reserve['reservas_id']
        ).select_from(reservas)

        count = conn.execute(qr).fetchone()

        if count['reserves_count'] == 0:
            conn.execute(reservasdia.delete().where(
                reservasdia.c.id == reserve['dia_reserva_id']
            ))

        return {'message': 'Reserva eliminada correctamente'}


@create_reserva.delete("/admin/delete_reserva_admin")
def delete_reserva(
    id: int,
    ##current_user: Any = Security(get_current_active_user)
):
    reserve_exists = conn.execute(
        reservas_admin.select().where(reservas_admin.c.id == id))
    if not reserve_exists:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'message': 'Esta reserva no existe'
            })
    conn.execute(reservas_admin.delete().where(reservas_admin.c.id == id))
    return {'message': 'Reserva eliminada correctamente'}


@create_reserva.get("/reservas_dias")
def get_reservas_admin(
    # nested: bool,
    # paginate: bool,
    # skip: int = 0,
    # limit: int = 100,
    # current_user: Any = Security(get_current_active_user),
):
    query = reservas_admin.select().order_by(desc(reservas_admin.c.id))
    reserves_admin = conn.execute(query).fetchall()

    reserv_admin_lst = []

    for r in reserves_admin:
        query = reservasdia.select().where(
            reservasdia.c.reservas_admin_id == r['id']
        )
        dia_reservas = conn.execute(query).fetchall()

        query = zonas.select().where(zonas.c.id_reservas_admin == r['id'])
        zones = conn.execute(query).fetchall()

        dia_reserva_lst = []

        for d in dia_reservas:
            query = select([func.count(reservas.c.id).label('reserves_count')]).where(
                reservas.c.dia_reserva_id == d['id'],
                reservas.c.reservas_id == r["id"]
            ).select_from(reservas)

            count = conn.execute(query).fetchone()

            dia_reserva_lst.append({
                **d,
                **count,
                'reserves': []
            })

        reserv_admin_lst.append({
            **r,
            'dias': dia_reserva_lst,
            'zones': zones
        })

    return reserv_admin_lst


@create_reserva.get("/reservas_dias/detalles")
def get_reservas_detalles(
    dia_id: int,
    id_zones: List[int] = Query(None)
):
    if len(id_zones) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'msg': 'Minimo un id de zonas requerido'
            })

    query = reservasdia.select().where(reservasdia.c.id == dia_id)
    dia = conn.execute(query).fetchone()

    if not dia:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': 'Este día de reserva no existe'
            })

    reserves_result = {
        'reserves': []
    }

    query = reservas.select().where(
        reservas.c.dia_reserva_id == dia_id,
        reservas.c.reservas_id == dia['reservas_admin_id'],
    )
    reserves = conn.execute(query).fetchall()
    reserves_result['reserves'] = reserves

    return reserves_result


@create_reserva.get("/reserves-flat")
def get_reserves_flat(

):
    query = reservas.select().order_by(desc(reservas.c.id)).offset(0).limit(5)
    return conn.execute(query).fetchall()


@create_reserva.get("/mostrar_horas")
def get_horas():
    qr = reservas_admin.select()

    reservs_admin = conn.execute(qr).fetchall()

    if not reservs_admin:
        return []

    reserv_admin_lst = []

    for r in reservs_admin:
        zones = conn.execute(zonas.select().where(
            zonas.c.id_reservas_admin == r['id'])).fetchall()

        reser_admin = {
            'horas': r,
            'zonas': []
        }
        reser_admin['zonas'] = zones
        reserv_admin_lst.append(reser_admin)

    return reserv_admin_lst
