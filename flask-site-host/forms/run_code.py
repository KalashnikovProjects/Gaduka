from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired


class CodeRunForm(FlaskForm):
    code = TextAreaField('Код на Гадюке')
    images = MultipleFileField('Прикрепить изображения', render_kw={'multiple': True})
    submit = SubmitField('Запустить')
