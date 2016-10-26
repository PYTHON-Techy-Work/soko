import datetime as dt

from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class Farmer(SurrogatePK, Model):
    __tablename__ = 'farmers'
    user_id = reference_col('users', nullable=True)
    user = relationship('User', backref='farmers')
    id_number = Column(db.Integer, nullable=True)
    photo = Column(db.String(80), nullable=True)
    product_id = reference_col('products', nullable=False)
    product = relationship('Product', backref='farmers')
    branch_id = reference_col('branches', nullable=True)
    branch = relationship('Branch', backref='farmers')
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user, photo, physical_address, stores):
        self.user = user
        self.photo = photo
        self.physical_address = physical_address
        self.stores = stores

    def __repr__(self):
        return '<Farmer %r>' % self.user


class Branch(SurrogatePK, Model):
    __tablename__ = 'branches'
    name = Column(db.String(80), unique=True, nullable=False)
    location = Column(db.String(80), nullable=True)
    farmer_id = reference_col('farmers', nullable=True)
    farmer = relationship('Farmer', backref='branches')
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name, location, farmer):
        self.name = name
        self.location = location
        self.farmer = farmer

    def __repr__(self):
        return '<Branch %r>' % self.user


