import datetime as dt

from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class Branch(SurrogatePK, Model):
    __tablename__ = 'branches'
    id = Column(db.Integer, nullable=False)
    location = Column(db.String(80), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self,  location):
        self.location = location

    def __repr__(self):
        return '<Location %r>' % self.location