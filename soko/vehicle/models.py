from . import *
import datetime as dt

from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class Vehicle(SurrogatePK, Model):
    __tablename__ = 'vehicles'
    number = Column(db.String(30), unique=True)
    type_id = reference_col('vehicle_Type', nullable=False)
    type = relationship('VehicleType', backref='vehicles')
    colour = Column(db.String(30), unique=True)
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


class VehicleType(SurrogatePK, Model):
    __tablename__ = 'vehicle_Type'
    name = Column(db.String(30), nullable=False)
    make = Column(db.String(30), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name, make):
        self.name = name
        self.make = make

    def __repr__(self):
        return '<Vehicle Type %r>' % self.name + self.make
