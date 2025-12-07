from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class CategoryForm(FlaskForm):
    name = StringField("Please enter a new category name.", validators=[InputRequired(), Length(max=50)])
    submit = SubmitField("Create")


class RoleForm(FlaskForm):
    name = StringField("Please enter a new role name.", validators=[InputRequired(), Length(max=50)])
    submit = SubmitField("Create")


class OfficeForm(FlaskForm):
    name = StringField("Please enter a new office name.", validators=[InputRequired(), Length(max=100)])
    acronym = StringField("Please enter the office acronym.", validators=[Length(max=10)])
    code = StringField("Please enter the office code.", validators=[Length(max=10)])
    submit = SubmitField("Create")
