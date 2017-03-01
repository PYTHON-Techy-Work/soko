# -*- coding: utf-8 -*-
"""Transporter models."""
import datetime as dt


from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class Transporter(SurrogatePK, Model):
    __tablename__ = 'transporters'
    user_id = reference_col('users', nullable=True)
    user = relationship('User', backref='transporters')
    vehicle_type = Column(db.String(80), nullable=False)
    vehicle_reg_no = Column(db.String(80), nullable=False)
    vehicle_color = Column(db.String(80), unique=True, nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user_id, vehicle_type, vehicle_reg_no, vehicle_color):
        self.user_id = user_id
        self.vehicle_type = vehicle_type
        self.vehicle_reg_no = vehicle_reg_no
        self.vehicle_color = vehicle_color

    def __repr__(self):
        return '<Transporter %r>' % self.user + self.vehicle + self.licence + self.location


class TransporterCurrentLocation(SurrogatePK, Model):
    __tablename__ = 'transporter_current_location'
    user_id = reference_col('users', nullable=True)
    user = relationship('User', backref='transporter_current_location')
    latitude = Column(db.String(80), nullable=True)
    longitude = Column(db.String(80), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user_id, latitude, longitude):
        self.user_id = user_id
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return '<Driver %r>' % self.user_id + self.latitude + self.longitude


class TransporterRatings(SurrogatePK, Model):
    __tablename__ = 'transporter_ratings'
    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref='transporter_ratings')
    rating = Column(db.Integer, nullable=False)
    review = Column(db.String(80), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, transporter_id, user_id, rating, review):
        self.transporter_id = transporter_id
        self.user_id = user_id
        self.rating = rating
        self.review = review

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user_id,
            "rating": self.rating,
            "review": self.review
        }


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