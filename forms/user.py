from wtforms.validators import DataRequired, EqualTo, Length, NumberRange
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, IntegerField
from wtforms import TextAreaField, SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    name = StringField('Никнейм', validators=[DataRequired()])
    email = EmailField('Электронная почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Пароль снова',
                                   validators=[DataRequired(),
                                               EqualTo('password', message='пароли не совпадают')])
    submit = SubmitField('Регистрация')


class EditProfileForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    about = TextAreaField('Обо мне', validators=[Length(max=700)])
    age = IntegerField('Возраст', validators=[NumberRange(6, 99)])
    is_private = SelectField('Приватность профиля', choices=[('False', 'Открыт для всех'),
                                                                  ("NS", 'Открыт для друзей'),
                                                                  ("True", 'Закрытый')])
    submit = SubmitField('Сохранить')


class EditAvatarForm(FlaskForm):
    image = FileField('Выберите новое фото профиля',
                      validators=[FileRequired(),
                                  FileAllowed(["png", "jpg", "svg", "jpeg"], 'Images only!')])
    submit = SubmitField('Поменять')