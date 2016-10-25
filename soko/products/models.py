import datetime as dt

from soko.database import Column, Model, SurrogatePK, db, reference_col, relationship


class Product(SurrogatePK, Model):
    """A Products of the app."""
    __tablename__ = 'products'
    name = Column(db.String(80), nullable=False)
    farmer = relationship('Farmer')
    product_type = relationship('ProductType')
    description = Column(db.String(80), nullable=False)
    price = Column(db.Integer, nullable=False)
    quantity = Column(db.String(80), nullable=False)
    photo = Column(db.String(80), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name, farmer, product_type, description, price, quantity, photo):
        self.name = name
        self.farmer = farmer
        self.product_type = product_type
        self.description = description
        self.price = price
        self.quantity = quantity
        self.photo = photo

    def __repr__(self):
        return '<Product %r>' % self.name + self.farmer + self.description + self.price + self.quantity


class ProductType(SurrogatePK, Model):
    __tablename__ = 'product_types'
    name = Column(db.String(80), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Product %r>' % self.user


class ProductRatings(SurrogatePK, Model):
    __tablename__ = 'product_ratings'
    product = relationship('Product')
    description = Column(db.String(80), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, product, description):
        self.product = product
        self.description = description

    def __repr__(self):
        return '<Product %r>' % self.user + self.description


class ProductReviews(SurrogatePK, Model):
    __tablename__ = 'product_reviews'
    product = Column(db.Integer, nullable=True)
    review = Column(db.Text, nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, product, review):
        self.product = product
        self.review = review

    def __repr__(self):
        return '<Product Review %r>' % self.product + self.review
