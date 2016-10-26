# -*- coding: utf-8 -*-
"""Transporter models."""
import datetime as dt


from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class Transporter(SurrogatePK, Model):
    __tablename__ = 'transporters'
    user_id = reference_col('users', nullable=True)
    user = relationship('User', backref='transporters')
    vehicle_id = reference_col('vehicles', nullable=False)
    vehicle = relationship('Vehicle', backref='transporters')
    photo = Column(db.String(80), nullable=False)
    licence = Column(db.String(80), unique=True, nullable=False)
    location = Column(db.String(30), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user, vehicle, photo, licence, location):
        self.user = user
        self.vehicle = vehicle
        self.photo = photo
        self.licence = licence
        self.location = location

    def __repr__(self):
        return '<Transporter %r>' % self.user + self.vehicle + self.licence + self.location


class DiversLicence(SurrogatePK, Model):
    __tablename__ = 'drivers_licence'
    number = Column(db.String(30), nullable=False)
    transporter_id = reference_col('transporters', nullable=True)
    transporter = relationship('Transporter', backref='drivers_licence')
    licence_photo = Column(db.String(80), nullable=False)
    expiry_date = Column(db.DateTime, nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, number, transporter, licence_photo, expiry_date):
        self.number = number
        self.transporter = transporter
        self.licence_photo = licence_photo
        self.expiry_date = expiry_date

    def __repr__(self):
        return '<Drivers Licence %r>' % self.number + self.transporter + self.licence_photo + self.expiry_date