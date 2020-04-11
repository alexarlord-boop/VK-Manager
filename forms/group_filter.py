from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, SubmitField, TextField, BooleanField, IntegerField, \
    SelectMultipleField, \
    SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from sqlalchemy_serializer import SerializerMixin


class GroupFilterForm(FlaskForm):
    activity = SelectField('Доступ', choices=[('all', 'Все'), ('Открытая группа', 'Открытая группа'),
                                              ('Закрытая группа', 'Закрытая группа')])

    submit = SubmitField('Show')
