from datetime import datetime
import os

from flask import current_app
from flask_login import UserMixin
from sqlalchemy import inspect, text
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager


product_model_tag = db.Table(
    "product_model_tag",
    db.Column("product_model_id", db.Integer, db.ForeignKey("product_model.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("product_tag.id"), primary_key=True),
)


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "app_user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user", index=True)
    full_name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_active(self) -> bool:
        return self.active


class ProductCategory(TimestampMixin, db.Model):
    __tablename__ = "product_category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=100)


class ProductFunction(TimestampMixin, db.Model):
    __tablename__ = "product_function"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=100)


class ProductTag(TimestampMixin, db.Model):
    __tablename__ = "product_tag"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)


class ProductModel(TimestampMixin, db.Model):
    __tablename__ = "product_model"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False, index=True)
    sun_code = db.Column(db.String(80), nullable=True, index=True)
    title = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("product_category.id"), nullable=False, index=True)
    function_id = db.Column(db.Integer, db.ForeignKey("product_function.id"), nullable=False, index=True)
    ports = db.Column(db.Integer, nullable=False, index=True)
    flow_lpm = db.Column(db.Integer, nullable=False, index=True)
    pressure_bar = db.Column(db.Integer, nullable=False, index=True)
    cavity = db.Column(db.String(80), nullable=False, index=True)
    structure = db.Column(db.String(200), nullable=False)
    symbol = db.Column(db.String(40), nullable=False, default="relief")
    summary = db.Column(db.Text, nullable=False)
    replacement_note = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="active", index=True)
    sort_order = db.Column(db.Integer, nullable=False, default=100)

    category_ref = db.relationship("ProductCategory", backref=db.backref("models", lazy="dynamic"))
    function_ref = db.relationship("ProductFunction", backref=db.backref("models", lazy="dynamic"))
    tag_refs = db.relationship("ProductTag", secondary=product_model_tag, backref=db.backref("models", lazy="dynamic"))
    feature_refs = db.relationship(
        "ProductFeature",
        backref="product_model",
        cascade="all, delete-orphan",
        order_by="ProductFeature.sort_order",
    )
    application_refs = db.relationship(
        "ProductApplication",
        backref="product_model",
        cascade="all, delete-orphan",
        order_by="ProductApplication.sort_order",
    )
    cross_references = db.relationship(
        "ProductCrossReference",
        backref="product_model",
        cascade="all, delete-orphan",
        order_by="ProductCrossReference.source_system",
    )

    @property
    def category(self) -> str:
        return self.category_ref.name if self.category_ref else ""

    @property
    def function(self) -> str:
        return self.function_ref.name if self.function_ref else ""

    @property
    def tags(self) -> tuple[str, ...]:
        return tuple(tag.name for tag in sorted(self.tag_refs, key=lambda tag: tag.name))

    @property
    def features(self) -> tuple[str, ...]:
        return tuple(feature.content for feature in self.feature_refs)

    @property
    def applications(self) -> tuple[str, ...]:
        return tuple(application.name for application in self.application_refs)

    @property
    def flow_bucket(self) -> str:
        if self.flow_lpm < 30:
            return "0-30"
        if self.flow_lpm < 60:
            return "30-60"
        if self.flow_lpm <= 120:
            return "60-120"
        return "120+"

    @property
    def pressure_bucket(self) -> str:
        if self.pressure_bar <= 240:
            return "240"
        if self.pressure_bar <= 350:
            return "350"
        return "420"


class ProductFeature(TimestampMixin, db.Model):
    __tablename__ = "product_feature"

    id = db.Column(db.Integer, primary_key=True)
    product_model_id = db.Column(db.Integer, db.ForeignKey("product_model.id"), nullable=False, index=True)
    content = db.Column(db.String(200), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=100)


