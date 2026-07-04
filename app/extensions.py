from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect


db = SQLAlchemy()
csrf = CSRFProtect()


def init_extensions(app) -> None:
    """Initialize Flask extensions."""
    db.init_app(app)
    csrf.init_app(app)
