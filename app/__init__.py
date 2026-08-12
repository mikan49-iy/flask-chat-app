import os

from flask import Flask, redirect, request, url_for
from flask_login import current_user

from .extensions import db, migrate, login_manager


def create_app():
    app = Flask(__name__)

    secret_key = os.environ.get("SECRET_KEY")
    database_url = os.environ.get("DATABASE_URL")

    if not secret_key:
        raise RuntimeError("SECRET_KEYが設定されていません")

    if not database_url:
        raise RuntimeError("DATABASE_URLが設定されていません")

    app.config["SECRET_KEY"] = secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from . import models
    from . import login_config

    from .cli import create_admin
    app.cli.add_command(create_admin)

    from .auth import auth_bp
    from .admin import admin_bp
    from .chat import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)

    @app.before_request
    def require_password_change():
        if not current_user.is_authenticated:
            return None

        if current_user.role != "user":
            return None

        if not current_user.must_change_password:
            return None

        allowed_endpoints = {
            "auth.password_change",
            "auth.logout",
            "static",
        }

        if request.endpoint not in allowed_endpoints:
            return redirect(url_for("auth.password_change"))

        return None

    @app.route("/")
    def index():
        return "Hello, Chat App!"

    return app