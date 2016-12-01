# -*- coding: utf-8 -*-
"""Item views."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from soko.utils import flash_errors
import time, os

from flask import current_app as app

from flask_login import login_required, current_user

from soko.user.models import User
from .models import ProductType

blueprint = Blueprint('item', __name__, url_prefix='/products', static_folder='../static')

from .models import *
from .forms import *

@blueprint.route('/')
@login_required
def index():
    """List all products."""
    products = Product.query.filter_by(user_id=current_user.id)

    return render_template('products/index.html', products=products, title="My items for sale")


@blueprint.route('/admin')
@login_required
def admin_index():
    """List all products."""
    products = Product.query.all()

    return render_template('products/index.html', products=products, title="All items for sale")



@blueprint.route('/admin/edit/<pid>', methods=["GET", "POST"])
@login_required
def item_edit_admin(pid):

    """Register new item type."""
    form = EditProductForm(request.form,
                            csrf_enabled=False)
    form.user_id.choices = [(g.id, g.email) for g in User.query.all()]
    form.product_type_id.choices = [(g.id, g.name) for g in ProductType.query.all()]

    obj = None
    if pid != "new":
        obj = Product.query.get(pid)

    if form.validate_on_submit():
        photo = None

        if "photo" in request.files and request.files["photo"].filename:
            filename = "upload_" + str(int(time.time())) + request.files["photo"].filename
            photo = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            request.files["photo"].save(photo)

        if pid == "new":
            Product.create(name=form.name.data,
                            description=form.description.data,
                            price=form.price.data,
                            quantity=form.quantity.data,
                            product_type_id=form.product_type_id.data,
                            user_id=form.user_id.data,
                            photo=photo)
        else:
            if not photo:
                photo = obj.photo

            obj.update(name=form.name.data,
                            description=form.description.data,
                            price=form.price.data,
                            quantity=form.quantity.data,
                            product_type_id=form.product_type_id.data,
                            user_id=form.user_id.data,
                            photo=photo)

        flash('Item saved', 'success')
        return redirect(url_for('item.admin_index'))
    else:
        flash_errors(form)
        
    return render_template('products/product_edit.html', form=form, item=obj)



@blueprint.route('/admin/types')
@login_required
def admin_type_list():
    """List all categories."""
    products = ProductType.query.all()
    return render_template('products/type_list.html', products=products, title="All categories")


@blueprint.route('/admin/types/<tid>', methods=["GET", "POST"])
@login_required
def type_edit(tid):
    """Register new item type."""
    form = EditProductTypeForm(request.form,
                            csrf_enabled=False,
                            obj=ProductType.query.get if tid != "new" else None)
    obj = None
    if tid != "new":
        obj = ProductType.query.get(tid)

    if form.validate_on_submit():
        if tid == "new":
            ProductType.create(name=form.name.data)
        else:
            obj.update(name=form.name.data)

        flash('Product category saved', 'success')
        return redirect(url_for('item.admin_type_list'))
    else:
        flash_errors(form)
        
    return render_template('products/type_edit.html', form=form, item=obj)