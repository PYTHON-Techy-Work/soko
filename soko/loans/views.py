# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user

from soko.user.models import User, Document
from forms import LoanForm
from soko.utils import flash_errors
from soko.extensions import csrf_protect, bcrypt
from werkzeug.utils import secure_filename

from datetime import datetime

import os, time

from models import *

from flask import current_app as app

blueprint = Blueprint('loans', __name__, url_prefix='/loans', static_folder='../static')



@blueprint.route('/')
@login_required
def list():
    """List loans."""
    loans = Loan.query.all()

    return render_template('loans/list.html', loans=loans)

@blueprint.route('/edit/<uid>', methods=["GET", "POST"])
@login_required
def edit_loan(uid):

    if uid == "new":
        l = Loan("New Loan")
        db.session.add(l)
        db.session.commit()
        return redirect("/loans/edit/" + str(l.id))

    form = LoanForm(request.form, csrf_enabled=False)
    form.user.choices = [(g.id, g.email) for g in User.query.all()]
    loan = Loan.query.get(uid)

    if request.method == "POST":

        if form.validate_on_submit():
            loan.name = request.form.get("name")
            loan.total = request.form.get("total")
            loan.paid = request.form.get("paid")
            loan.user_id = request.form.get("user")
            loan.created_on = datetime.strptime(request.form.get("created_on"), "%Y-%m-%d")
            loan.due_on = datetime.strptime(request.form.get("due_on"), "%Y-%m-%d")
            db.session.commit()

            flash('Loan updated', 'success')
            return redirect("/loans")
        else:
            flash_errors(form)
            return render_template('loans/edit.html', form=form, loan=loan)

    else:
        return render_template('loans/edit.html', form=form, loan=loan)
