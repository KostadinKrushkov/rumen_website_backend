from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# from project.database.database_manager import DatabaseManager

# Provides bcrypt hashing utilities for the application
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()

#
# def get_database_for_app(app):
#     return DatabaseManager(app).init_database()




