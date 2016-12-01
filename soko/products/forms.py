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



class EditProductForm(Form):
    """Edit an item type form."""

    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=25)])
    description = StringField('Description', validators=[DataRequired(), Length(min=3, max=25)])
    price = IntegerField('Price', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    #created_at = DateField('Created On',validators=[])
    user_id = SelectField('User', coerce=int)
    product_type_id = SelectField('Category', coerce=int)
    photo = FileField("Photo")

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(EditProductForm, self).__init__(*args, **kwargs)

    def validate(self):
        """Validate the form."""
        initial_validation = super(EditProductForm, self).validate()
        if not initial_validation:
            return False
        return True
