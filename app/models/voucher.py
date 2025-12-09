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
    resp_center_id = db.Column(
        db.ForeignKey("responsibility_centers.id", name="fk_vouchers_resp_center_id", ondelete="SET NULL")
    )
    resp_center = db.relationship("ResponsibilityCenter", back_populates="vouchers", lazy="selectin")

    particulars = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)

    attachments = db.relationship(
        "Attachment", back_populates="voucher", lazy="selectin", cascade="all, delete-orphan", passive_deletes=True
    )

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


class ResponsibilityCenter(db.Model):
    __tablename__ = "responsibility_centers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    acronym = db.Column(db.String(20), unique=True, nullable=True)
    code = db.Column(db.String(20), unique=True, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    vouchers = db.relationship("DisbursementVoucher", back_populates="resp_center", passive_deletes=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.id} | {self.name}>"


class Attachment(db.Model):
    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)

    uploaded_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    voucher_id = db.Column(db.Integer, db.ForeignKey("vouchers.id", ondelete="CASCADE"), nullable=False)

    voucher = db.relationship("DisbursementVoucher", back_populates="attachments", lazy="selectin")

    def __repr__(self):
        return f"<Attachment: {self.filename} for Voucher ID {self.voucher_id}>"
