from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, make_response, json
from flask_login import login_required, login_user, logout_user
from flask_restful import reqparse

from soko.user.models import User
from soko.utils import flash_errors
from soko.extensions import csrf_protect

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


@csrf_protect.exempt
@blueprint.route('/register', methods=['POST'])
def reg_user():
    parser = reqparse.RequestParser()
    parser.add_argument('surname', type=int, location='form')
    parser.add_argument('first_name', type=int, location='form')
    parser.add_argument('last_name', type=int, location='form')
    parser.add_argument('email', type=int, location='form')
    parser.add_argument('password', type=int, location='form')
    parser.add_argument('category', type=int, location='form')
    args = parser.parse_args()
    try:
        db.session.add(args)
        db.session.commit()
        status = 'success'
    except:
        status = 'the user is already registered'
    db.session.close()
    return jsonify({'result': status})
