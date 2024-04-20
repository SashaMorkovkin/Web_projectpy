from wtforms.validators import DataRequired, EqualTo, Length, NumberRange
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, IntegerField
from wtforms import FileField, TextAreaField, SelectField


class AuthForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class Auth2(FlaskForm):
    code = IntegerField('Код подтверждения', validators=[DataRequired()])