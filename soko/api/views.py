from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, make_response, json
from flask_login import login_required, login_user, logout_user
from flask_restful import reqparse
from sqlalchemy import orm
from flask_mail import Mail, Message

from werkzeug.utils import secure_filename

from soko.user.models import User, Document
from soko.transporter.models import Transporter, County, TransporterCurrentLocation
from soko.farmer.models import Farmer, FarmerAddress
from soko.customer.models import Customer
from soko.products.models import Product, ProductCategory, ProductType, ProductSubType, ProductRatings, Cart, Purchase, ShoppingList, Order
from soko.locations.models import Locations
from soko.database import db
from soko.utils import flash_errors
from soko.extensions import csrf_protect, bcrypt, mail, geolocator
from math import sin, cos, atan2, sqrt, radians
from suds.client import Client

import os
import base64
import time
import uuid
import xmltodict

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
    else:
        active = True
    is_admin = False
    token = ''
    region = County.query.filter_by(id=data["region"]).first()
    print region.name
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        password_reset=0,
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone_number=data['phone_number'],
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
                      sender="from@example.com",
                      recipients=[data['email']])
        msg.body = "You have successfully registered to soko mkononi as a  "+data['category']
        msg.html = "<b>Hi</b> "+data['first_name']+"<br/> <b>You have successfully registered to soko mkononi as a "+data['category']+"</b>"
        mail.send(msg)
    except Exception, e:
        print e
        status = {'status': 'failure', 'message': str(e)}
    db.session.close()
    return jsonify(status)


# update_profile api farmer, transporter, customer
@csrf_protect.exempt
@blueprint.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.json
    print data
    user = User.query.filter_by(token=data['token']).first()
    print user
    try:
        user.username = data['username']
        user.email = data['email']
        user.phone_number = data['phone_number']
        user.profile_photo = data['profile_photo']
        user.region = data['region']
        db.session.commit()
        status = {'status': 'success', 'message': 'user profile successfully updated'}
        msg = Message("Welcome To Soko Mkononi",
                      sender="from@example.com",
                      recipients=[data['email']])
        msg.body = "You have successfully Updated your profile a  "+user.category
        msg.html = "<b>Hi</b> "+user.first_name+"<br/> " \
                                                "<b>You have successfully Updated your profile on Soko Mkononi as a "+user.category+\
                   "</b>"
        mail.send(msg)
    except Exception, e:
        print e
        status = {'status': 'failure', 'message': 'the user is already registered'}
    db.session.close()
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
    # elif registered_user.active is False:
    #     status = {'status': 'failure', 'message': 'Your documents have not yet been verified'}
    else:
        if bcrypt.check_password_hash(registered_user.password, password):
            registered_user.token = uuid.uuid4()
            db.session.add(registered_user)
            db.session.commit()
            status = {'status': 'success', 'message': 'welcome ' + registered_user.first_name,
                      'token': registered_user.token,
                      'username': registered_user.username, 'category': registered_user.category, 'active': registered_user.active,
                      'password reset': registered_user.password_reset}
        else:
            status = {'status': 'failure', 'message': 'Invalid Username or password'}
    return jsonify(status)


#add transporter details #lorry, pick-up, van, truck, motorcycle
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
        except Exception, e:
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
    print drivers_licence

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
        except Exception, e:
            status = {"status":"failure", "message": str(e)}
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
    print id_card

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
        except Exception, e:
            status = {"status":"failure", "message": str(e)}
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


# api for getting all the product types
@blueprint.route('/get_product_types', methods=["GET"])
def get_product_types():
    data = request.args
    print data
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
    print data
    user = User.query.filter_by(token=data["token"]).first()
    print user.id
    user_id = user.id
    if user.id:
        if "product_sub_type_id" in data:
            subtypeid = data['product_sub_type_id']

        product_name = ProductSubType.query.filter_by(id=subtypeid).first()
        print product_name.product_category_id
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
        except Exception, e:
            status = {'status': 'failure', 'message': 'problem adding product'}
            print e
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
    token = request.args
    print token
    if data:
        user = User.query.filter_by(token=token["token"]).first()
        print user
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
    data = request.json
    if "token" not in request.json:
        return jsonify({'status': 'failure', 'message': 'Error!'})

    user = User.query.filter_by(token=data["token"]).first()

    for cart in Cart.query.filter_by(user=user.id):
        # todo: do some stuff with the cart
        # add to 'purchases' table or something
        purchase = Purchase(
            user=user.id,
            product=cart.product,
            quantity=cart.quantity,
            total=cart.total,
        )
        shopping_list = ShoppingList(
            user_id=user.id,
            product_id=cart.product_id,
            quantity=cart.quantity,
            lat=data["lat"],
            lng=data["lng"]
        )
        order = Orders(
            user_id=user.id,
            product_id=cart.product_id,
            quantity=cart.quantity,
            lat=data["lat"],
            lng=data["lng"]
        )
        db.session.add(purchase)
        db.session.add(shopping_list)
        db.session.add(order)
        product = Product.query.get(cart.product_id)
        product.quantity = int(product.quantity) - int(purchase.quantity)
        db.session.delete(cart)
        db.session.commit()
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Items successfully purchased!'})


