from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SelectField, MultipleSelectField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Optional

class ThreatForm(FlaskForm):
    name = StringField('Название угрозы', validators=[DataRequired()])
    damage = FloatField('Ущерб', validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Описание', validators=[Optional()])

class ProgramForm(FlaskForm):
    name = StringField('Название программы', validators=[DataRequired()])
    price = FloatField('Цена', validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Описание', validators=[Optional()])
    type = SelectField('Тип программы', choices=[('Антивирус', 'Антивирус'), ('Межсетевой экран', 'Межсетевой экран'), ('Антивирусная утилита', 'Антивирусная утилита')], validators=[DataRequired()])

class EfficacyForm(FlaskForm):
    efficacy = FloatField('Эффективность', validators=[DataRequired(), NumberRange(min=0, max=1)])

class CalculationForm(FlaskForm):
    threats = MultipleSelectField('Выберите угрозы', validators=[DataRequired()])
    max_price = FloatField('Максимальная цена', validators=[DataRequired(), NumberRange(min=0)])
