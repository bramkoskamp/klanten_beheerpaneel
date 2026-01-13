from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, RadioField
from wtforms.validators import DataRequired


class InvoiceForm(FlaskForm):
    customer = SelectField('Klant', coerce=int, validators=[DataRequired()])
    invoice_date = DateField('Factuur datum', validators=[DataRequired()])
    expiration_date = DateField('Verlooop datum', validators=[DataRequired()])
    service = SelectField('Dienst', coerce=int, validators=[DataRequired()])
    vat_rate = RadioField(
        'BTW tarief',
        choices=[(9, '9%'), (21, '21%')],
        coerce=int,
        default=21,
        validators=[DataRequired()]
    )
     
     
    def validate_price(self, field):
        # Replace comma with dot before conversion
        if isinstance(field.data, str):
            field.data = float(field.data.replace(',', '.'))