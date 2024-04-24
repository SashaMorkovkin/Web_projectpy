from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField


class AuthForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class Auth2(FlaskForm):
    key = StringField('Ключ верификации (придёт на аторизированное устройство)',
                      validators=[DataRequired()])
    submit = SubmitField('Продолжить')
