from flask import url_for
import datetime as dt
import decimal
import os

from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class ProductCategory(SurrogatePK, Model):
    __tablename__ = 'product_categories'
    name = Column(db.String(80), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Product Category Type %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "product_types": [pt.serialize() for pt in self.get_types()]
        }

    def get_types(self):
        return ProductType.query.filter_by(product_category_id=self.id)


class ProductType(SurrogatePK, Model):
    __tablename__ = 'product_types'
    name = Column(db.String(80), nullable=False)
    product_category_id = reference_col('product_categories', nullable=False)
    product_category = relationship('ProductCategory', backref='product_types')
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name, product_category_id):
        self.name = name
        self.product_category_id = product_category_id

    def __repr__(self):
        return '<Product Type Name %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "product_type": [pt.serialize() for pt in self.get_sub_types()]
        }

    def get_sub_types(self):
        return ProductSubType.query.filter_by(product_type_id=self.id)


class ProductSubType(SurrogatePK, Model):
    __tablename__ = 'product_sub_types'
    name = Column(db.String(80), nullable=False)
    description = Column(db.String(500), nullable=False)
    product_category_id = reference_col('product_categories', nullable=False)
    product_category = relationship('ProductCategory', backref='product_sub_sub_types')
    product_type_id = reference_col('product_types', nullable=False)
    product_type = relationship('ProductType', backref='product_sub_sub_types')
    photo = Column(db.String(500), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name, description, product_category_id, product_type_id, photo):
        self.name = name
        self.description = description
        self.product_category_id = product_category_id
        self.product_type_id = product_type_id
        self.photo = photo

    def __repr__(self):
        return '<Product Sub Type Name %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "product_category": self.product_category_id,
            "product_type": self.product_type_id,
            "photo": self.photo
        }

    def get_photo(self):
        if os.path.exists("soko/static/uploads/" + self.photo):
            return self.photo
        return "missing.jpg"


class Product(SurrogatePK, Model):
    __tablename__ = 'products'
    name = Column(db.String(80), nullable=False)
    product_category_id = reference_col('product_categories', nullable=False)
    product_category = relationship('ProductCategory', backref='products')
    product_type_id = reference_col('product_types', nullable=False)
    product_type = relationship('ProductType', backref='products')
    product_sub_type_id = reference_col('product_sub_types', nullable=False)
    product_sub_type = relationship('ProductSubType', backref='products')
    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref='products')
    description = Column(db.String(500), nullable=False)
    packaging = Column(db.String(80), nullable=False)
    price = Column(db.Numeric(15, 2), nullable=False)
    quantity = Column(db.Integer, nullable=False)
    photo = Column(db.String(500), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name,product_category_id, product_type_id, product_sub_type_id, description, packaging, price, quantity, photo,
                 user_id):
        self.name = name
        self.product_category_id = product_category_id
        self.product_type_id = product_type_id
        self.product_sub_type_id = product_sub_type_id
        self.description = description
        self.packaging = packaging
        self.price = price
        self.quantity = quantity
        self.photo = photo
        self.user_id = user_id

    def serialize(self):
        if self.get_user().business_name:
            seller = self.get_user().business_name,
        else:
            seller = self.get_user().first_name,
        return {
            "id": self.id,
            "name": self.name,
            "photo": self.photo,
            "seller": seller,
            "description": self.description,
            "quantity": self.quantity,
            "farmer": self.user_id,
            "product_type": self.product_type_id,
            "product_sub_type": self.product_sub_type_id,
            "price": float(self.price)
        }

    def get_photo(self):
        if os.path.exists("soko/static/uploads/" + self.photo):
            return self.photo
        return "missing.jpg"

    def get_user(self):
        from soko.user.models import User
        return User.query.filter_by(id=self.user_id).first()


class ProductRatings(SurrogatePK, Model):
    __tablename__ = 'product_ratings'
    product_id = reference_col('products', nullable=False)
    product = relationship('Product', backref='product_ratings')
    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref='product_ratings')
    rating = Column(db.Integer, nullable=False)
    review = Column(db.String(80), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, product_id, user_id, rating, review):
        self.product_id = product_id
        self.user_id = user_id
        self.rating = rating
        self.review = review

    def serialize(self):
        return {
            "id":self.id,
            "product":self.product_id,
            "user":self.user_id,
            "rating":self.rating,
            "review":self.review
        }


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

    def __init__(self, user, product_id, quantity, total):
        self.user = user
        self.product_id = product_id
        self.quantity = quantity
        self.total = total

    def serialize(self):
        return {
            "id": self.id,
            "user": self.get_user().first_name,
            "product": self.product.serialize(),
            "quantity": self.quantity,
            "total": float(self.total),
            "Date": self.created_at,
        }

    def get_user(self):
        from soko.user.models import User
        return User.query.get(self.user)


class ShoppingList(SurrogatePK, Model):
    __tablename__ = 'shopping_list'
    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref='shopping_list')
    product_id = reference_col('products', nullable=False)
    product = relationship('Product', backref='shopping_list')
    quantity = Column(db.Integer, nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user_id, product_id, quantity):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

    def serialize(self):
        return {
            "user_id": self.user_id,
            "product": self.product_id,
            "quantity": self.quantity,
        }


class Delivery(SurrogatePK, Model):
    __tablename__ = 'deliveries'
    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref='deliveries')
    product_id = reference_col('products', nullable=False)
    product = relationship('Product', backref='deliveries')
    quantity = Column(db.Integer, nullable=False)
    transporter = Column(db.Integer, nullable=False)
    status = Column(db.String(50), nullable=False)
    total = Column(db.Numeric(15, 2), nullable=False)
    lat = Column(db.Numeric(15, 10), nullable=False)
    lng = Column(db.Numeric(15, 10), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user_id, product_id, quantity, transporter, status, total, lat, lng):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
        self.transporter = transporter
        self.status = status
        self.total = total
        self.lat = lat
        self.lng = lng

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user_id,
            "product": self.product.serialize(),
            "quantity": self.quantity,
            "transporter": self.transporter,
            "status": self.status,
            "total": self.total,
            "lat": self.lat,
            "lng": self.lng,
            "date": self.created_at
        }