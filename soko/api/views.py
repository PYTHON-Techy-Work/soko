from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, make_response, json
from flask_login import login_required, login_user, logout_user
from flask_restful import reqparse
from sqlalchemy import orm

from werkzeug.utils import secure_filename

from soko.user.models import User
from soko.transporter.models import Transporter
from soko.farmer.models import Farmer
from soko.customer.models import Customer
from soko.products.models import Product, ProductType, ProductRatings
from soko.database import db
from soko.utils import flash_errors
from soko.extensions import csrf_protect, bcrypt

import os
from flask import current_app as app


import uuid
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])



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


# checking for the file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# api to add products
@csrf_protect.exempt
@blueprint.route('/add_products', methods=["POST"])
def add_products():
    photo = request.files.get("photo")
    print request.files.keys()
    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(path)
        print filename
        product = Product(
            name=request.form['name'],
            product_type_id=request.form['product_type_id'],
            description=request.form['description'],
            price=request.form['price'],
            quantity=request.form['quantity'],
            photo=filename
        )
    try:
        db.session.add(product)
        db.session.commit()
        status = {'status': 'success', 'message': 'product type added successfully'}
    except Exception, e:
        status = {'status': 'failure', 'message': 'there was a problem adding a new product'}
        print e
    db.session.close()
    return jsonify(status)
