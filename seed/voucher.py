# seed.py
import random

from faker import Faker

from app import create_app
from app.extensions import db
from app.models.voucher import DisbursementVoucher

fake = Faker()


def seed_vouchers(n=50):
    app = create_app()
    with app.app_context():
        vouchers = []
        for i in range(n):
            voucher = DisbursementVoucher(
                dv_number=f"DV-{i+1:03d}",
                mode_of_payment=random.choice(["Cash", "Check", "Others"]),
                payee=fake.name(),
                address=fake.address(),
                obr_number=f"OBR-{i+1:03d}",
                resp_center=random.choice(["OMA", "MTO", "MBO", "DRR", "HR", "MENRO", "MEO", "MPDC"]),
                particulars=fake.sentence(nb_words=15),
                amount=round(random.uniform(100.0, 10000.0), 2),
            )
            vouchers.append(voucher)

        db.session.bulk_save_objects(vouchers)
        db.session.commit()
        print(f"Inserted {n} vouchers successfully!")


if __name__ == "__main__":
    seed_vouchers()
