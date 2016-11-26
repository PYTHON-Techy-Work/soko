# -*- coding: utf-8 -*-
"""Loan forms."""
from flask_wtf import Form
from wtforms import PasswordField, StringField, HiddenField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from soko.user.models import User
from wtforms.fields.html5 import DateField


class LoanForm(Form):
    """Register form."""

    name = StringField('Description',
                           validators=[DataRequired(), Length(min=1)])
    user = SelectField('User', coerce=int)
    created_on = DateField('Created On',validators=[DataRequired()])
    due_on = DateField('Due On',validators=[DataRequired()])
    total = IntegerField('Total',validators=[DataRequired()])
    paid = IntegerField('Paid',validators=[DataRequired()])


    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoanForm, self).__init__(*args, **kwargs)

    def validate(self):
        """Validate the form."""
        initial_validation = super(LoanForm, self).validate()
        if not initial_validation:
            return False
        return True
