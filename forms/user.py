from wtforms.validators import DataRequired, EqualTo, Length, NumberRange
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, IntegerField
from wtforms import FileField, TextAreaField, SelectField


class LoginForm(FlaskForm):
    ''' Форма авторизации '''
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    ''' Форма регистрации '''
    name = StringField('Никнейм', validators=[DataRequired()])
    email = EmailField('Электронная почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Пароль снова',
                                   validators=[DataRequired(),
                                               EqualTo('password', message='пароли не совпадают')])
    submit = SubmitField('Регистрация')


class EditProfileForm(FlaskForm):
    ''' Форма изменения профиля '''
    name = StringField('Имя', validators=[DataRequired()])
    about = TextAreaField('Обо мне', validators=[Length(max=700)])
    age = IntegerField('Возраст', validators=[NumberRange(6, 99)])
    is_private = SelectField('Приватность профиля', choices=[('False', 'Открыт для всех'),
                                                                  ("NS", 'Открыт для друзей'),
                                                                  ("True", 'Закрытый')])
    submit = SubmitField('Сохранить')