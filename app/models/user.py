import json
from datetime import datetime, timezone

from flask_login import UserMixin

from app.extensions import bcrypt, db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(128), nullable=False)

    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # JSON string to store per-user preferences
    preferences_json = db.Column(db.Text, nullable=True)

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

    # Preferences helpers
    def get_preferences(self) -> dict:
        try:
            return json.loads(self.preferences_json) if self.preferences_json else {}
        except Exception:
            return {}

    def set_preferences(self, prefs: dict):
        try:
            self.preferences_json = json.dumps(prefs)
        except Exception:
            # Fallback: clear preferences if serialization fails
            self.preferences_json = None


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<{self.__class__.__name__}: id={self.id} | name={self.name}>"
