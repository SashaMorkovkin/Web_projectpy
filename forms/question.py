from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, RadioField
from sqlalchemy_serializer import SerializerMixin


class AddForm(FlaskForm):
    ask = StringField('Вопрос', validators=[DataRequired()])
    question1 = StringField('Ответ1', validators=[DataRequired()])
    question2 = StringField('Ответ2', validators=[DataRequired()])
    question3 = StringField('Ответ3', validators=[DataRequired()])
    question4 = StringField('Ответ4', validators=[DataRequired()])
    is_private = BooleanField('Публичная')
    submit = SubmitField('Создать')