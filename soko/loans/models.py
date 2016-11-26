# -*- coding: utf-8 -*-
"""Loan models."""
import datetime as dt

from flask_login import UserMixin

from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship
from soko.extensions import bcrypt


class Loan(SurrogatePK, Model):
    """an uploaded document."""

    __tablename__ = 'loans'
    name = Column(db.String(80), nullable=False)
    user_id = reference_col('users', nullable=True)
    created_on = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    due_on = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    user = relationship('User', backref='loans')

    total = Column(db.Integer)
    paid = Column(db.Integer)
    total = Column(db.Integer)
    total = Column(db.Integer)


    def get_status_name(self):
        # TODO: figure out the status
        return "Unpaid"

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Loan({name})>'.format(name=self.name)