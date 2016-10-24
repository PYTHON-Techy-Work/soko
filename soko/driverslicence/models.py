import datetime as dt


from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class DriversLicence(SurrogatePK, Model):
    __tablename__ = 'transporters'
    licence = Column(db.String(30), nullable=False)
    user = relationship('transporter')
    vehicle = relationship('vehicle')
    expiry_date = Column(db.DateTime, nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self,licence, user, vehicle, expiry_date):
        self.licence = licence
        self.user = user
        self.vehicle = vehicle
        self.expiry_date = expiry_date

    def __repr__(self):
        return '<Transporter %r>' % self.licence + self.user + self.vehicle + self.expiry_date