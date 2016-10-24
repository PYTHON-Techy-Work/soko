from . import *
import datetime as dt

from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class Vehicle(SurrogatePK, Model):
    __tablename__ = 'Vehicles'
    number = Column(db.String(30), unique=True)
    type = Column(db.String(30), nullable=False)
    colour = Column(db.String(30), unique=True)
    user = relationship('transporter')
    expiry_date = Column(db.DateTime, nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, number, type, colour, user, expiry_date):
        self.number = number
        self.type = type
        self.colour = colour
        self.user = user
        self.expiry_date = expiry_date

    def __repr__(self):
        return '<Vehicle %r>' % self.licence + self.user + self.vehicle + self.expiry_date


class Vehicle_Type(SurrogatePK, Model):
    __tablename__ = 'vehicle_Type'
    name = Column(db.String(30), unique=True)
    make = Column(db.String(30), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name, make):
        self.name = name
        self.make = make

    def __repr__(self):
        return '<Vehicle Type %r>' % self.name + self.make
