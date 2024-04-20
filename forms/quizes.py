from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField


class AddQuiz(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(min=10, max=70)])
    description = TextAreaField('Описание', validators=[Length(max=500)])
    mode = SelectField('Приватность',
                       choices=[('forall', 'Доступно для всех'),
                                ('forfriends', 'Доступно для друзей'),
                                ('forme', 'Доступно для меня')],
                       validators=[DataRequired()])
    submit = SubmitField('Создать')

    def set_categories(category):
        AddQuiz.category1 = SelectField('Категория 1', choices=category)
        AddQuiz.category2 = SelectField('Категория 2', choices=category)
        AddQuiz.category3 = SelectField('Категория 3', choices=category)


class AddQuest(FlaskForm):
    title = StringField('Вопрос', validators=[DataRequired()])
    answer1 = StringField('Ответ1', validators=[DataRequired()])
    answer2 = StringField('Ответ2', validators=[DataRequired()])
    answer3 = StringField('Ответ3')
    answer4 = StringField('Ответ4')
    answer5 = StringField('Ответ5')
    answer6 = StringField('Ответ6')
    submit = SubmitField('Создать')