from asyncio import ensure_future
import email
from numbers import Integral
from typing import Collection
from unicodedata import numeric
from sqlalchemy import Integer, Table, Column, table, true, ForeignKey, Time, Boolean
from sqlalchemy.orm import relationship, declarative_base, backref
from sqlalchemy.sql.sqltypes import Integer, String, Numeric
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
        descripcion= Column(String(255))
        relationship('Platillos', backref=backref('menu1', cascade="all,delete"))
menu1 = Menu1.__table__

class Platillos(Base):
        __tablename__ = 'platillos'
        id= Column(Integer(), primary_key=True)
        nombre= Column(String(255))
        descripcion = Column(String(255))
        precio = Column(Numeric(precision=8, scale=2))
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
        zona= Column(String(255))
        fecha= Column(String(255))
        fecha_de_cumpleaños = Column(String(255))
        numero_de_personas = Column(Integer)
        nota = Column(String(500
        ))
        reservas_id = Column(Integer(), ForeignKey('reservas_admin.id', ondelete='CASCADE'), nullable=False)
reservas = Reservas.__table__

class Reservas_admin(Base):
        __tablename__ = 'reservas_admin'
        id=Column(Integer(), primary_key=True)
        nombre=Column(String(255))
        hora1= Column(Time)
        hora2= Column(Time)
        capacidad=Column(Integer())
        max_capacity= Column(Boolean, default=False)
        zonas= relationship('zonas', secondary ='reservas_zona_aso', backref='zonas')
        relationship('Reservas', cascade="all,delete", backref=backref('reservas_admin',cascade="all,delete"))


reservas_admin = Reservas_admin.__table__

class Reserva_zona_aso(Base):
        __tablename__ = 'reservas_zona_aso'
        id = Column(Integer, primary_key=True)
        id_reservas_admin = Column(Integer, ForeignKey('reservas_admin.id', ondelete='CASCADE'))
        id_zonas = Column(Integer, ForeignKey('zonas.id', ondelete='CASCADE'))

reservas_zona_aso = Reserva_zona_aso.__table__

class Zonas(Base):
        __tablename__ = 'zonas'
        id=Column(Integer, primary_key=True)
        nombre=Column(String(255))
        relationship('Reservas', cascade="all,delete", backref=backref('zonas', cascade="all,delete"))

zonas = Zonas.__table__

class Galeria(Base):
        __tablename__ = 'galeria'
        id= Column(Integer(), primary_key=True)
        ruta= Column ( String(255))

galeria= Galeria.__table__


Base.metadata.create_all(engine)