@blueprint.route('/get_purchases', methods=["GET"])
def get_purchase():
    data = request.args
    if "token" not in data:
        return jsonify({'status': 'failure', 'message': 'Error!'})
    print data
    user = User.query.filter_by(token=data["token"]).first()
    print user.id
    if user:
        for purchase in Purchase.query.filter_by(user=user.id):
             purchases =[purchase.serialize()]
        status = {"status":"success", "message": purchases}
    else:
        status = {'status': 'failure', 'message': 'You have not purchased any items on soko mkononi'}
    return jsonify(status)

# add the product categories api
@csrf_protect.exempt
@blueprint.route('/add_product_categories', methods=["POST"])
def add_product_categories():
        data = request.json
        print data
        product_category = ProductCategory(
            name=data['name']
        )
        try:
            db.session.add(product_category)
            db.session.commit()
            status = {'status': 'success', 'message': 'product category added'}
        except Exception, e:
            status = {'status': 'failure', 'message': str(e)}
            print e
        db.session.close()
        return jsonify(status)

# add the product type api
@csrf_protect.exempt
@blueprint.route('/add_product_type', methods=["POST"])
def add_product_type():
        data = request.json
        print data
        product_type = ProductType(
            name=data['name'],
            product_category_id=data['product_category']
        )
        try:
            db.session.add(product_type)
            db.session.commit()
            status = {'status': 'success', 'message': 'product type added'}
        except Exception, e:
            status = {'status': 'failure', 'message': str(e)}
            print e
        db.session.close()
        return jsonify(status)


# add the product sub type api
@csrf_protect.exempt
@blueprint.route('/add_product_sub_type', methods=["POST"])
def add_product_sub_type():
        data = request.json
        print data
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
        except Exception, e:
            status = {'status': 'failure', 'message': str(e)}
            print e
        db.session.close()
        return jsonify(status)


@blueprint.route('/get_shopping_list', methods=["GET"])
def get_shopping_list():
        data = request.args
        if data:
            user = User.query.filter_by(token=data["token"]).first()
            # print user.id
            if user:
                ret = []
                ls = ShoppingList.query.filter_by(user_id=user.id)
                for ls in ShoppingList.query.filter_by(user_id=user.id):
                    product = Product.query.filter_by(id=ls.product_id).first()
                    print product.name
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
        except Exception, e:
            print e
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
    print user.region
    if user:
        try:
            location = geolocator.reverse(str(latitude) + "," + str(longitude))
            print location.address
            farmer_address = FarmerAddress(
                user_id=user.id,
                primary_address=location.address,
                location=user.region
            )
            db.session.add(farmer_address)
            db.session.commit()
            status = {"status": "success", "message": location.address}
        except Exception, e:
            print e
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
        except Exception, e:
            status = {"status":"failure", "message": str(e)}
    else:
        status = {"status": "failure", "message": "Pass the correct data"}
    db.session.close()
    return jsonify(status)


@csrf_protect.exempt
@blueprint.route('/available_orders', methods=["POST"])
def available_orders():
    data = request.json
    R = 6373.0
    lat1 = radians(data["lat"])
    lon1 = radians(data["lng"])
    user = User.query.filter_by(token=data["token"]).first()
    if user:
        order = Order.query.filter_by(delivered=False)
        lat2 = order.lat
        lon2 = order.lng
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        status = {"status": "failure", "message": distance}
    else:
        status = {"status": "failure", "message": "No records found"}
    return jsonify(status)


# categories api
@blueprint.route('/get_categories', methods=["GET"])
def get_categories():
    # data = request.args
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


# accept payments api
@csrf_protect.exempt
@blueprint.route('/accept_payments', methods=["POST"])
def accept_payments():
    data = request.json
    return jsonify(data)

# will use this api to simulate the mpesa response
@blueprint.route('/current_oil_price', methods=['GET'])
def oil_current_price():
    # Get SOAP Service via suds
    url = 'http://www.pttplc.com/webservice/pttinfo.asmx?WSDL'
    client = Client(url)
    # Execute CurrentOilPrice method of SOAP
    xml = client.service.CurrentOilPrice("EN")
    # Convert XML to dict
    res_dict = xmltodict.parse(xml)
    result = {}
    result['result'] = res_dict['PTT_DS']['DataAccess']
    # Convert dict to JSON
    return jsonify(**result)


# forget password api
@blueprint.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json
    if data:
        user = User.query.filter_by(email=data['email']).first()