# -*- coding: utf-8 -*-
"""Item views."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from soko.utils import flash_errors
import time, os

from flask import current_app as app
from soko.extensions import csrf_protect
from flask_login import login_required, current_user

from .models import ProductType, ProductCategory, Order

blueprint = Blueprint('item', __name__, url_prefix='/products', static_folder='../static')

from .models import *
from .forms import *

@blueprint.route('/')
def index():
    return render_template('products/home.html', items=ProductSubType.query.limit(20))


@blueprint.route('/admin')
@login_required
def admin_index():
    """List all products."""
    products = Product.query.all()

    return render_template('products/index.html', products=products, title="All items for sale", is_admin=True)


@blueprint.route('/mine')
@login_required
def my_products():
    """List all products."""
    products = Product.query.filter_by(user_id=current_user.id)

    return render_template('products/index.html', 
        products=products, title="My items for sale", is_admin=False)



@blueprint.route('/admin/edit/<pid>', methods=["GET", "POST"])
@blueprint.route('/mine/edit/<pid>', methods=["GET", "POST"])
@login_required
def item_edit(pid):

    from soko.user.models import User

    is_admin = request.url.find("mine") == -1

    obj = None
    if pid != "new":
        obj = Product.query.get(pid)

    if request.method == "POST":
        photo = None

        if "photo" in request.files and request.files["photo"].filename:
            filename = "upload_" + str(int(time.time())) + request.files["photo"].filename
            photo = filename
            request.files["photo"].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        pc = ProductCategory.query.get(request.form.get("category_id"))
        pt = ProductType.query.get(request.form.get("product_type_id"))
        pst = ProductSubType.query.get(request.form.get("product_sub_type_id"))

        if pid == "new":
            Product.create(name=pst.name,
                            description=pst.description,
                            price=request.form.get("price"),
                            quantity=request.form.get("quantity"),
                            product_type_id=pt.id,
                            product_category_id=pc.id,
                            product_sub_type_id=pst.id,
                            user_id=request.form.get("user_id"),
                            photo=pst.photo,
                            packaging="")
        else:
            obj.update(name=pst.name,
                            description=pst.description,
                            price=request.form.get("price"),
                            quantity=request.form.get("quantity"),
                            product_type_id=pt.id,
                            product_category_id=pc.id,
                            product_sub_type_id=pst.id,
                            user_id=request.form.get("user_id"),
                            photo=pst.photo,
                            packaging="")

        flash('Item saved', 'success')

        if is_admin:
            return redirect(url_for('item.admin_index'))
        else:
            return redirect("/products/mine")
    
        
    return render_template('products/product_edit.html', 
        item=obj, categories=ProductCategory.query.all(),
        users=User.query.all(),
        is_admin=is_admin)



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

    if "addid" in request.args:
        if not current_user.is_authenticated:
            flash("You need to be logged in to do that!", "danger")
            return redirect("/products/browse")

        product = Product.query.get(request.args.get("addid"))

        total = float(request.args.get("quantity")) * float(product.price)
        c = Cart(current_user.id, product.id, request.args.get("quantity"), total)

        db.session.add(c)
        db.session.commit()

        flash("Added to cart", "success")
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
            product_id=cart.product_id,
            quantity=cart.quantity,
            total=cart.total,
        )
        shopping_list = ShoppingList(
            user_id=current_user.id,
            product_id=cart.product_id,
            quantity=cart.quantity,
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

@blueprint.route('/sold', methods=["GET"])
@login_required
def sold():
    items = []

    for p in Purchase.query.all():
        if p.product.user_id == current_user.id:
            items.append(p)

    return render_template('products/sales.html', items=items)

