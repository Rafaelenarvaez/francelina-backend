from msilib.schema import Directory
from fastapi import FastAPI
from routes.user import user
from routes.auth import auth_routes
from routes.reserva import create_reserva
from routes.create_menu import create_menu

from routes.router import api_router
# from config.db import db

from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
app = FastAPI()

load_dotenv() 

app.include_router(api_router, prefix='/api')


app.mount("/imagenes", StaticFiles(directory="imagenes"),name="imagenes")

# @app.on_event("startup")
# async def startup():
#     await db.connect()


# @app.on_event("shutdown")
# async def shutdown():
#     await db.disconnect()