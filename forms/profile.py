from wtforms.validators import DataRequired, EqualTo
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, IntegerField


class ProfileForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    about = StringField('Обо мне', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    photo = FileField('Красивое фото', validators=[DataRequired()])
    submit = SubmitField('Сохранить')