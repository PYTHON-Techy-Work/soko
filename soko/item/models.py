# -*- coding: utf-8 -*-
"""Item models."""
import datetime as dt

from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship

class ItemType(SurrogatePK, Model):
    """A type of item."""

    __tablename__ = 'itemtypes'
    name = Column(db.String(80), unique=True, nullable=False)
    descr = Column(db.String(512), unique=True, nullable=False)
   
    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<ItemType({name!r})>'.format(name=self.name)


# An instance of things
class Item(SurrogatePK, Model):
    """A specific quantity of a specific type of items."""

    __tablename__ = 'items'
    name = Column(db.String(80), unique=True, nullable=False)
    type_id = reference_col('itemtypes', nullable=True)
    user_id = reference_col('users', nullable=True)

    type = relationship('ItemType', backref='items')
    user = relationship('User', backref='items')
   
    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Item({name!r})x{quantity}>'.format(name=self.type.name,quantity=self.quantity)


