"""Application factory."""

import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

from app.config import config
from app.extensions import bcrypt, cache, csrf, db, login_manager, migrate


def create_app(config_name: str = "default") -> Flask:
    """Create and configure the Flask application.

    Args:
        config_name: The configuration profile to use
                     (development / testing / production).

    Returns:
        A fully configured Flask application instance.
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config[config_name])

    _init_extensions(app)
    _configure_login_manager(app)
    _configure_security(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _configure_logging(app)

    return app


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _init_extensions(app: Flask) -> None:
    """Initialise all Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)

    Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=app.config.get("RATELIMIT_STORAGE_URI", "memory://"),
    )

    if not app.testing:
        csp = {
            "default-src": "'self'",
            "style-src": ["'self'", "'unsafe-inline'"],
            "script-src": "'self'",
        }
        Talisman(
            app,
            content_security_policy=csp,
            force_https=False,
        )


def _configure_login_manager(app: Flask) -> None:
    """Set up Flask-Login."""
    login_manager.login_view = "auth.login"  # type: ignore[assignment]
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id: str) -> "User | None":
        from app.extensions import db as _db
        return _db.session.get(User, int(user_id))


def _configure_security(app: Flask) -> None:
    """Apply additional security settings."""
    # Enable WAL mode for SQLite to improve concurrency
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record) -> None:  # type: ignore[type-arg]
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


def _register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    from app.controllers.auth import auth_bp
    from app.controllers.main import main_bp
    from app.controllers.posts import posts_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(posts_bp, url_prefix="/posts")


def _register_error_handlers(app: Flask) -> None:
    """Register HTTP error handlers."""

    @app.errorhandler(400)
    def bad_request(e):  # type: ignore[type-arg]
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(401)
    def unauthorized(e):  # type: ignore[type-arg]
        from flask import render_template

        return render_template("errors/401.html"), 401

    @app.errorhandler(403)
    def forbidden(e):  # type: ignore[type-arg]
        return jsonify({"error": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(e):  # type: ignore[type-arg]
        from flask import render_template

        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):  # type: ignore[type-arg]
        db.session.rollback()
        app.logger.error("Internal server error: %s", e, exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


def _configure_logging(app: Flask) -> None:
    """Set up application logging."""
    if app.testing:
        return

    log_level = logging.DEBUG if app.debug else logging.INFO
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(log_level)

    app.logger.addHandler(stream_handler)
    app.logger.setLevel(log_level)
