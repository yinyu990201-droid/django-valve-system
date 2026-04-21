import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def create_app() -> Flask:
    app = Flask(__name__)
    project_root = Path(app.root_path).parent.resolve()
    data_dir = project_root / "data"
    upload_dir = data_dir / "uploads"
    default_db_uri = f"sqlite:///{(data_dir / 'app.db').as_posix()}"

    load_dotenv(project_root / ".env")

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", default_db_uri)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_DIR"] = os.getenv("UPLOAD_DIR", str(upload_dir))
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", str(32 * 1024 * 1024)))
    app.config["SHOW_DEMO_CREDENTIALS"] = _env_flag("SHOW_DEMO_CREDENTIALS", default=True)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    app.config["SESSION_COOKIE_SECURE"] = _env_flag("SESSION_COOKIE_SECURE", default=False)
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["REMEMBER_COOKIE_SAMESITE"] = os.getenv("REMEMBER_COOKIE_SAMESITE", "Lax")
    app.config["REMEMBER_COOKIE_SECURE"] = _env_flag("REMEMBER_COOKIE_SECURE", default=False)

    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=int(os.getenv("PROXY_FIX_X_FOR", "1")),
        x_proto=int(os.getenv("PROXY_FIX_X_PROTO", "1")),
        x_host=int(os.getenv("PROXY_FIX_X_HOST", "1")),
        x_port=int(os.getenv("PROXY_FIX_X_PORT", "1")),
        x_prefix=int(os.getenv("PROXY_FIX_X_PREFIX", "0")),
    )

    db.init_app(app)
    login_manager.init_app(app)

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}, 200

    from . import models
    from .routes import register_routes

    with app.app_context():
        db.create_all()
        models.ensure_document_model_code_column()
        models.ensure_default_admin()

    register_routes(app)
    return app
