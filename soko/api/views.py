from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, make_response, json
from flask_login import login_required, login_user, logout_user
from flask_restful import reqparse
from sqlalchemy import orm

from werkzeug.utils import secure_filename

from soko.user.models import User
from soko.transporter.models import Transporter, County
from soko.farmer.models import Farmer
from soko.customer.models import Customer
from soko.products.models import Product, ProductType, ProductRatings, Cart, Purchase, ProductName
from soko.locations.models import Locations
from soko.database import db
from soko.utils import flash_errors
from soko.extensions import csrf_protect, bcrypt

import os
import base64
import time
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
        status = {'status': 'failure', 'message': 'the user is already registered'}
    db.session.close()
    print status
    return jsonify(status)


#login_api
@csrf_protect.exempt
@blueprint.route('/login', methods=["POST"])
def login():
    data = request.json
    print data
    username = data['username']
    password = data['password']
    registered_user = User.query.filter_by(username=username).first()
    if registered_user is None:
        status = {'status': 'failure', 'message': 'Invalid Username or password'}
    else:
        if bcrypt.check_password_hash(registered_user.password, password):
            registered_user.token = uuid.uuid4()
            db.session.add(registered_user)
            db.session.commit()
            status = {'status': 'success', 'message': 'welcome ' + registered_user.first_name,
                      'token': registered_user.token,
                      'username': registered_user.username, 'category': registered_user.category}
        else:
            status = {'status': 'failure', 'message': 'Invalid Username or password'}
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


# checking for the image extensions
def guess_image_extension(fdata):
    if fdata.startswith("data:image/jpeg"):
        return "jpg"
    return "png"


# api to add products
@csrf_protect.exempt
@blueprint.route('/add_products', methods=["POST"])
def add_products():
    if request.get_json(force=True):
        data = request.get_json(force=True)
    else:
        data = request.form

    if "photo" not in data:
        return jsonify({'status': 'failure', 'message': 'you need to provide a photo'})

    photo = data["photo"]

    print photo

    # need to de-base-64 the image, as it is passed as long string
    if "base64," in photo:
        photo_decoded = base64.decodestring(photo.partition("base64,")[2])
    else:
        photo_decoded = base64.decodestring(photo)

    # we don't have a filename, so let's make a random one
    filename = "upload_" + str(int(time.time())) + "." + guess_image_extension(photo)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    fp = open(path, 'wb')  # create a writable image and write the decoding result
    fp.write(photo_decoded)
    fp.close()

    user = User.query.filter_by(token=data["token"]).first()
    user_id = user.id

    if "product_type_id" in data:
        typeid = data['product_type_id']
    else:
        typeid = ProductType.query.first().id

    if photo:
        product = Product(
            name=data['name'],
            product_type_id=typeid,
            description=data['description'],
            price=data['price'],
            quantity=data['quantity'],
            photo=filename,
            user_id=user_id
        )
    try:
        db.session.add(product)
        db.session.commit()
        status = {'status': 'success', 'message': 'product added'}
    except Exception, e:
        status = {'status': 'failure', 'message': 'problem adding product'}
        print e
    db.session.close()
    return jsonify(status)


# api to get all the products
@blueprint.route('/get_products', methods=["GET"])
def get_products():
    ret = []
    products = Product.query.all()
    for pt in products:
        ret.append(pt.serialize())
    print ret
    return jsonify(data=ret)


# api to edit products
@csrf_protect.exempt
@blueprint.route('/edit_products', methods=["POST"])
def edit_products():
    data = request.json
    ret = []
    print data
    if data:
        user = User.query.filter_by(token=data["token"]).first()

    if user.id:
        product = Product.query.get(data["id"])
        ret.append(product.serialize())
        status = {'status': 'success', 'message': ret}
    else:
        status = {'status': 'failure', 'message': 'error!'}

    return jsonify(status)


# delete a product
@blueprint.route('/delete_product', methods=["GET"])
def delete_product():
    data = request.args
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        print user.id
        try:
            product = Product.query.filter(Product.user == user.id)
            product.delete()
            status = {'status': 'success', 'message': 'product deleted'}
        except Exception, e:
            print e
            status = {'status': 'failure', 'message': e}
    return jsonify(status)


# api for all the counties
@blueprint.route('/get_counties', methods=["GET"])
def get_counties():
    ret = []
    counties = County.query.all()
    for pt in counties:
        ret.append(pt.serialize())
    return jsonify(data=ret)


# api to add county
@csrf_protect.exempt
@blueprint.route('/add_county', methods=["POST"])
def add_county():
    data = request.json
    print data
    county = County(
        name=data['name']
    )
    try:
        db.session.add(county)
        db.session.commit()
        status = {'status': 'success', 'message': 'county added'}
    except Exception, e:
        status = {'status': 'failure', 'message': 'problem adding county'}
        print e
    db.session.close()
    return jsonify(status)


