from flask_wtf import FlaskForm
from wtforms import DecimalField, RadioField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, NumberRange


class DVForm(FlaskForm):
    dv_number = StringField("Disbursement Voucher No.", validators=[Length(max=20)])
    mode_of_payment = RadioField(
        "Mode of Payment", choices=[("Check", "Check"), ("Cash", "Cash"), ("Others", "Others")], default="Check"
    )

    payee = StringField("Payee", validators=[InputRequired(), Length(max=120)])
    address = StringField("Address", validators=[Length(max=120)])

    obr_number = StringField("OBR No.", validators=[Length(max=20)])
    resp_center = StringField("Office/Unit/Project", validators=[Length(max=20)])

    particulars = TextAreaField("Particulars", validators=[InputRequired()])
    amount = DecimalField(
        "Amount",
        places=2,
        validators=[InputRequired(), NumberRange(min=0)],
    )

    submit = SubmitField("Save")
