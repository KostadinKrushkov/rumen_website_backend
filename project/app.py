import sys
import logging

from flask import Flask
from flask_compress import Compress
from flask_cors import CORS

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from project.auth.user import User
from project.common.constants import ResponseConstants
from project.database.database_manager import DatabaseManager
from project.database.gateways.user_gateway import UserGateway
from project.extensions import (
    bcrypt, login_manager
)
from project.flask.blueprints.auth.authentication_blueprint import auth_blueprint
from project.flask.blueprints.blog.blog_blueprint import blog_blueprint
from project.flask.blueprints.category.category_blueprint import category_blueprint
from project.flask.blueprints.email.email_blueprint import email_blueprint
from project.flask.blueprints.picture.picture_blueprint import picture_blueprint
from project.flask.blueprints.ping_blueprint import ping_blueprint
from project.settings import Config

logging.basicConfig(format='%(asctime)s | %(levelname)s | %(message)s', level=logging.DEBUG if Config.DEBUG else logging.INFO)


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    register_extensions(app)
    register_blueprints(app)

    limiter = Limiter(get_remote_address, app=app)
    limiter.limit(Config.SMTP_REQUESTS_LIMIT, error_message=ResponseConstants.DAILY_LIMIT_EXCEEDED)(email_blueprint)
    return app


def register_extensions(app):
    CORS(app, supports_credentials=True)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    Compress(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            user_dto = UserGateway().get_by_id(user_id)
            return User.from_dto(user_dto)
        except Exception:
            return None


def register_blueprints(app):
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(blog_blueprint)
    app.register_blueprint(picture_blueprint)
    app.register_blueprint(category_blueprint)
    app.register_blueprint(email_blueprint)
    app.register_blueprint(ping_blueprint)


app = create_app()


if __name__ == "__main__":
    arguments = sys.argv[1:] if len(sys.argv) > 1 else []
    should_reset = "--reset" == arguments[0] if arguments else False

    if should_reset:
        DatabaseManager(app).reset_database()
    else:
        app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000, ssl_context=(Config.CERT_PATH, Config.CERT_KEY_PATH))
