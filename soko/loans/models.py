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
    due_on = Column(db.DateTime, nullable=False)
    user = relationship('User', backref='loans')
    total = Column(db.Integer)
    paid = Column(db.Integer)
    status = Column(db.Integer)

    def get_status_name(self):
        # TODO: figure out the status
        if not self.status:
            return "Pending"
        
        elif self.status == 1:
            return "Denied"

        elif self.status == 2:
            return "Unpaid"

        elif self.status == 3:
            return "Paid"

        return "Unknown (" + str(self.status) + ")"

    def is_approved(self):
        return self.status in [2, 3]

    def is_denied(self):
        return self.status in [1]

    def is_pending(self):
        return not self.status 

    def is_paid(self):
        return self.paid >= self.total

    def get_remaining(self):
        if not self.total:
            return 0

        if not self.paid:
            return self.total


        r = self.total - self.paid

        if r > 0:
            return r

        return 0

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    # def __repr__(self):
    #     """Represent instance as a unique string."""
    #     return '<Loan({name})>'.format(name=self.name)

    def serialize(self):
        return {
            "id": self.user_id,
            "name": self.name,
            "due_on": self.due_on,
            "amount paid": self.paid,
            "total": float(self.total),
            "status": self.status,
            "created_at":self.created_on
        }