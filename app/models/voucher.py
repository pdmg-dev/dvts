from datetime import datetime, timezone

from app.extensions import db


class DisbursementVoucher(db.Model):
    __tablename__ = "vouchers"

    id = db.Column(db.Integer, primary_key=True)

    dv_number = db.Column(db.String(20), unique=True)
    mode_of_payment = db.Column(db.Enum("Cash", "Check", "Others", name="mode_of_payment"), default="Check")

    payee = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))

    obr_number = db.Column(db.String(20), unique=True, nullable=True)
    resp_center = db.Column(db.String(20))

    particulars = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)

    attachment = db.Column(db.String(120))

    date_received = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    category_id = db.Column(db.ForeignKey("categories.id", name="fk_vouchers_category_id", ondelete="SET NULL"))
    category = db.relationship("Category", back_populates="vouchers", lazy="selectin")

    def __repr__(self):
        return f"<Voucher: {self.payee} | {self.amount}>"


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    vouchers = db.relationship("DisbursementVoucher", back_populates="category", passive_deletes=True)

    def __repr__(self):
        return f"<Category: {self.name}>"
