from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import FilePath
from config.db import conn
from models.user import reservas
from models.user import reservas_admin
from schemas.reserva_admin import Reserva_admin
from schemas.reserva_cliente import Reserva

create_reserva = APIRouter()


@create_reserva.post("/reserva")
def reserva(
        id: int,
        reserva: Reserva
):
    qr = reservas_admin.select().where(reservas_admin.c.id == id)
    reserv = conn.execute(qr).fetchone()

    if not reserv:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': 'Esta reserva no existe'
            })

    qr = reservas.select().where(reservas.c.reservas_id == reserv['id'])
    reserv_exists = conn.execute(qr).fetchall()

    if reserv_exists and len(reserv_exists) > reserv['capacidad']:
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={
                'msg': 'Capacidad maxima'
            })
    else:
        new_reserv = {
            "nombre": reserva.nombre,
            "email": reserva.email,
            "telefeno": reserva.telefono, 
            "hora": reserva.hora, 
            "fecha": reserva.fecha,
            "fecha de cumpleaños":reserva.nacimiento,
            "reservas_id": reserv['id']
        }
        result = conn.execute(reservas.insert().values(new_reserv))
        print(result)

    return ("success")


@create_reserva.post("/admin/reserva")
def create_reserva_admin(reserva: Reserva_admin):
    new_reserva = {"zona": reserva.zona,
                   "horas": reserva.horas, 
                   "capacidad": reserva.capacidad}
    conn.execute(reservas_admin.insert().values(new_reserva))
    return


@create_reserva.get("/reservas")
def get_reservas():
    return conn.execute(reservas_admin.select()).fetchall()
