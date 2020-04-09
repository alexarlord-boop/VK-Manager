from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, SubmitField, TextField, BooleanField, IntegerField, \
    SelectMultipleField, \
    SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from sqlalchemy_serializer import SerializerMixin


class EventFilterForm(FlaskForm):
    activity = SelectField('События', choices=[('all', 'Все'), (0, 'Прошедшие'),
                                              (1, 'Скоро будут')])

    submit = SubmitField('Show')
