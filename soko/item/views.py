# -*- coding: utf-8 -*-
"""Item views."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from soko.utils import flash_errors

blueprint = Blueprint('item', __name__, url_prefix='/items', static_folder='../static')

from .models import *
from .forms import *

@blueprint.route('/')
@login_required
def index():
    """List all items."""
    return render_template('items/index.html')

@blueprint.route('/types')
@login_required
def type_list():
    """List all categories."""
    items = ItemType.query.all()

    return render_template('items/type_list.html', items=items)


@blueprint.route('/types/<tid>', methods=["GET", "POST"])
@login_required
def type_edit(tid):
    """Register new item type."""
    form = EditItemTypeForm(request.form, 
                            csrf_enabled=False,
                            obj=ItemType.query.get(tid) if tid != "new" else None)
    if form.validate_on_submit():
        if tid == "new":
            ItemType.create(name=form.name.data,descr=form.descr.data)
        else:
            obj = ItemType.query.get(tid)
            obj.update(name=form.name.data,descr=form.descr.data)

        flash('Item type saved', 'success')
        return redirect(url_for('item.type_list'))
    else:
        flash_errors(form)
    return render_template('items/type_edit.html', form=form)