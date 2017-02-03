# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import Form
from wtforms import PasswordField, StringField, IntegerField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.fields.html5 import DateField


class EditProductTypeForm(Form):
    """Edit an item type form."""

    name = StringField('name', validators=[DataRequired(), Length(min=3, max=25)])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(EditProductTypeForm, self).__init__(*args, **kwargs)

    def validate(self):
        """Validate the form."""
        initial_validation = super(EditProductTypeForm, self).validate()
        if not initial_validation:
            return False
        return True

