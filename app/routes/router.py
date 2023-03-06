from fastapi import APIRouter

from routes import (
    create_menu,
    reserva,
    user,
)

api_router = APIRouter()

api_router.include_router(create_menu.create_menu)
api_router.include_router(reserva.create_reserva)
api_router.include_router(user.user)