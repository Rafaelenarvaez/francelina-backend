from fastapi import APIRouter, Security, status
from fastapi.responses import JSONResponse
from functions.deps import get_current_active_user
from schemas.events import Events, EventsBase
from config.db import conn
from models.user import t_events
from typing import Any, List


events = APIRouter()


@events.get("/events")
def get_events() -> List[Events]:
    return conn.execute(t_events.select()).fetchall()


@events.post(
    "/events"
)
async def create_event(
    *,
    event_in: EventsBase,
    # current_user: Any = Security(get_current_active_user)
):
    new_event = conn.execute(t_events.insert().values(
        event_in.dict()))

    if new_event:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                'msg': f"Evento creado exitosamente!",
            })
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'msg': f"El servicio no está disponible actualmente. Intente mas tarde",
            })


@events.put("/events")
def update_event(
    id: int,
    event_in: EventsBase,
    current_user: Any = Security(get_current_active_user)
) -> Events:
    qr = t_events.select().where(t_events.c.id == id)
    old_event = conn.execute(qr).fetchone()

    if not old_event:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': f"El evento no existe",
            })

    conn.execute(t_events.update().values(
        event_in.dict()
    ).where(t_events.c.id == id))

    updated = conn.execute(t_events.select().where(
        t_events.c.id == id)).fetchone()

    return updated


@events.delete("/events")
def delete_event(
    id: int,
    current_user: Any = Security(get_current_active_user)
):
    qr = t_events.select().where(t_events.c.id == id)
    old_event = conn.execute(qr).fetchone()

    if not old_event:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'msg': f"El evento no existe",
            })

    conn.execute(t_events.delete().where(t_events.c.id == id))
    return {'message': "success"}
