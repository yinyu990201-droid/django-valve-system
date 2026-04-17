from datetime import datetime
import os

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app

from . import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    uploader = db.relationship("User", backref="documents")

    @property
    def full_path(self) -> str:
        upload_dir = current_app.config["UPLOAD_DIR"]
        return os.path.join(upload_dir, self.stored_filename)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    contact_person = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


def ensure_default_admin() -> None:
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "Admin@123")
    admin = User.query.filter_by(username=username).first()
    if not admin:
        admin = User(username=username, role="admin")
        admin.set_password(password)
        db.session.add(admin)

    demo_username = os.getenv("DEMO_USERNAME", "viewer")
    demo_password = os.getenv("DEMO_PASSWORD", "Viewer@123")
    demo_user = User.query.filter_by(username=demo_username).first()
    if not demo_user:
        demo_user = User(username=demo_username, role="user")
        demo_user.set_password(demo_password)
        db.session.add(demo_user)

    db.session.commit()
