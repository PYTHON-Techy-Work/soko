from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, make_response, json
from flask_mail import Mail, Message


from werkzeug.utils import secure_filename

from soko.user.models import User, Document
from soko.transporter.models import Transporter, County, TransporterCurrentLocation, TransporterRatings
from soko.products.models import Product, ProductCategory, ProductType, ProductSubType, ProductRatings, Cart, Purchase, \
    ShoppingList, Delivery, Order, Earning, Trip, Payment
from soko.locations.models import Locations
from soko.loans.models import Loan
from soko.database import db
from soko.utils import flash_errors
from soko.extensions import csrf_protect, bcrypt, mail, geolocator
from math import sin, cos, atan2, sqrt, radians
from suds.client import Client as SudsClient

import os
import base64
import time
import uuid
import xmltodict
import string
import random
import suds.client
import datetime as dt

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')


# checking for the file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# checking for the image extensions
def guess_image_extension(fdata):
    if fdata.startswith("data:image/jpeg"):
        return "jpg"
    return "png"


# getting the list of all the users
@blueprint.route('/get_users', methods=['GET'])
def get_users():
    # Query the database and return all users
    users = User.query.all()
    try:
        results = jsonify({'status': 'success', 'data': users})
    except:
        results = jsonify({'status': 'failure', 'message': 'No users found in the database'})
    return make_response(results)


# registration api farmer, transporter, customer
@csrf_protect.exempt
@blueprint.route('/register', methods=['POST'])
def reg_user():
    data = request.json
    if "Transporter" in data["category"]:
        active = False
        first_name = data['first_name']
        last_name = data['last_name']
        business_name = ""
        business_branch = ""
        user_type = ""
    elif "Farmer" in data["category"]:
        active = False
        if "Business" in data["user_type"]:
            first_name = ""
            last_name = ""
            business_name = data['business_name']
            business_branch = data['business_branch']
            user_type = data['user_type']
        else:
            first_name = data['first_name']
            last_name = data['last_name']
            business_name = ""
            business_branch = ""
            user_type = ""
    else:
        active = True
        first_name = data['first_name']
        last_name = data['last_name']
        business_name = ""
        business_branch = ""
        user_type = ""

    is_admin = False
    token = ''
    region = County.query.filter_by(id=data["region"]).first()
    user = User(
        email=data['email'],
        password=data['password'],
        password_reset=0,
        first_name=first_name,
        last_name=last_name,
        phone_number=data['phone_number'],
        user_type=user_type,
        business_name=business_name,
        business_branch=business_branch,
        is_admin=is_admin,
        active=active,
        token=token,
        category=data['category'],
        region=region.name
    )
    try:
        db.session.add(user)
        db.session.commit()
        status = {'status': 'success', 'message': 'user registered successfully'}
        msg = Message("Welcome To Soko Mkononi",
                      sender="soko@tracom.co.ke",
                      recipients=[data['email']])
        msg.body = "You have successfully registered to soko mkononi as a  " + data['category']
        msg.html = "<b>Hi</b> " + data[
            'first_name'] + "<br/> <b>You have successfully registered to Soko Mkononi as a " + data[
                       'category'] + "</b>"
        msg.html = "Your email address is" + data['email'] + " and your password is " + data['password']+"."
        mail.send(msg)
    except Exception as e:
        status = {'status': 'failure', 'message': str(e)}
    db.session.close()
    return jsonify(status)


