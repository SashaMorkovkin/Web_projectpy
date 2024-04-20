from wtforms.validators import DataRequired, Length, NumberRange, Optional
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, IntegerField


class AddQuiz(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(max=70)])
    description = TextAreaField('Описание', validators=[Length(max=500)])
    mode = SelectField('Приватность',
                       choices=[('forall', 'Доступно для всех'),
                                ('forfriends', 'Доступно для друзей'),
                                ('forme', 'Доступно для меня')],
                       validators=[DataRequired()])
    category1 = SelectField()
    category2 = SelectField()
    category3 = SelectField()
    submit = SubmitField('Опубликовать')
    save = SubmitField('Сохранить')

    def set_categories(category: list):
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
    points1 = IntegerField(validators=[DataRequired(), NumberRange(0, 100)])
    points2 = IntegerField(validators=[DataRequired(), NumberRange(0, 100)])
    points3 = IntegerField(validators=[Optional(), NumberRange(0, 100)])
    points4 = IntegerField(validators=[Optional(), NumberRange(0, 100)])
    points5 = IntegerField(validators=[Optional(), NumberRange(0, 100)])
    points6 = IntegerField(validators=[Optional(), NumberRange(0, 100)])
    koeff = IntegerField("Коэффициент важности",
                         validators=[DataRequired(), NumberRange(0, 100)])
    submit = SubmitField('Создать')