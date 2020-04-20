from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, SubmitField, TextField, BooleanField, IntegerField
from wtforms.validators import DataRequired


class PageForm(FlaskForm):
    p_id = StringField(validators=[DataRequired()])
    p_typ = StringField(validators=[DataRequired()])
    submit = SubmitField('X')