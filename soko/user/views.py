# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user

from soko.user.models import User, Document
from soko.user.forms import UpdateForm
from soko.utils import flash_errors
from soko.extensions import csrf_protect, bcrypt
from werkzeug.utils import secure_filename

import os, time


from flask import current_app as app

blueprint = Blueprint('user', __name__, url_prefix='/users', static_folder='../static')


@blueprint.route('/')
@login_required
def members():
    """List members."""

    if "category" in request.args:
        users = User.query.filter_by(category=request.args.get("category"))
    else:
        users = User.query.all()

    return render_template('users/members.html', users=users)

@blueprint.route('/edit/<uid>', methods=["GET", "POST"])
@login_required
def edit_user(uid):

    if uid == "me":
        user = current_user
    else:
        user = User.query.get(uid)

    # re-use most of the register form here
    form = UpdateForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        user.update(username=form.username.data, email=form.email.data, 
            active=True, 
            first_name=form.first_name.data,
            last_name=form.last_name.data, phone_number=form.phone_number.data,
            region=form.region.data)

        if form.password.data:
            user.update(password=form.password)

        flash('Profile updated', 'success')
        return redirect("/users/edit/" + str(uid))
    else:
        flash_errors(form)
    return render_template('users/profile.html', form=form, user=user)

def allowed_file(fn):
    return True #TODO

@blueprint.route('/documents/upload', methods=["GET", "POST"])
@login_required
@csrf_protect.exempt
def upload_document():

    if request.method == "GET":
        return render_template('users/upload.html')

    file = request.files.get("file")

    if file and allowed_file(file.filename):
        filename = str(int(time.time())) + "_" + secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        d = Document(file.filename)
        d.update(filename=path, user_id=current_user.id)

        flash("Uploaded file", "success")
    else:
        flash("error uploading file", "danger")

    return redirect("/users/documents/upload")

@blueprint.route('/documents/get/<fid>/<fname>', methods=["GET"])
@login_required
def download_document(fid, fname):
    doc = Document.query.get(fid)
    return send_file(doc.filename)



@blueprint.route('/documents', methods=["GET"])
@login_required
def view_documents():

    if request.method == "GET":
        return render_template('users/documents.html', documents=Document.query.all())






@blueprint.route('/dashboard', methods=["GET"])
@login_required
def dashboard():
    if request.method == "GET":
        return render_template('users/dashboard.html')



@blueprint.route('/locations/map', methods=["GET"])
@login_required
def locations_map():
    if request.method == "GET":
        return render_template('users/locations_map.html')

