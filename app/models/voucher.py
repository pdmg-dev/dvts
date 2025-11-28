from app.extensions import db


class DisbursementVoucher(db.Model):
    __tablename__ = "vouchers"

    id = db.Column(db.Integer, primary_key=True)

    dv_number = db.Column(db.String(20), unique=True)
    mode_of_payment = db.Column(db.Enum("Cash", "Check", "Others", name="mode_of_payment"), default="Check")

    payee = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))

    obr_number = db.Column(db.String(20), unique=True)
    resp_center = db.Column(db.String(20))

    particulars = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)

    def __repr__(self):
        return f"<Voucher: {self.payee} | {self.amount}>"
