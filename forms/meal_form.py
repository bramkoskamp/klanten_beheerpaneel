from flask_wtf import FlaskForm
from wtforms import FileField, FloatField, StringField, ValidationError
from wtforms.validators import DataRequired, Length, NumberRange


class MealForm(FlaskForm):
    description = StringField('description', validators=[DataRequired(), Length(min=4, max=40, message='This should be between 4 and 40 characters')])
    price = FloatField('price', validators=[DataRequired(), NumberRange(min=1, max=100, message='This should be between 1 and 100 euro')])
    receipt_img = FileField('Upload receipt', validators=[])

    def __init__(self, meal_obj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meal_obj = meal_obj

    # Attach the custom validator
    def validate_receipt_img(self, field):
        meal = getattr(self, 'meal_obj', None)
        # Only require if meal has no existing receipt and no file uploaded
        if meal and not meal.receipt_img and not field.data:
            raise ValidationError("Please upload a receipt image.")
