# -*- coding: utf-8 -*-
"""Transporter models."""
import datetime as dt


from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class Customer(SurrogatePK, Model):
    __tablename__ = 'customers'
    user_id = reference_col('users', nullable=True)
    user = relationship('User', backref='customers')
    vehicle_id = reference_col('vehicles', nullable=False)
    vehicle = relationship('Vehicle', backref='customers')
    photo = Column(db.String(80), nullable=False)
    dob = Column(db.String(80), unique=True, nullable=False)
    home_address = Column(db.String(150), nullable=True)
    work_address = Column(db.String(150), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user, vehicle, photo, licence, location):
        self.user = user
        self.vehicle = vehicle
        self.photo = photo
        self.licence = licence
        self.location = location

    def __repr__(self):
        return '<Customer %r>' % self.user + self.vehicle + self.licence + self.location