from fastapi import FastAPI


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
