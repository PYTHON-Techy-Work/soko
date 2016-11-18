# -*- coding: utf-8 -*-
"""location models."""
import datetime as dt


from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class Locations(SurrogatePK, Model):
    __tablename__ = 'locations'
    user = Column(db.Integer, nullable=False)
    latitude = Column(db.String(150), nullable=False)
    longitude = Column(db.String(150), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user, latitude, longitude):
        self.user = user
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return '<Location %r>' % self.user + self.latitude + self.longitude

    def serialize(self):
        return {"id": self.id, "user": self.user, "latitude": self.latitude, "longitude": self.longitude}