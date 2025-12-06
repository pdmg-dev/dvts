from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class CategoryForm(FlaskForm):
    name = StringField("Please enter a new category name.", validators=[InputRequired(), Length(max=50)])
    submit = SubmitField("Create")
