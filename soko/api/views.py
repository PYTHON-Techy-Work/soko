from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, make_response
from flask_login import login_required, login_user, logout_user

from soko.user.models import User
from soko.utils import flash_errors

blueprint = Blueprint('api',__name__,url_prefix='/api/v1')

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
    return jsonify(ret={'users': users})


