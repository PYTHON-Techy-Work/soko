# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import Form
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class EditItemTypeForm(Form):
    """Edit an item type form."""

    name = StringField('name', validators=[DataRequired(), Length(min=3, max=25)])
    descr = StringField('descr', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(EditItemTypeForm, self).__init__(*args, **kwargs)

    def validate(self):
        """Validate the form."""
        initial_validation = super(EditItemTypeForm, self).validate()
        if not initial_validation:
            return False
        return True
