from app import create_app
from app.extensions import db
from app.models.user import User


def seed_admin():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        existing_user = User.query.filter_by(email="philidanielgonzales@gmail.com").first()
        if existing_user:
            print("Admin user already exists.")
            return

        # Create new admin user
        admin = User(
            full_name="Philip Daniel Gonzales",
            username="philip",
            email="philipdanielgonzales@gmail.com",
            is_admin=True,
        )
        admin.set_password("philip")

        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")


if __name__ == "__main__":
    seed_admin()
