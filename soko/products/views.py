# -*- coding: utf-8 -*-
"""Item views."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from soko.utils import flash_errors

blueprint = Blueprint('item', __name__, url_prefix='/products', static_folder='../static')

from .models import *
from .forms import *

@blueprint.route('/')
@login_required
def index():
    """List all products."""
    return render_template('products/index.html')

@blueprint.route('/types')
@login_required
def type_list():
    """List all categories."""
    products = ProductType.query.all()

    return render_template('products/type_list.html', products=products)


@blueprint.route('/types/<tid>', methods=["GET", "POST"])
@login_required
def type_edit(tid):
    """Register new item type."""
    form = EditProductTypeForm(request.form,
                            csrf_enabled=False,
                            obj=ProductType.query.get if tid != "new" else None)
    if form.validate_on_submit():
        if tid == "new":
            ProductType.create(name=form.name.data,descr=form.descr.data)
        else:
            obj = ProductType.query.get
            obj.update(name=form.name.data,descr=form.descr.data)

        flash('Product type saved', 'success')
        return redirect(url_for('product.type_list'))
    else:
        flash_errors(form)
    return render_template('products/type_edit.html', form=form)