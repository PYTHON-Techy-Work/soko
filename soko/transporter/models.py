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
    transporter_id = reference_col('transporters', nullable=True)
    transporter = relationship('Transporter', backref='drivers_licence')
    drivers_licence = Column(db.String(80), nullable=True)
    dl_expiry_date = Column(db.DateTime, nullable=False)
    national_id = Column(db.String(80), nullable=False)
    good_conduct = Column(db.String(80), nullable=True)
    pin_certificate = Column(db.String(80), nullable=True)
    psv_drivers_licence = Column(db.String(80), nullable=False)
    photo = Column(db.String(80), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, transporter, drivers_licence, dl_expiry_date, national_id, good_conduct, pin_certificate, psv_drivers_licence):
        self.transporter = transporter
        self.drivers_licence = drivers_licence
        self.dl_expiry_date = dl_expiry_date
        self.national_id = national_id
        self.good_conduct = good_conduct
        self.pin_certificate = pin_certificate
        self.psv_drivers_licence = psv_drivers_licence

    def __repr__(self):
        return '<Driver %r>' % self.transporter + self.drivers_licence + self.dl_expiry_date + self.national_id + self.good_conduct + self.pin_certificate + self.psv_drivers_licence

class County(SurrogatePK, Model):
    __tablename__ = 'counties'
    name = Column(db.String(80), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<County %r>' % self.name

    def serialize(self):
        return {"id": self.id, "name": self.name}