# -*- coding: utf-8 -*-
"""Transporter models."""
import datetime as dt


from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship



class Transporter(SurrogatePK, Model):
    __tablename__ = 'transporters'
    user = relationship('users')
    vehicle = relationship('vehicle')
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
        return '<Transporter %r>' % self.user + self.vehicle + self.licence