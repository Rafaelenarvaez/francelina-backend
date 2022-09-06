from asyncio import ensure_future
from calendar import c
import email
from numbers import Integral
from re import S
from typing import Collection
from xmlrpc.client import Boolean
from sqlalchemy import Integer, Table, Column, table, true, ForeignKey, Time
from sqlalchemy.orm import relationship, declarative_base, backref
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta,engine 
        

Base = declarative_base()

class Users(Base):
        __tablename__ = 'users'
        id = Column(Integer(), primary_key=True)
        name = Column(String(255))
        email = Column(String(255))
        password = Column(String(255))
users = Users.__table__

class Menu1(Base):
        __tablename__ = 'menu1'
        id =Column(Integer,primary_key=True)
        nombre= Column(String(255))
        descripcion= Column(String (255))
        relationship('Platillos', backref=backref('menu1', cascade="all,delete"))
menu1 = Menu1.__table__

class Platillos(Base):
        __tablename__ = 'platillos'
        id= Column(Integer(), primary_key=True)
        nombre= Column(String(255))
        descripcion = Column(String(255))
        precio = Column(Integer)
        categoria_id = Column(Integer(), ForeignKey('menu1.id', ondelete="CASCADE"), nullable=False)
        imagen = Column(String(255), nullable=True)

platillos = Platillos.__table__

class Reservas(Base):
        __tablename__ = 'reservas'
        id = Column(Integer(), primary_key=True)
        nombre= Column(String(255))
        apellido = Column(String(255))
        cedula = Column(String(255))
        email= Column(String(255))
        telefeno = Column(String(255))
        hora = Column(String(255))
        fecha= Column(String(255))
        fecha_de_cumpleaños = Column(String(255))
        numero_de_personas = Column(Integer)
        reservas_id = Column(Integer(), ForeignKey('reservas_admin.id'), nullable=False)
reservas = Reservas.__table__

class Reservas_admin(Base):
        __tablename__ = 'reservas_admin'
        id=Column(Integer(), primary_key=True)
        zona=Column(String(255))
        horas= Column(Time)
        capacidad=Column(Integer())
        relationship('Reservas', cascade="all,delete", backref=backref('reservas_admin', cascade="all,delete"))
reservas_admin = Reservas_admin.__table__

class Galeria(Base):
        __tablename__ = 'galeria'
        id= Column(Integer(), primary_key=True)
        ruta= Column ( String(255))
galeria= Galeria.__table__

Base.metadata.create_all(engine)
