from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, make_response
from flask_login import login_required, login_user, logout_user

from soko.user.models import User
from soko.utils import flash_errors

from soko.extensions import csrf_protect



blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

users = [
    {
        'id': 1,
        'name': 'James',
        'email': 'njugunanduati@gmail.com'
    },
    {
        'id': 2,
        'name': 'Paul',
        'email': 'paul@gmail.com'
    }
]

@blueprint.route('/get_users', methods=['GET'])
def get_users():
    # Query the database and return all users
    users = User.query.all()
    try:
        results = jsonify({'status':'success','data':users})
    except:
        results = jsonify({'status':'failure','message':'No users found in the database'})
    return results

# @csrf.exempt
@blueprint.route('/register', methods=['POST'])
def reg_user():
    json_data = request.json
    user = User(
        user_type=json_data['user_type'],
        surname=json_data['surname'],
        first_name=json_data['first_name'],
        last_name=json_data['last_name'],
        email=json_data['email'],
        password=json_data['password'],
        category=json_data['category']
    )
    try:
        db.session.add(user)
        db.session.commit()
        status = 'success'
    except:
        status = 'the user is already registered'
    db.session.close()
    return jsonify({'result': status})
