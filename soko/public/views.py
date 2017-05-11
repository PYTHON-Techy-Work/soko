# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user

from soko.extensions import login_manager
from soko.public.forms import LoginForm
from soko.user.forms import RegisterForm
from soko.user.models import User
from soko.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.query.get(int(user_id))


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    return redirect("/products")


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """Home page."""
    if current_user.is_authenticated():
        return redirect("/")

    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash('You are logged in.', 'success')
            redirect_url = request.args.get("next") or "/"
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return redirect("/")


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect("/")


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        User.create(email=form.email.data, 
            password=form.password.data, active=True, token="(not set)",
            category=form.category.data, first_name=form.first_name.data,
            last_name=form.last_name.data, phone_number=form.phone_number.data,
            region=form.region.data)
        flash('Thank you for registering. You can now log in.', 'success')
        return redirect("/")
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route('/about/')
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template('public/about.html', form=form)
