# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user

from soko.user.models import User, Document
from forms import LoanForm
from soko.utils import flash_errors
from soko.extensions import csrf_protect, bcrypt
from werkzeug.utils import secure_filename
from soko.extensions import csrf_protect, bcrypt

from datetime import datetime

import os, time

from models import *

from flask import current_app as app

blueprint = Blueprint('loans', __name__, url_prefix='/loans', static_folder='../static')



@blueprint.route('/admin')
@login_required
def admin_list():
    """List loans."""
    loans = Loan.query.all()

    return render_template('loans/list.html', loans=loans, title="All Loans", is_admin=True)


@blueprint.route('/')
@login_required
def my_list():
    """List loans."""
    loans = Loan.query.filter_by(user=current_user)

    return render_template('loans/list.html', loans=loans, title="My Loans", is_admin=False)


@blueprint.route('/cancel/<uid>', methods=["GET", "POST"])
@login_required
def cancel_loan(uid):
    loan = Loan.query.get(uid)

    if loan.is_pending():
        db.session.delete(loan)
        db.session.commit()
        flash("Loan request deleted", "success")
    else:
        flash("Couldn't delete request", "danger")

    return redirect("/loans")



@blueprint.route('/pay', methods=["GET", "POST"])
@login_required
@csrf_protect.exempt
def pay_loan():
    loan = Loan.query.get(request.form.get("id"))

    if loan.is_approved():
        loan.paid += int(request.form.get("amount"))

        if loan.get_remaining() == 0:
            loan.status = 3 #paid

        db.session.commit()
        flash("Loan payment confirmed", "success")
    else:
        flash("Couldn't pay loan", "danger")

    return redirect("/loans")



@blueprint.route('/admin/edit/<uid>', methods=["GET", "POST"])
@blueprint.route('/edit/<uid>', methods=["GET", "POST"])
@login_required
def edit_loan(uid):

    is_admin = False
    if "admin" in request.url:
        is_admin = True

    if uid == "new":
        l = Loan("New Loan")
        db.session.add(l)
        db.session.commit()
        return redirect("/loans/edit/" + str(l.id))

    loan = Loan.query.get(uid)

    form = LoanForm(request.form, csrf_enabled=False)
    form.user.choices = [(g.id, g.email) for g in User.query.all()]
    form.status.data = str(loan.status or 0)

    if request.method == "POST":

        if form.validate_on_submit():
            loan.name = request.form.get("name")
            loan.total = request.form.get("total")
            loan.paid = request.form.get("paid")
            loan.user_id = request.form.get("user", default=current_user)
            loan.status = request.form.get("status")
            
            if "created_on" in request.form:
                loan.created_on = datetime.strptime(request.form.get("created_on"), "%Y-%m-%d")
            else:
                loan.created_on = datetime.now()

            loan.due_on = datetime.strptime(request.form.get("due_on"), "%Y-%m-%d")
            db.session.commit()

            flash('Loan updated', 'success')
            if is_admin:
                return redirect("/loans/admin")
            return redirect("/loans")
        else:
            flash_errors(form)

    return render_template('loans/edit.html', 
        form=form, 
        loan=loan, 
        is_admin=is_admin, 
        current_user=current_user)