class ProductApplication(TimestampMixin, db.Model):
    __tablename__ = "product_application"

    id = db.Column(db.Integer, primary_key=True)
    product_model_id = db.Column(db.Integer, db.ForeignKey("product_model.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=100)


class ProductCrossReference(TimestampMixin, db.Model):
    __tablename__ = "product_cross_reference"

    id = db.Column(db.Integer, primary_key=True)
    product_model_id = db.Column(db.Integer, db.ForeignKey("product_model.id"), nullable=False, index=True)
    source_system = db.Column(db.String(80), nullable=False, default="SUN", index=True)
    source_code = db.Column(db.String(80), nullable=False, index=True)
    note = db.Column(db.Text, nullable=True)
    confidence_level = db.Column(db.String(20), nullable=False, default="reference")
    status = db.Column(db.String(20), nullable=False, default="active", index=True)


class Document(TimestampMixin, db.Model):
    __tablename__ = "product_document"

    id = db.Column(db.Integer, primary_key=True)
    product_model_id = db.Column(db.Integer, db.ForeignKey("product_model.id"), nullable=True, index=True)
    model_code = db.Column(db.String(80), nullable=True, index=True)
    title = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    document_type = db.Column(db.String(40), nullable=False, default="pdf")
    version_label = db.Column(db.String(80), nullable=True)
    visibility = db.Column(db.String(20), nullable=False, default="internal")
    file_size_bytes = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(120), nullable=False, default="application/pdf")
    uploaded_by = db.Column(db.Integer, db.ForeignKey("app_user.id"), nullable=False, index=True)

    product_model = db.relationship("ProductModel", backref=db.backref("documents", lazy="dynamic"))
    uploader = db.relationship("User", backref=db.backref("documents", lazy="dynamic"))

    @property
    def full_path(self) -> str:
        upload_dir = current_app.config["UPLOAD_DIR"]
        return os.path.join(upload_dir, self.stored_filename)


class Customer(TimestampMixin, db.Model):
    __tablename__ = "customer"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    contact_person = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    industry = db.Column(db.String(120), nullable=True)
    region = db.Column(db.String(120), nullable=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey("app_user.id"), nullable=True, index=True)
    status = db.Column(db.String(20), nullable=False, default="active", index=True)
    notes = db.Column(db.Text, nullable=True)

    owner = db.relationship("User", backref=db.backref("customers", lazy="dynamic"))


class CustomerContact(TimestampMixin, db.Model):
    __tablename__ = "customer_contact"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    is_primary = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.Text, nullable=True)

    customer = db.relationship("Customer", backref=db.backref("contacts", lazy="dynamic"))


class Inquiry(TimestampMixin, db.Model):
    __tablename__ = "inquiry"

    id = db.Column(db.Integer, primary_key=True)
    product_model_id = db.Column(db.Integer, db.ForeignKey("product_model.id"), nullable=True, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=True, index=True)
    source_model_code = db.Column(db.String(80), nullable=True, index=True)
    sun_reference_code = db.Column(db.String(80), nullable=True, index=True)
    contact_name = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(50), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    flow_lpm = db.Column(db.Integer, nullable=True)
    pressure_bar = db.Column(db.Integer, nullable=True)
    application_context = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="draft", index=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey("app_user.id"), nullable=True, index=True)

    product_model = db.relationship("ProductModel", backref=db.backref("inquiries", lazy="dynamic"))
    customer = db.relationship("Customer", backref=db.backref("inquiries", lazy="dynamic"))
    assignee = db.relationship("User", backref=db.backref("assigned_inquiries", lazy="dynamic"))


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


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


def ensure_legacy_schema_compatibility() -> None:
    inspector = inspect(db.engine)
    table_names = set(inspector.get_table_names())

    if "customer" in table_names:
        columns = {column["name"] for column in inspector.get_columns("customer")}
        missing_columns = {
            "industry": "VARCHAR(120)",
            "region": "VARCHAR(120)",
            "owner_user_id": "INTEGER",
            "status": "VARCHAR(20)",
            "updated_at": "DATETIME",
        }
        with db.engine.begin() as connection:
            for name, column_type in missing_columns.items():
                if name not in columns:
                    connection.execute(text(f"ALTER TABLE customer ADD COLUMN {name} {column_type}"))
