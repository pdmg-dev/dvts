from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
    DateTimeLocalField,
    DecimalField,
    FileField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import InputRequired, Length, NumberRange


class DVForm(FlaskForm):
    dv_number = StringField("Voucher No.", validators=[Length(max=20)])
    mode_of_payment = SelectField(
        "Mode of Payment", choices=[("Check", "Check"), ("Cash", "Cash"), ("Others", "Others")], default="Check"
    )

    payee = StringField("Payee", validators=[InputRequired(), Length(max=120)])
    address = StringField("Address", validators=[Length(max=120)])

    obr_number = StringField("OBR No.", validators=[Length(max=20)])
    resp_center = StringField("Office", validators=[InputRequired(), Length(max=20)])
    particulars = TextAreaField("Particulars", validators=[InputRequired()])
    amount = DecimalField(
        "Amount",
        places=2,
        validators=[InputRequired(), NumberRange(min=0)],
    )

    attachment = FileField("Attachment", validators=[FileAllowed(["jpg", "jpeg", "png", "pdf"])])

    date_received = DateTimeLocalField("Date Received", format="%Y-%m-%dT%H:%M", validators=[InputRequired()])
    category = StringField("Category", validators=[Length(max=20)])

    submit = SubmitField("Save")
