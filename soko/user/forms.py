# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import Form
from wtforms import PasswordField, StringField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from .models import User


class RegisterForm(Form):
    """Register form."""

    #username = StringField('Username',
    #                       validators=[DataRequired(), Length(min=3, max=25)])
   
    first_name = StringField('First Name',
                        validators=[DataRequired(), Length(min=3, max=40)])

    category = StringField('category',
                        validators=[DataRequired()])

    region = StringField('Region',
                        validators=[DataRequired()])

    last_name = StringField('Last Name',
                             validators=[DataRequired(), Length(min=1, max=40)])
    phone_number = StringField('Phone Number',
                             validators=[DataRequired(), Length(min=1, max=40)])
    email = StringField('Email',
                        validators=[DataRequired(), Email(), Length(min=6, max=40)])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=1, max=40)])
    confirm = PasswordField('Verify password',
                            [DataRequired(), EqualTo('password', message='Passwords must match')])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append('Email already registered')
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append('Email already registered')
            return False
        return True


class UpdateForm(Form):
    """Register form."""

    username = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=25)])
   
    first_name = StringField('First Name',
                        validators=[DataRequired(), Length(min=3, max=40)])

    category = StringField('category',
                        validators=[])

    region = StringField('Region',
                        validators=[DataRequired()])

    last_name = StringField('Last Name',
                             validators=[DataRequired(), Length(min=3, max=40)])
    phone_number = StringField('Phone Number',
                             validators=[DataRequired(), Length(min=6, max=40)])
    email = StringField('Email',
                        validators=[DataRequired(), Email(), Length(min=6, max=40)])
    password = PasswordField('Password')
    confirm = PasswordField('Verify password',
                            [EqualTo('password', message='Passwords must match')])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(UpdateForm, self).validate()
        if not initial_validation:
            return False
        return True
