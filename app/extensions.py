"""Flask extensions singletons.

Extensions are instantiated here (outside the factory) and then
initialised inside ``create_app`` so that they can be imported from
anywhere in the application without triggering circular imports.
"""

from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db: SQLAlchemy = SQLAlchemy()
migrate: Migrate = Migrate()
bcrypt: Bcrypt = Bcrypt()
login_manager: LoginManager = LoginManager()
csrf: CSRFProtect = CSRFProtect()
cache: Cache = Cache()
