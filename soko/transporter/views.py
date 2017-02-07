# -*- coding: utf-8 -*-
"""Transporter views."""
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user

from soko.user.models import User, Document
from soko.products.models import Product, ProductSubType, Purchase
from soko.user.forms import UpdateForm
from soko.utils import flash_errors
from soko.extensions import csrf_protect, bcrypt
from werkzeug.utils import secure_filename

import os, time


from flask import current_app as app

blueprint = Blueprint('transporter', __name__, url_prefix='/transporter', static_folder='../static')


@blueprint.route('/available')
@login_required
def available():
    """List members."""
    return render_template('transporter/available.html', items=Purchase.query.all())
