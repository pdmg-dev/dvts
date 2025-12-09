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

from app.models.voucher import Category, ResponsibilityCenter


class DVForm(FlaskForm):
    dv_number = StringField("Voucher No.", validators=[Length(max=20)])
    mode_of_payment = SelectField(
        "Mode of Payment", choices=[("Check", "Check"), ("Cash", "Cash"), ("Others", "Others")], default="Check"
    )

    payee = StringField("Payee", validators=[InputRequired(), Length(max=120)])
    address = StringField("Address", validators=[Length(max=120)])

    obr_number = StringField("OBR No.", validators=[Length(max=20)])
    resp_center_id = SelectField("Office", coerce=int)

    particulars = TextAreaField("Particulars", validators=[InputRequired()])
    amount = DecimalField(
        "Amount",
        places=2,
        validators=[InputRequired(), NumberRange(min=0)],
    )

    attachment = FileField("Attachment", validators=[FileAllowed(["jpg", "jpeg", "png", "pdf"])])

    date_received = DateTimeLocalField("Date Received", format="%Y-%m-%dT%H:%M", validators=[InputRequired()])
    category_id = SelectField("Category", coerce=int, validate_choice=False)

    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super(DVForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(0, "")] + [
            (cat.id, cat.name) for cat in Category.query.order_by(Category.name.asc()).all()
        ]
        self.resp_center_id.choices = [
            (rc.id, rc.acronym) for rc in ResponsibilityCenter.query.order_by(ResponsibilityCenter.name.asc()).all()
        ]