# get maps api
@csrf_protect.exempt
@blueprint.route('/post_maps', methods=["POST"])
def get_maps():
    data = request.json
    print data
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        location = Locations(
            user=user.id,
            latitude=data['lat'],
            longitude=data['lng']
        )
    try:
        db.session.add(location)
        db.session.commit()
        status = {'status': 'success', 'message': 'location added'}
    except Exception, e:
        status = {'status': 'failure', 'message': 'problem saving location'}
        print e
    db.session.close()
    return jsonify(status)


# send maps api
@blueprint.route('/send_maps', methods=["GET"])
def send_maps():
    data = request.args
    print data
    ret = []
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        if user:
            locations = Locations.query.all()
            for pt in locations:
                ret.append(pt.serialize())
            status = {'message': 'success', 'data': ret}
        else:
            status = {'message': 'failure', 'data': 'no riders at this time'}
    else:
        status = {'message': 'failure', 'data': 'no riders at this time'}
    return jsonify(status)


# get to cart
@blueprint.route('/get_cart_items', methods=["GET"])
def get_cart_items():
    data = request.args
    ret = []
    total = 0
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        if user:
            cart = Cart.query.filter_by(user=user.id)
            for pt in cart:
                ret.append(pt.serialize())
                total += pt.total
            print ret
            status = {'status': 'success', 'data': {"items": ret, "total": float(total)}}
        else:
            status = {'status': 'failure', 'message': 'Error!'}
    return jsonify(status)


# add to cart
@csrf_protect.exempt
@blueprint.route('/add_to_cart', methods=["POST"])
def add_to_cart():
    data = request.json
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        if user:
            product = Product.query.filter_by(id=data["product"]).first();
            print product.price
            cart = Cart(
                user=user.id,
                product_id=data['product'],
                quantity=data['quantity'],
                total=data['quantity'] * product.price
            )
            try:
                db.session.add(cart)
                db.session.commit()
                status = {'status': 'success', 'message': str(data['quantity']) + ' items added to cart'}

            except Exception, e:
                status = {'status': 'failure', 'message': 'problem adding product to cart'}
                print e
            db.session.close()
        else:
            status = {'status': 'failure', 'message': 'Error!'}
    else:
        status = {'status': 'failure', 'message': 'Error!'}
    return jsonify(status)



# add to cart
@csrf_protect.exempt
@blueprint.route('/remove_from_cart', methods=["POST"])
def remove_from_cart():
    
    if "token" not in request.json or "cid" not in request.json:
        return jsonify({'status': 'failure', 'message': 'Error!'})

    user = User.query.filter_by(token=request.json["token"]).first()

    if not user:
        return jsonify({'status': 'failure', 'message': 'Error!'})

    cid = Cart.query.get(request.json["cid"])

    if not cid or cid.user != user.id:
        return jsonify({'status': 'failure', 'message': 'Couldn\'t find cart item'})

    db.session.delete(cid)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'product removed from cart'})


@csrf_protect.exempt
@blueprint.route('/purchase_cart', methods=["POST"])
def purchase_cart():
    
    if "token" not in request.json:
        return jsonify({'status': 'failure', 'message': 'Error!'})

    user = User.query.filter_by(token=request.json["token"]).first()

    for cart in Cart.query.filter_by(user=user.id):
        # todo: do some stuff with the cart
        # add to 'purchases' table or somethign
        purchase = Purchase(
            user=user.id,
            product=cart.product,
            quantity=cart.quantity,
            total=cart.total,
        )
        db.session.add(purchase)
        db.session.delete(cart)
        db.session.commit()

    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Items successfully purchased!'})


@blueprint.route('/get_product_name', methods=["GET"])
def get_product_name():
        data = request.args
        print data
        ret = []
        if data:
            user = User.query.filter_by(token=data["token"]).first()
            if user:
                productname = ProductName.query.all()
                for pt in productname:
                    ret.append(pt.serialize())
                status = {'message': 'success', 'data': ret}
            else:
                status = {'message': 'failure', 'data': 'no product_names available on the system'}
        else:
            status = {'message': 'failure', 'data': 'no product_names available on the system'}
        return jsonify(status)


@csrf_protect.exempt
@blueprint.route('/add_product_name', methods=["POST"])
def add_product_name():
        data = request.form
        print data['photo']
        if data:
            product = ProductName(
                name=data['name'],
                description=data['description'],
                photo=data['photo']
            )
        try:
            db.session.add(product)
            db.session.commit()
            status = {'status': 'success', 'message': 'product name added'}
        except Exception, e:
            status = {'status': 'failure', 'message': 'problem adding product name'}
            print e
        db.session.close()
        return jsonify(status)


