from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from flask_wtf.file import FileRequired, FileAllowed


class UploadPhoto(FlaskForm):
    image = FileField('Выберите файл',
                      validators=[FileRequired(),
                                  FileAllowed(["png", "jpg", "svg", "jpeg"], 'Images only!')])
    submit = SubmitField('Загрузить')