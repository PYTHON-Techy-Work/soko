from flask import url_for
import datetime as dt
import decimal

from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class Product(SurrogatePK, Model):
    __tablename__ = 'products'
    name = Column(db.String(80), nullable=False)
    product_type_id = reference_col('product_types', nullable=False)
    product_type = relationship('ProductType', backref='products')
    product_sub_type_id = reference_col('product_sub_type', nullable=False)
    product_sub_type = relationship('ProductSubType', backref='products')
    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref='products')
    description = Column(db.String(500), nullable=False)
    packaging = Column(db.String(80), nullable=False)
    price = Column(db.Numeric(15, 2), nullable=False)
    quantity = Column(db.Integer, nullable=False)
    photo = Column(db.String(500), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name, product_type_id, product_sub_type_id, description, packaging, price, quantity, photo, user_id):
        self.name = name
        self.product_type_id = product_type_id
        self.product_sub_type_id = product_sub_type_id
        self.description = description
        self.packaging = packaging
        self.price = price
        self.quantity = quantity
        self.photo = photo
        self.user_id = user_id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "photo": self.photo,
            "description": self.description,
            "quantity": self.quantity,
            "farmer": self.user_id,
            "product_type": self.product_type_id,
            "product_sub_type": self.product_sub_type_id,
            "price": float(self.price)
        }


class ProductType(SurrogatePK, Model):
    __tablename__ = 'product_types'
    name = Column(db.String(80), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Product Type %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


class ProductSubType(SurrogatePK, Model):
    __tablename__ = 'product_sub_type'
    name = Column(db.String(80), nullable=False)
    description = Column(db.String(500), nullable=False)
    product_type_id = reference_col('product_types', nullable=False)
    product_type = relationship('ProductType', backref='product_sub_type')
    photo = Column(db.String(500), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name, description, product_type_id, photo):
        self.name = name
        self.description = description
        self.product_type_id = product_type_id
        self.photo = photo

    def __repr__(self):
        return '<Product Name %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "product_type": self.product_type_id,
            "photo": self.photo
        }


class ProductRatings(SurrogatePK, Model):
    __tablename__ = 'product_ratings'
    product = Column(db.Integer, nullable=False)
    rating = Column(db.Integer, nullable=False)
    review = Column(db.String(80), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, product, rating, review):
        self.product = product
        self.rating = rating
        self.review = review

    def __repr__(self):
        return '<Product %r>' % self.user + self.rating + self.review


class Cart(SurrogatePK, Model):
    __tablename__ = 'cart'
    product_id = reference_col('products', nullable=False)
    product = relationship('Product', backref='cart')
    user = Column(db.Integer, nullable=False)
    quantity = Column(db.Integer, nullable=False)
    total = Column(db.Numeric(15, 2), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user, product_id, quantity, total):
        self.user = user
        self.product_id = product_id
        self.quantity = quantity
        self.total = total

    def __repr__(self):
        return '<Cart %r>' % self.user + self.product_id + self.quantity + self.total

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user,
            "product": self.product.serialize(),
            "quantity": self.quantity,
            "total": float(self.total),
        }


class Purchase(SurrogatePK, Model):
    __tablename__ = 'purchases'
    product_id = reference_col('products', nullable=False)
    product = relationship('Product', backref='purchases')
    user = Column(db.Integer, nullable=False)
    quantity = Column(db.Integer, nullable=False)
    total = Column(db.Numeric(15, 2), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user, product, quantity, total):
        self.user = user
        self.product = product
        self.quantity = quantity
        self.total = total

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user,
            "product": self.product.serialize(),
            "quantity": self.quantity,
            "total": float(self.total),
            "Date": self.created_at,
        }
