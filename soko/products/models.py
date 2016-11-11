import datetime as dt
import decimal

from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class Product(SurrogatePK, Model):
    """A Products of the app."""
    __tablename__ = 'products'
    name = Column(db.String(80), nullable=False)
    product_type_id = reference_col('product_types', nullable=False)
    product_type = relationship('ProductType', backref='products')
    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref='products')
    description = Column(db.String(80), nullable=False)
    price = Column(db.Numeric(15, 2), nullable=False)
    quantity = Column(db.String(80), nullable=False)
    photo = Column(db.String(500), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name,  product_type_id, description, price, quantity, photo, user_id):
        self.name = name
        self.product_type_id = product_type_id
        self.description = description
        self.price = price
        self.quantity = quantity
        self.photo = photo
        self.user_id = user_id

    def __repr__(self):
        return '<Product %r>' % self.name + self.product_type_id + self.description + self.price + self.quantity + self.photo + self.user_id

    def serialize(self):
        return {"id": self.id, "name": self.name, "photo": self.photo, "description": self.description, "farmer": self.user_id, "product_type":self.product_type_id, "price": float(self.price)}


class ProductType(SurrogatePK, Model):
    __tablename__ = 'product_types'
    name = Column(db.String(80), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Product Type %r>' % self.name

    def serialize(self):
        return {"id": self.id, "name": self.name}


class ProductRatings(SurrogatePK, Model):
    __tablename__ = 'product_ratings'
    product = Column(db.Integer, nullable=False)
    rating = Column(db.Integer, nullable=False)
    review = Column(db.String(80), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, product, description):
        self.product = product
        self.description = description

    def __repr__(self):
        return '<Product %r>' % self.user + self.rating + self.review

