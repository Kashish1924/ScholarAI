from flask import Flask, render_template

from app.config.settings import config_by_name
from app.extensions import csrf, init_extensions
from app.routes.main import main_bp
from app.student.routes import student_bp
from app.admin.routes import admin_bp
from app.api.routes import api_bp
from app.api.seed_routes import seed_bp
import app.models  # noqa: F401


def create_app(config_name: str = "development") -> Flask:
    """Application factory used to create Flask app instances."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_by_name[config_name])

    init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)

    return app


def register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(seed_bp, url_prefix="/api/v1")
    csrf.exempt(api_bp)
    csrf.exempt(seed_bp)


def register_error_handlers(app: Flask) -> None:
    """Register HTML and JSON friendly error handlers."""

    @app.errorhandler(404)
    def not_found_error(error):
        if _is_api_request():
            return {"status": "error", "message": "Resource not found"}, 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        if _is_api_request():
            return {"status": "error", "message": "Internal server error"}, 500
        return render_template("errors/500.html"), 500

    def _is_api_request() -> bool:
        from flask import request

        return request.path.startswith("/api/")
