from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,DecimalField, SubmitField, TextField, BooleanField, IntegerField, SelectMultipleField, \
    SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from sqlalchemy_serializer import SerializerMixin


class FilterForm(FlaskForm):
    # typ = SelectField('')
    activity = SelectField('Активность', choices=[('all', 'Все'), ('кино', 'Кино'), ('прогр', 'Программирование'),
                                                    ('юмор', 'Юмор'), ('образ', 'Образование'),
                                                    ('курс', 'Курсы'), ('игр', 'Игры'), ('спорт', 'Спорт'),
                                                  ('медицин', 'Медицина') , ('дизайн', 'Дизайн')])

    submit = SubmitField('Show')

    result = None
