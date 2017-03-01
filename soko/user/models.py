# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from flask_login import UserMixin

from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship
from soko.extensions import bcrypt

from soko.products.models import Cart


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_col('users', nullable=True)
    user = relationship('User', backref='roles')

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Role({name})>'.format(name=self.name)


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""
    __tablename__ = 'users'
    email = Column(db.String(80), unique=True, nullable=False)
    password = Column(db.String(128), nullable=True)
    password_reset = Column(db.Integer, nullable=True)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    phone_number = Column(db.String(15), nullable=True)
    profile_photo = Column(db.String(150), nullable=True)
    category = Column(db.String(30), nullable=True)
    user_type = Column(db.String(80), nullable=True)#company or individual
    business_name = Column(db.String(300), nullable=True)#company or individual
    business_branch = Column(db.String(300), nullable=True)  # company or individual
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)
    token = Column(db.String(100), nullable=False)
    photo = Column(db.String(300), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    region = Column(db.String(80), nullable=True)

    def __init__(self, email, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)
        print ("SET PASSWORD '" + str(password) + "'")

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    @property
    def cart_count(self):
        return Cart.query.filter_by(user=self.id).count()

    @property
    def full_name(self):
        """Full user name."""
        return '{0} {1}'.format(self.first_name, self.last_name, self.surname)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({username!r})>'.format(username=self.username)


class Document(SurrogatePK, Model):
    """an uploaded document."""

    __tablename__ = 'documents'
    name = Column(db.String(80), nullable=False)
    filename = Column(db.String(256), nullable=False)
    user_id = reference_col('users', nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    user = relationship('User', backref='documents')

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Document({name})>'.format(name=self.name)