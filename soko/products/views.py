# -*- coding: utf-8 -*-
"""Item views."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from soko.utils import flash_errors
import time, os

from flask import current_app as app
from soko.extensions import csrf_protect
from flask_login import login_required, current_user

#from soko.user.models import User
from .models import ProductType, ProductCategory

blueprint = Blueprint('item', __name__, url_prefix='/products', static_folder='../static')

from .models import *
from .forms import *

@blueprint.route('/')
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
            photo = filename
            request.files["photo"].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

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






@blueprint.route('/browse', methods=["GET", "POST"])
@csrf_protect.exempt
def browse():

    if "addid" in request.form:
        product = Product.query.get(request.form.get("addid"))

        total = float(request.form.get("quantity")) * float(product.price)
        c = Cart(current_user.id, product.id, request.form.get("quantity"), total)

        db.session.add(c)
        db.session.commit()

        flash("Addeed to cart", "success")
        return redirect("/products/browse")

    """List all products."""
    products = Product.query.all()

    return render_template('products/browse.html', 
        products=products, title="All items for sale", product_categories=ProductCategory.query.all())


@blueprint.route('/cart', methods=["GET", "POST"])
@login_required
@csrf_protect.exempt
def cart():

    if "remove" in request.args:
        c = Cart.query.get(request.args.get("remove"))
        db.session.delete(c)
        flash("Removed from cart", "success")
        db.session.commit()
        return redirect("/products/cart")

    items = Cart.query.filter_by(user=current_user.id)

    total = 0
    for i in items:
        total += i.total

    return render_template('products/cart.html', items=items, total=total)




@blueprint.route('/pay', methods=["GET", "POST"])
@login_required
@csrf_protect.exempt
def pay():

    for cart in Cart.query.filter_by(user=current_user.id):
        purchase = Purchase(
            user=current_user.id,
            product=cart.product,
            quantity=cart.quantity,
            total=cart.total,
        )
        shopping_list = ShoppingList(
            user_id=current_user.id,
            product_id=cart.product_id,
            quantity=cart.quantity,
            lat=None,
            lng=None
        )
        db.session.add(purchase)
        db.session.add(shopping_list)
        product = Product.query.get(cart.product_id)
        product.quantity = int(product.quantity) - int(purchase.quantity)
        db.session.delete(cart)
        db.session.commit()
    db.session.commit()

    flash("Payment completed", "success")

    return redirect("/products/orders")



@blueprint.route('/orders', methods=["GET"])
@login_required
def orders():
    items = Purchase.query.filter_by(user=current_user.id)
    return render_template('products/orders.html', items=items)

