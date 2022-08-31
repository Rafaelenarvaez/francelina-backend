from msilib.schema import Directory
from fastapi import FastAPI
from routes.user import user
from routes.auth import auth_routes
from routes.reserva import create_reserva
from routes.create_menu import create_menu

from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
app = FastAPI()

load_dotenv()
app.include_router(auth_routes)
app.include_router(user)
app.include_router(create_menu)
app.include_router(create_reserva)


app.mount("/imagenes", StaticFiles(directory="imagenes"),name="imagenes")
