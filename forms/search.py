from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm


class Search(FlaskForm):
    field = StringField(validators=[DataRequired()])
    user = SubmitField('Юзер')
    quiz = SubmitField('Опрос')