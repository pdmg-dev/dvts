from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    identifier = StringField(label="Email or username", validators=[DataRequired("Enter your email or username")])
    password = PasswordField(label="Password", validators=[DataRequired("Enter a password")])
    remember = BooleanField(label="Remember me")
    submit = SubmitField(label="Login")
