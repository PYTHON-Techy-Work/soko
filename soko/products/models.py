# -*- coding: utf-8 -*-
"""Transporter models."""
import datetime as dt


from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship



class Products(db.Model):
    """A Products of the app."""
    __tablename__ = 'products'
    id = Column(db.Integer(primary_key=True))
    product_type = Column(db.Integer, nullable=False)
    description = Column(db.String(80), nullable=False)
    price = Column(db.Integer, nullable=False)
    quantity = Column(db.String(80), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, product_type, description, price, quantity, location):
        self.product_type = product_type
        self.description = description
        self.price = price
        self.quantity = quantity
        self.location = location

    def __repr__(self):
        return '<Product %r>' % self

class Product_Type(db.Model):
    """A product_type of the app."""
    __tablename__ = 'product_types'
    id = Column(db.Integer(primary_key=True))
    type = Column(db.String(80), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return '<Product %r>' % self.user