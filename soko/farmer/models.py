import datetime as dt

from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class Farmer(SurrogatePK, Model):
    __tablename__ = 'farmers'
    user = relationship('User')
    id_number = Column(db.Integer, nullable=True)
    photo = Column(db.String(80), nullable=True)
    product = relationship('Product')
    branch = relationship('Branch')
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user, photo, physical_address, stores):
        self.user = user
        self.photo = photo
        self.physical_address = physical_address
        self.stores = stores

    def __repr__(self):
        return '<Farmer %r>' % self.user