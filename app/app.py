from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.router import api_router
# from config.db import db

from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
app = FastAPI()

load_dotenv() 
origins = [
    "https://francelina.co",
    "https://www.francelina.co",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix='/api')


app.mount("/imagenes", StaticFiles(directory="imagenes"),name="imagenes")

# @app.on_event("startup")
# async def startup():
#     await db.connect()


# @app.on_event("shutdown")
# async def shutdown():
#     await db.disconnect()
