from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, make_response, json
from flask_login import login_required, login_user, logout_user
from flask_restful import reqparse
from sqlalchemy import orm

from soko.user.models import User
from soko.transporter.models import Transporter
from soko.farmer.models import Farmer
from soko.customer.models import Customer
from soko.products.models import Product, ProductType, ProductRatings
from soko.database import db
from soko.utils import flash_errors
from soko.extensions import csrf_protect, bcrypt

import uuid

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')


@blueprint.route('/get_users', methods=['GET'])
def get_users():
    # Query the database and return all users
    users = User.query.all()
    try:
        results = jsonify({'status': 'success', 'data': users})
    except:
        results = jsonify({'status': 'failure', 'message': 'No users found in the database'})
    return make_response(results)


# registetation api farmer, transporter, customer
@csrf_protect.exempt
@blueprint.route('/register', methods=['POST'])
def reg_user():
    active = 'Yes'
    is_admin = 'No'
    token = ''
    data = request.json
    print data
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone_number=data['phone_number'],
        is_admin=is_admin,
        active=active,
        token=token,
        category=data['category'],
        region=data['region']
    )
    try:
        db.session.add(user)
        db.session.commit()
        status = {'status': 'success', 'message': 'user registered successfully'}
        print status
    except:
        status ={'status': 'failure', 'message': 'the user is already registered'}
    db.session.close()
    print status
    return jsonify(status)


# login api
@csrf_protect.exempt
@blueprint.route('/login', methods=["POST"])
def login():
    data = request.json
    print data
    username = data['username']
    password = data['password']
    registered_user = User.query.filter_by(username=username).first()
    if registered_user is None:
        status = {'status': 'failure', 'message': 'Username does not exist. Register'}
    else:
        if bcrypt.check_password_hash(registered_user.password, password):
            registered_user.token = uuid.uuid4()
            db.session.add(registered_user)
            db.session.commit()
            userdata = {'username': registered_user.username, 'token': registered_user.token,
                        'category': registered_user.category}
            status = {'status': 'success', 'message': userdata}
        else:
            status = {'status': 'failure', 'message': 'Password is invalid'}

    return jsonify(status)


# api for all the product types
@blueprint.route('/get_product_types', methods=["GET"])
def get_product_types():
    ret = []
    product_types = ProductType.query.all()
    for pt in product_types:
        ret.append(pt.serialize())
    return jsonify(data=ret)


@csrf_protect.exempt
@blueprint.route('/insert_product_type', methods=["POST"])
def put_product_types():
    data = request.json
    product_type = ProductType(
        name=data['name']
    )
    try:
        db.session.add(product_type)
        db.session.commit()
        status = {'status': 'success', 'message': 'product type added successfully'}
    except:
        status = 'the product type  is already registered'
    db.session.close()
    return jsonify({'result': status})

# api to add products
@csrf_protect.exempt
@blueprint.route('/add_products', methods=["POST"])
def add_products():
    data = request.json
    print data
    product = Product(
        name=data['name'],
        type=data['type'],
        description=data['description'],
        price=data['price'],
        quantity=data['quantity'],
        photo=data['photo']
    )
    try:
        db.session.add(product)
        db.session.commit()
        status = {'status': 'success', 'message': 'product type added successfully'}
    except:
        status = 'the product type  is already registered'
    db.session.close()
    return jsonify({'result': status})
