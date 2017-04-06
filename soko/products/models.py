from flask import url_for
import datetime as dt
import decimal
from decimal import Decimal as D
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
    lat = Column(db.Numeric(9, 6), nullable=False)
    lng = Column(db.Numeric(9, 6), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name,product_category_id, product_type_id, product_sub_type_id, description, packaging, price, quantity, photo,
                 user_id, lat, lng):
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
        self.lat = lat
        self.lng = lng

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "photo": self.photo,
            "seller": self.get_user(),
            "lat": self.lat,
            "lng": self.lng,
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
        user = User.query.filter_by(id=self.user_id).first()
        if user.first_name:
            return user.first_name
        else:
            return user.business_name



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
            "product_name": self.get_product().name,
            "product_price": float(self.get_product().price),
            "product": self.product.serialize(),
            "seller": self.get_seller(),
            "quantity": self.quantity,
            "total": float(self.total),
            "Date": self.created_at,
        }

    def get_user(self):
        from soko.user.models import User
        return User.query.get(self.user)

    def get_product(self):
        return Product.query.get(self.product_id)

    def get_seller(self):
        from soko.user.models import User
        product = Product.query.get(self.product_id)
        user = User.query.get(product.user_id)
        return user.first_name


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
    purchase_date = Column(db.DateTime, nullable=False)
    transporter = Column(db.Integer, nullable=False)
    status = Column(db.Enum('Accepted', 'Delivered', 'Pending', name='status_delivery'), nullable=False, default='Pending')
    lat = Column(db.Numeric(9, 6), nullable=False)
    lng = Column(db.Numeric(9, 6), nullable=False)
    total = Column(db.Numeric(15, 2), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user_id, product_id, quantity, purchase_date, transporter, status, lat, lng, total):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
        self.purchase_date = purchase_date
        self.transporter = transporter
        self.status = status
        self.lat = lat
        self.lng = lng
        self.total = total

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user_id,
            "product": self.product.serialize(),
            "quantity": self.quantity,
            "purchase_date": self.purchase_date,
            "transporter": self.transporter,
            "status": self.status,
            "lat": float(self.lat),
            "lng": float(self.lng),
            "total": float(self.total),
            "date": self.created_at
        }


class Order(SurrogatePK, Model):
    __tablename__ = 'orders'
    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref='orders')
    consumer = Column(db.String(120), nullable=True)
    order_date = Column(db.DateTime, nullable=False)
    status = Column(db.Enum('Accepted', 'Delivered', 'Pending', name='order_status'), nullable=False, default='Pending')
    lat = Column(db.Numeric(9, 6), nullable=False)
    lng = Column(db.Numeric(9, 6), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user_id, consumer, order_date, status, lat, lng):
        self.user_id = user_id
        self.consumer = consumer
        self.order_date = order_date
        self.status = status
        self.lat = lat
        self.lng = lng

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user_id,
            "consumer": self.consumer,
            "order_date": self.order_date,
            "status": self.status,
            "lat": float(self.lat),
            "lng": float(self.lng)
        }


class Variable(SurrogatePK, Model):
    __tablename__ = 'variables'
    cost_per_km_normal_time = Column(db.Numeric(15, 2), nullable=False)
    cost_per_km_peak_time = Column(db.Numeric(15, 2), nullable=False)
    cost_per_km_scheduled = Column(db.Numeric(15, 2), nullable=False)
    cost_waiting_time = Column(db.Numeric(15, 2), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, cost_per_km_normal_time, cost_per_km_peak_time, cost_per_km_scheduled, cost_waiting_time):
        self.cost_per_km_normal_time = cost_per_km_normal_time
        self.cost_per_km_peak_time = cost_per_km_peak_time
        self.cost_per_km_scheduled = cost_per_km_scheduled
        self.cost_waiting_time = cost_waiting_time

    def __repr__(self):
        return '<Variable %r>' % self.cost_per_km_normal_time + self.cost_per_km_peak_time + self.cost_per_km_scheduled + self.cost_waiting_time


class Earning(SurrogatePK, Model):
    __tablename__ = 'earnings'
    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref='earnings')
    order_id = reference_col('orders', nullable=False)
    order = relationship('Order', backref='earnings')
    total = Column(db.Numeric(9, 6), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user_id, order_id, total):
        self.user_id = user_id
        self.order_id = order_id
        self.total = total

    # def get_order(self):
    #     order = Order.query.filter_by(id=self.order_id).first()
    #     return order

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user_id,
            "order": self.order_id,
            "status": self.status,
            "date": self.created_at
        }


class Trip(SurrogatePK, Model):
    __tablename__ = 'trips'
    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref='trips')
    order_id = reference_col('orders', nullable=False)
    order = relationship('Order', backref='trips')
    status = Column(db.Enum('Accepted', 'Rejected', 'Started', 'Finished','Pending',  name='trip_status'), nullable=False, default='Pending')
    lat = Column(db.Numeric(9, 6), nullable=False)
    lng = Column(db.Numeric(9, 6), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user_id, order_id, status, lat, lng):
        self.user_id = user_id
        self.order_id = order_id
        self.status = status
        self.lat = lat
        self.lng = lng

    # def get_order(self):
    #     order = Order.query.filter_by(id=self.order_id).first()
    #     return order

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user_id,
            "order": self.order_id,
            "status": self.status,
            "latitude": self.lat,
            "longitude": self.lng,
            "date": self.created_at
        }


class Payment(SurrogatePK, Model):
    __tablename__ = 'payments'
    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref='payments')
    order_id = reference_col('orders', nullable=False)
    order = relationship('Order', backref='payments')
    payment_method = Column(db.Enum('Cheque', 'Cash', 'M-pesa', 'Debit Card', 'Credit Card',  name='payment_method'), nullable=False, default='Cash')
    amount = Column(db.Numeric(9, 6), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, user_id, order_id, payment_method, amount):
        self.user_id = user_id
        self.order_id = order_id
        self.payment_method = payment_method
        self.amount = amount

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user_id,
            "order": self.order_id,
            "payment_method": self.payment_method,
            "amount":self.amount,
            "date": self.created_at
        }