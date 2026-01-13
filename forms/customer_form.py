from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class CustomerForm(FlaskForm):
    full_name = StringField('Volledige naam', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    phone_number = StringField('Telefoonnummer', validators=[DataRequired()])
    adress = StringField('Adress', validators=[DataRequired()])