# get user profile
# update_profile api farmer, transporter, customer
@blueprint.route('/get_profile', methods=['GET'])
def get_profile():
    data = request.args
    try:
        user = User.query.filter_by(token=data['token']).first()
        user_data = {
            "email": user.email,
            "phone_number": user.phone_number,
            "photo": user.profile_photo,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        status = {'status': 'success', 'message': user_data}
    except Exception as e:
        status = {'status': 'failure', 'message': str(e)}
    db.session.close()
    return jsonify(status)


# update_profile api farmer, transporter, customer
@csrf_protect.exempt
@blueprint.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.json
    user = User.query.filter_by(token=data['token']).first()
    try:
        user.email = data['email']
        user.phone_number = data['phone_number']
        # user.profile_photo = data['profile_photo']
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        db.session.commit()
        status = {'status': 'success', 'message': 'user profile successfully updated'}
        msg = Message("Welcome To Soko Mkononi",
                      sender="soko@tracom.co.ke",
                      recipients=[data['email']])
        msg.body = "You have successfully Updated your profile a  " + user.category
        msg.html = "<b>Hi</b> " + user.first_name + "<br/> " \
                                                    "<b>You have successfully Updated your profile on Soko Mkononi as a " + user.category + \
                   "</b>"
        mail.send(msg)
    except Exception as e:
        status = {'status': 'failure', 'message': 'the user is already registered'}
    db.session.close()
    return jsonify(status)


# login_api
@csrf_protect.exempt
@blueprint.route('/login', methods=["POST"])
def login():
    data = request.json
    # print data
    email = data['email']
    password = data['password']
    registered_user = User.query.filter_by(email=email).first()
    if registered_user is None:
        status = {'status': 'failure', 'message': 'Invalid Email or password'}
    # elif registered_user.active is False:
    #     status = {'status': 'failure', 'message': 'Your documents have not yet been verified'}
    else:
        if bcrypt.check_password_hash(registered_user.password, password):
            registered_user.token = uuid.uuid4()
            db.session.add(registered_user)
            db.session.commit()
            status = {'status': 'success', 'message': 'welcome ' + registered_user.first_name,
                      'token': registered_user.token,
                      'email': registered_user.email, 'category': registered_user.category,
                      'active': registered_user.active,
                      'password_reset': registered_user.password_reset}
        else:
            status = {'status': 'failure', 'message': 'Invalid Email or password'}
    return jsonify(status)


# add transporter details #lorry, pick-up, van, truck, motorcycle
@csrf_protect.exempt
@blueprint.route('/add_transporter_details', methods=["POST"])
def add_transporter_details():
    data = request.json
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        try:
            transporter = Transporter(
                user_id=user.id,
                vehicle_type=data["vehicle_type"],
                vehicle_reg_no=data["vehicle_reg_no"],
                vehicle_color=data["vehicle_color"]
            )
            db.session.add(transporter)
            db.session.commit()
            status = {"status": "success", "message": "Data added successfully"}
        except Exception as e:
            status = {"status": "failure", "message": str(e)}
    else:
        status = {"status": "failure", "message": "Please enter the correct data"}
    db.session.close()
    return jsonify(status)


# add driver's licence for verification
@csrf_protect.exempt
@blueprint.route('/add_driver_licence', methods=["POST"])
def add_driver_licence():
    # data = request.json
    if request.get_json(force=True):
        data = request.get_json(force=True)
    else:
        data = request.form

    if "drivers_licence" not in data:
        return jsonify({'status': 'failure', 'message': 'you need to provide a drivers_licence'})

    drivers_licence = data["drivers_licence"]

    # need to de-base-64 the image, as it is passed as long string
    if "base64," in drivers_licence:
        drivers_licence_decoded = base64.decodestring(drivers_licence.partition("base64,")[2])
    else:
        drivers_licence_decoded = base64.decodestring(drivers_licence)

    # we don't have a filename, so let's make a random one
    filename = "upload_" + str(int(time.time())) + "." + guess_image_extension(drivers_licence)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    fp = open(path, 'wb')  # create a writable image and write the decoding result
    fp.write(drivers_licence_decoded)

    fp.close()
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        try:
            document = Document(
                name=data["name"],
                filename=path,
                user_id=user.id,
            )
            db.session.add(document)
            db.session.commit()
            status = {"status": "success", "message": "Driver's licence added successfully"}
        except Exception as e:
            status = {"status": "failure", "message": str(e)}
    else:
        status = {"status": "failure", "message": "Please add the correct data"}
    db.session.close()
    return jsonify(status)


# add id card for verification
@csrf_protect.exempt
@blueprint.route('/add_id_card', methods=["POST"])
def add_id_card():
    # data = request.json
    if request.get_json(force=True):
        data = request.get_json(force=True)
    else:
        data = request.form

    if "id_card" not in data:
        return jsonify({'status': 'failure', 'message': 'you need to provide a id_card'})

    id_card = data["id_card"]

    # need to de-base-64 the image, as it is passed as long string
    if "base64," in id_card:
        id_card_decoded = base64.decodestring(id_card.partition("base64,")[2])
    else:
        id_card_decoded = base64.decodestring(id_card)

    # we don't have a filename, so let's make a random one
    filename = "upload_" + str(int(time.time())) + "." + guess_image_extension(id_card)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    fp = open(path, 'wb')  # create a writable image and write the decoding result
    fp.write(id_card_decoded)

    fp.close()
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        try:
            document = Document(
                name=data["name"],
                filename=path,
                user_id=user.id,
            )
            db.session.add(document)
            db.session.commit()
            status = {"status": "success", "message": "Identity Card added successfully"}
        except Exception as e:
            status = {"status": "failure", "message": str(e)}
    else:
        status = {"status": "failure", "message": "Please add the correct data"}
    db.session.close()
    return jsonify(status)


# api for getting all the product categories
@blueprint.route('/get_product_categories', methods=["GET"])
def get_product_categories():
    ret = []
    product_categories = ProductCategory.query.all()
    for pt in product_categories:
        ret.append(pt.serialize())
    return jsonify(data=ret)


# api for getting all the product category
@blueprint.route('/get_product_category', methods=["GET"])
def get_product_category():
    ret = []
    product_categories = ProductCategory.query.all()
    for pt in product_categories:
        ret.append(pt.serialize())
    return jsonify(data=ret)


# api for getting the product type for a selected all the product category
@blueprint.route('/get_product_types', methods=["GET"])
def get_product_types():
    data = request.args
    ret = []
    product_types = ProductType.query.filter_by(product_category_id=data['id'])
    for pt in product_types:
        ret.append(pt.serialize())
    return jsonify(data=ret)


# api for getting all the product sub types
@blueprint.route('/get_product_sub_types', methods=["GET"])
def get_product_sub_types():
    data = request.args
    ret = []
    product_sub_types = ProductSubType.query.filter_by(product_type_id=data['id'])
    for pst in product_sub_types:
        ret.append(pst.serialize())
    return jsonify(data=ret)


# api for inserting a product type
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
    # if request.get_json(force=True):
    #     data = request.get_json(force=True)
    # else:
    #     data = request.form
    #
    # if "photo" not in data:
    #     return jsonify({'status': 'failure', 'message': 'you need to provide a photo'})
    #
    # photo = data["photo"]
    #
    # print photo
    #
    # # need to de-base-64 the image, as it is passed as long string
    # if "base64," in photo:
    #     photo_decoded = base64.decodestring(photo.partition("base64,")[2])
    # else:
    #     photo_decoded = base64.decodestring(photo)
    #
    # # we don't have a filename, so let's make a random one
    # filename = "upload_" + str(int(time.time())) + "." + guess_image_extension(photo)
    # path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #
    # fp = open(path, 'wb')  # create a writable image and write the decoding result
    # fp.write(photo_decoded)
    # fp.close()
    data = request.get_json(force=True)
    user = User.query.filter_by(token=data["token"]).first()
    user_id = user.id
    if user.id:
        if "product_sub_type_id" in data:
            subtypeid = data['product_sub_type_id']

        product_name = ProductSubType.query.filter_by(id=subtypeid).first()
        product = Product(
            name=product_name.name,
            product_category_id=product_name.product_category_id,
            product_type_id=product_name.product_type_id,
            product_sub_type_id=subtypeid,
            description=product_name.description,
            packaging=data['packaging'],
            price=data['price'],
            quantity=data['quantity'],
            photo=product_name.photo,
            user_id=user.id
        )
        try:
            db.session.add(product)
            db.session.commit()
            status = {'status': 'success', 'message': 'product added'}
        except Exception as e:
            status = {'status': 'failure', 'message': 'problem adding product'}
    db.session.close()
    return jsonify(status)


# api to get all the products
@blueprint.route('/get_products', methods=["GET"])
def get_products():
    data = request.args
    ret = []
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        if user:
            products = Product.query.all()
            for pt in products:
                ret.append(pt.serialize())
    return jsonify(data=ret)


# api to get my products merchant
@blueprint.route('/get_my_products', methods=["GET"])
def get_my_products():
    data = request.args
    ret = []
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        if user:
            for pt in Product.query.filter_by(user_id=user.id):
                ret.append(pt.serialize())
    return jsonify(data=ret)


# api to edit products
@csrf_protect.exempt
@blueprint.route('/edit_products', methods=["POST"])
def edit_products():
    data = request.json
    ret = []
    if data:
        user = User.query.filter_by(token=data["token"]).first()

    if user.id:
        product = Product.query.get(data["id"])
        product.price = data["price"]
        product.quantity = data["quantity"]
        db.session.commit()
        status = {'status': 'success', 'message': "product updated"}
    else:
        status = {'status': 'failure', 'message': 'error!'}

    return jsonify(status)


# delete a product
@blueprint.route('/delete_product', methods=["GET"])
def delete_product():
    data = request.args
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        try:
            product = Product.query.filter(Product.user == user.id)
            product.delete()
            status = {'status': 'success', 'message': 'product deleted'}
        except Exception as e:
            status = {'status': 'failure', 'message': str(e)}
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
    county = County(
        name=data['name']
    )
    try:
        db.session.add(county)
        db.session.commit()
        status = {'status': 'success', 'message': 'county added'}
    except Exception as e:
        status = {'status': 'failure', 'message': str(e)}
    db.session.close()
    return jsonify(status)


# get maps api
@csrf_protect.exempt
@blueprint.route('/post_maps', methods=["POST"])
def get_maps():
    data = request.json
    token = request.args
    user = User.query.filter_by(token=token["token"]).first()
    location = Locations.query.filter_by(user=user.id).first()
    try:
        if location:
            location.latitude = data['lat']
            location.longitude = data['lng']
            db.session.add(location)
            db.session.commit()
            status = {'status': 'success', 'message': 'location updated'}
        else:
            location = Locations(
                latitude=data['lat'],
                longitude=data['lng'],
                user=user.id
            )
            db.session.add(location)
            db.session.commit()
            status = {'status': 'success', 'message': 'location added'}
    except Exception as e:
        status = {'status': 'failure', 'message': str(e)}
    db.session.close()
    return jsonify(status)


# send maps api
@blueprint.route('/send_maps', methods=["GET"])
def send_maps():
    data = request.args
    ret = []
    try:
        user = User.query.filter_by(token=data["token"]).first()
        if user:
            locations = Locations.query.all()
            for pt in locations:
                ret.append(pt.serialize())
            status = {'message': 'success', 'data': ret}
    except Exception as e:
        status = {'message': 'failure', 'data': str(e)}
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
            product = Product.query.filter_by(id=data["product"]).first()
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

            except Exception as e:
                status = {'status': 'failure', 'message': 'problem adding product to cart'}
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
    db.session.close()
    return jsonify({'status': 'success', 'message': 'product removed from cart'})


@csrf_protect.exempt
@blueprint.route('/purchase_cart', methods=["POST"])
def purchase_cart():
    data = request.json
    delivery_status = "Pending"
    order_status = "Pending"
    transporter = 0
    if "token" not in request.json:
        status = {'status': 'failure', 'message': 'Error!'}
    else:
        user = User.query.filter_by(token=data["token"]).first()
        try:
            for cart in Cart.query.filter_by(user=user.id):
                # todo: do some stuff with the cart
                # add to 'purchases' table or something
                purchase = Purchase(
                    user=user.id,
                    product_id=cart.product_id,
                    quantity=cart.quantity,
                    total=cart.total
                )
                shopping_list = ShoppingList(
                    user_id=user.id,
                    product_id=cart.product_id,
                    quantity=cart.quantity
                )
                delivery = Delivery(
                    user_id=user.id,
                    product_id=cart.product_id,
                    transporter=transporter,
                    status=delivery_status,
                    total=cart.total,
                    lat=data["lat"],
                    lng=data["lng"],
                    quantity=cart.quantity
                )
                order = Order(
                    user_id=user.id,
                    delivery_id=delivery.id,
                    transporter=transporter,
                    status=order_status,
                    total=cart.total,
                    lat=data["lat"],
                    lng=data["lng"]
                )
                db.session.add(purchase)
                db.session.add(shopping_list)
                db.session.add(delivery)
                db.session.add(order)
                product = Product.query.get(cart.product_id)
                product.quantity = int(product.quantity) - int(purchase.quantity)
                db.session.delete(cart)
                db.session.commit()
            print("am here with success")
            status = {'status': 'success', 'message': 'Items successfully purchased!'}
        except Exception as e:
            print("am not here with success")
            status = {"status": "failure", "message": str(e)}
    db.session.close()
    return jsonify(status)


@blueprint.route('/get_purchases', methods=["GET"])
def get_purchase():
    data = request.args
    purchases = []
    if "token" not in data:
        return jsonify({'status': 'failure', 'message': 'Error!'})
    user = User.query.filter_by(token=data["token"]).first()
    if user:
        for purchase in Purchase.query.filter_by(user=user.id):
            purchases.append(purchase.serialize())
        status = {"status": "success", "message": purchases}
    else:
        status = {'status': 'failure', 'message': 'You have not purchased any items on soko mkononi'}
    return jsonify(status)


# add the product categories api
@csrf_protect.exempt
@blueprint.route('/add_product_categories', methods=["POST"])
def add_product_categories():
    data = request.json
    product_category = ProductCategory(
        name=data['name']
    )
    try:
        db.session.add(product_category)
        db.session.commit()
        status = {'status': 'success', 'message': 'product category added'}
    except Exception as e:
        status = {'status': 'failure', 'message': str(e)}
    db.session.close()
    return jsonify(status)


# add the product type api
@csrf_protect.exempt
@blueprint.route('/add_product_type', methods=["POST"])
def add_product_type():
    data = request.json
    product_type = ProductType(
        name=data['name'],
        product_category_id=data['product_category']
    )
    try:
        db.session.add(product_type)
        db.session.commit()
        status = {'status': 'success', 'message': 'product type added'}
    except Exception as e:
        status = {'status': 'failure', 'message': str(e)}
    db.session.close()
    return jsonify(status)


# add the product sub type api
@csrf_protect.exempt
@blueprint.route('/add_product_sub_type', methods=["POST"])
def add_product_sub_type():
    data = request.json
    product_sub_sub_type = ProductSubType(
        name=data['name'],
        description=data['description'],
        product_type_id=data['product_type'],
        product_category_id=data['product_category'],
        photo=data['photo']
    )
    try:
        db.session.add(product_sub_sub_type)
        db.session.commit()
        status = {'status': 'success', 'message': 'product sub sub type added'}
    except Exception as e:
        status = {'status': 'failure', 'message': str(e)}
    db.session.close()
    return jsonify(status)


@blueprint.route('/get_shopping_list', methods=["GET"])
def get_shopping_list():
    data = request.args
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        if user:
            ret = []
            ls = ShoppingList.query.filter_by(user_id=user.id)
            for ls in ShoppingList.query.filter_by(user_id=user.id):
                product = Product.query.filter_by(id=ls.product_id).first()
                ret.append(product.serialize())
            status = {"status": "success", "message": ret}
        else:
            status = {"status": "failure", "message": "No records found"}
    else:
        status = {"status": "failure", "message": "No records found"}
    return jsonify(status)


@csrf_protect.exempt
@blueprint.route('/remove_from_shopping_list', methods=["POST"])
def remove_from_shopping_list():
    data = request.json
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        try:
            shopping_list = ShoppingList.query.filter_by(user_id=user.id, product_id=data["id"]).first()
            shopping_list.delete()
            status = {'status': 'success', 'message': 'shopping list product deleted'}
        except Exception as e:
            status = {'status': 'failure', 'message': e}
    return jsonify(status)


# save faramer location
@csrf_protect.exempt
@blueprint.route('/get_farmer_location', methods=["POST"])
def get_farmer_location():
    data = request.json
    latitude = data["lat"]
    longitude = data["lng"]
    user = User.query.filter_by(token=data["token"]).first()
    if user:
        try:
            location = geolocator.reverse(str(latitude) + "," + str(longitude))
            farmer_address = FarmerAddress(
                user_id=user.id,
                primary_address=location.address,
                location=user.region
            )
            db.session.add(farmer_address)
            db.session.commit()
            status = {"status": "success", "message": location.address}
        except Exception as e:
            status = {"status": "failure", "message": str(e)}
    else:
        status = {"status": "failure", "message": "user not found"}
    db.session.close()
    return jsonify(status)


# get_transporter_current_location
@csrf_protect.exempt
@blueprint.route('/get_transporter_current_location', methods=["POST"])
def transporter_current_location():
    data = request.json
    if data:
        user = User.query.filter_by(token=data["token"]).first()
        try:
            tranporter_current_location = TransporterCurrentLocation(
                user_id=user.id,
                latitude=data["lat"],
                longitude=data["lng"]
            )
            db.session.add(tranporter_current_location)
            db.session.commit()
            status = {"status": "failure", "message": "Location added successfully"}
        except Exception as e:
            status = {"status": "failure", "message": str(e)}
    else:
        status = {"status": "failure", "message": "Pass the correct data"}
    db.session.close()
    return jsonify(status)


# sending the notifications to the drivers with the location
@csrf_protect.exempt
@blueprint.route('/available_orders', methods=["POST"])
def available_orders():
    ret = []
    data = request.json
    status = "Not Delivered"
    R = 6373.0
    lat1 = radians(float(data["lat"]))
    lon1 = radians(float(data["lng"]))
    user = User.query.filter_by(token=data["token"]).first()
    if user:
        try:
            for order in Order.query.filter_by(status=status):
                lat2 = radians(order.lat)
                lon2 = radians(order.lng)
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                distance = R * c
                if distance <= 5:
                    ret.append(order)
                status = {"status": "success", "message": distance, "lat": order.lat, "lng": order.lng}
        except Exception as e:
            status = {"status": "failure", "message": str(e)}
    else:
        status = {"status": "failure", "message": "No records found"}
    return jsonify(status)


# categories api
@blueprint.route('/get_categories', methods=["GET"])
def get_categories():
    ret = []
    data = []
    products_categories = ProductCategory.query.all()
    for ls in products_categories:
        ret.append(ls.serialize())
    data.append(ret)
    if ret:
        status = {"status": "success", "message": data}
    else:
        status = {"status": "failure", "message": "no records found"}
    return jsonify(status)


# generate random password for password reset api
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# forget password api
@csrf_protect.exempt
@blueprint.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json
    if data:
        new_password = id_generator()
        user = User.query.filter_by(email=data['email']).first()
        user.password = bcrypt.generate_password_hash(new_password)
        user.password_reset = 1
        db.session.commit()
        status = {"status": "success", "message": "your password has been reset", "new_password": new_password}
        msg = Message("Soko Mkononi Password Reset",
                      sender="soko@tracom.co.ke",
                      recipients=[data['email']])
        msg.body = "You have successfully reset your password"
        msg.html = "<b>Hi</b> " + user.first_name + "<br/> " \
                                                    "<b>You password has been reset successfully. Your new password is " + new_password + \
                   "</b>"
        mail.send(msg)
    else:
        status = {"status": "failure", "message": "problem resetting your password"}
    db.session.close()
    return jsonify(status)


# reset password api
@csrf_protect.exempt
@blueprint.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    if data:
        user = User.query.filter_by(token=data['token']).first()
        user.password = bcrypt.generate_password_hash(data['password'])
        user.password_reset = 0
        db.session.commit()
        status = {"status": "success", "message": "password changed"}
    else:
        status = {"status": "failure", "message": "problem resetting your password"}
    db.session.close()
    return jsonify(status)


# rate a product
@csrf_protect.exempt
@blueprint.route('/rate_product', methods=['POST'])
def rate_product():
    data = request.json
    print (data)
    if data:
        user = User.query.filter_by(token=data['token']).first()
        rate_product = ProductRatings(
            product_id=data["product_id"],
            user_id=user.id,
            rating=data["rating"],
            review=data["review"]
        )
        try:
            db.session.add(rate_product)
            db.session.commit()
            status = {"status": "success", "message": "product rated"}
        except Exception as e:
            status = {"status": "failure ", "message": str(e)}
        db.session.close()
        return jsonify(status)


# rate a transporter
@csrf_protect.exempt
@blueprint.route('/rate_transporter', methods=['POST'])
def rate_transporter():
    data = request.json
    try:
        user = User.query.filter_by(token=data['token']).first()
        rate_transporter = TransporterRatings(
            user_id=user.id,
            rating=data["rating"],
            review=data["review"]
        )
        db.session.add(rate_transporter)
        db.session.commit()
        status = {"status": "success", "message": "Transporter rated Successfully"}
    except Exception as e:
        status = {"status": "failure ", "message": str(e)}
    db.session.close()
    return jsonify(status)


# loans api --get my loans
@blueprint.route('/get_loan', methods=["GET"])
def get_loan():
    data = request.args
    ret = []
    user = User.query.filter_by(token=data["token"]).first()
    print(user.id)
    if user:
        loan = Loan.query.filter_by(user_id=user.id).first()
        loan_data = {"total": float(loan.total), "paid": float(loan.paid),
                     "name": loan.name, "due_date": loan.due_on, "status":loan.status}
        status = {"status": "success", "message": loan_data}
    else:
        status = {"status": "failure", "message": "no records found"}
    return jsonify(status)


# apply fo a loan
@csrf_protect.exempt
@blueprint.route('/apply_loan', methods=["POST"])
def apply_loan():
    data = request.json
    user = User.query.filter_by(token=data['token']).first()
    # check whether the user has an existing loan
    check_loan = Loan.query.filter_by(user_id=user.id, status=2).first()
    if check_loan:
        status = {"status": "failure", "message": "Please clear your existing loan to get another loan"}
    else:
        loan = Loan(
            name=user.first_name + " " + user.last_name,
            user_id=user.id,
            due_on=data["due_on"],
            total=data["total"],
            paid=0,
            status=2
        )
        db.session.add(loan)
        db.session.commit()
        status = {"status": "success", "message": "Loan application successful"}
    db.session.close()
    return jsonify(status)


# pay loan api
@csrf_protect.exempt
@blueprint.route('/pay_loan', methods=["POST"])
def pay_loan():
    data = request.json
    date = dt.datetime.now()
    print(data)
    user = User.query.filter_by(token=data['token']).first()
    # check whether the user has an existing loan
    get_loan = Loan.query.filter_by(user_id=user.id).first()
    print(get_loan.name)
    try:
        get_loan.paid = 1
        get_loan.total = data["amount"]
        get_loan.paid_on = date
        get_loan.status = 3
        db.session.commit()
        status = {"status": "success", "message": "Loan cleared"}
    except Exception as e:
        status = {"status": "failure", "message": str(e)}
    db.session.close()
    return jsonify(status)


# accept trip
@blueprint.route('/accept_trip', methods=["GET"])
def accept_trip():
    data = request.args
    status = 'Accepted'
    try:
        user = User.query.filter_by(token=data["token"]).first()
        order = Order.query.filter_by(id=data["order_id"]).first()
        trip = Trip(
            user_id=user.id,
            order_id=order.id,
            status=status,
            lat=order.lat,
            lng=order.lng
        )
        db.session.add(trip)
        status = {"status": "success","message": "Trip Accepted"}
    except Exception as e:
        status = {"status": "failure","message": str(e)}
    return jsonify(status)


# start trip
@blueprint.route('/start_trip', methods=["POST"])
def start_trip():
    data = request.json
    status = 'Started'
    try:
        user = User.query.filter_by(token=data["token"]).first()
        order = Order.query.filter_by(id=data["order_id"]).first()
        trip = Trip.query.filter_by(user_id=user.id,status='Accepted').first
        trip.status = status
        db.session.commit()
        status = {"status": "success","message": "Trip Started"}
    except Exception as e:
        status = {"status": "failure","message": str(e)}
    db.session.close()
    return jsonify(status)


# end trip
@blueprint.route('/end_trip', methods=["POST"])
def end_trip():
    data = request.json
    status = 'Finished'
    try:
        user = User.query.filter_by(token=data["token"]).first()
        order = Order.query.filter_by(id=data["order_id"]).first()
        trip = Trip.query.filter_by(user_id=user.id,status='Accepted').first
        trip.status = status
        db.session.commit()
        status = {"status": "success","message": "Trip Started"}
    except Exception as e:
        status = {"status": "failure","message": str(e)}
    db.session.close()
    return jsonify(status)


# reject_trip
@blueprint.route('/reject_trip', methods=["GET"])
def reject_trip():
    data = request.args
    status = 'Rejected'
    try:
        user = User.query.filter_by(token=data["token"]).first()
        order = Order.query.filter_by(id=data["order_id"]).first()
        trip = Trip(
            user_id=user.id,
            order_id=order.id,
            status=status,
            lat=order.lat,
            lng=order.lng
        )
        db.session.add(trip)
        db.session.commit()
        status = {"status": "success","message": "Trip rejected"}
    except Exception as e:
        status = {"status": "failure","message": str(e)}
    db.session.close()
    return jsonify(status)


# new orders merchant
@blueprint.route('/merchant_new_orders', methods=["GET"])
def merchant_new_orders():
    data = request.args
    my_order = []
    try:
        user = User.query.filter_by(token=data["token"]).first()
        product = Product.query.filter_by(user_id=user.id).first()
        for delivery in Delivery.query.filter_by(product_id=product.id):
            my_order.append(delivery.serialize())
        status = {"status": "success", "message": my_order}
    except Exception as e:
        status = {"status": "failure", "message": str(e)}
    db.session.close()
    return jsonify(status)


# earnings api transporter and farmer
@blueprint.route('/my_earnings', methods=["GET"])
def my_earnings_transporter():
    data = request.args
    my_earnings = []
    try:
        user = User.query.filter_by(token=data["token"]).first()
        for earning in Earning.query.filter_by(user_id=user.id):
            my_earnings.append(earning.serialize())
        status = {"status": "success","message": my_earnings}
    except Exception as e:
        status = {"status": "failure","message": str(e)}
    db.session.close()
    return jsonify(status)


# accept payments api
@csrf_protect.exempt
@blueprint.route('/accept_payments', methods=["POST"])
def accept_payments():
    data = request.json
    payment_method = data["payment_method"]
    try:
        user = User.query.filter_by(token=data["token"]).first()
        payment = Payment(
            user_id=user.id,
            order_id=data["order_id"],
            payment_method=payment_method
        )
        db.session.add(payment)
        db.session.commit()
        status = {"status":"success","message":"Payment made successfully"}
    except Exception as e:
        status = {"status": "success", "message": str(e)}
    db.session.close()
    return jsonify(status)


# will use this api to simulate the mpesa response
@blueprint.route('/current_oil_price', methods=['GET'])
def oil_current_price():
    # Get SOAP Service via suds
    url = 'http://www.pttplc.com/webservice/pttinfo.asmx?WSDL'
    client = SudsClient(url)
    # Execute CurrentOilPrice method of SOAP
    xml = client.service.CurrentOilPrice("EN")
    # Convert XML to dict
    res_dict = xmltodict.parse(xml)
    result = {}
    result['result'] = res_dict['PTT_DS']['DataAccess']
    # Convert dict to JSON
    return jsonify(**result)
