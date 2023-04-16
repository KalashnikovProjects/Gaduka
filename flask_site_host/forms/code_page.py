from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, FileField, StringField
from wtforms.validators import DataRequired


class SaveProjectForm(FlaskForm):
    name = StringField('Название проекта', validators=[DataRequired(),])
    code = TextAreaField('Код на Гадюке')
    images = FileField('Добавить иконку')
    submit = SubmitField('Сохранить')
    delete = SubmitField('')

