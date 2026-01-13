from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, TextAreaField
from wtforms.validators import DataRequired


class ServiceForm(FlaskForm):
    name = StringField('naam', validators=[DataRequired()])
    price = FloatField('Prijs', validators=[DataRequired()])
    description = TextAreaField('Beschrijving', validators=[DataRequired()])