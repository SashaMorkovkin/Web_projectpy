from wtforms.validators import DataRequired, Length, NumberRange, Optional
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, IntegerField


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
    points1 = IntegerField(validators=[DataRequired(), NumberRange(min=0, max=100)])
    answer2 = StringField('Ответ2', validators=[DataRequired()])
    points2 = IntegerField(validators=[DataRequired(), NumberRange(min=0, max=100)])
    answer3 = StringField('Ответ3')
    points3 = IntegerField(validators=[NumberRange(min=0, max=100), Optional()])
    answer4 = StringField('Ответ4')
    points4 = IntegerField(validators=[NumberRange(min=0, max=100), Optional()])
    answer5 = StringField('Ответ5')
    points5 = IntegerField(validators=[NumberRange(min=0, max=100), Optional()])
    answer6 = StringField('Ответ6')
    points6 = IntegerField(validators=[NumberRange(min=0, max=100), Optional()])
    koeff = IntegerField("Коэффициент важности",
                         validators=[NumberRange(min=0, max=100), Optional()])
    submit = SubmitField('Создать')