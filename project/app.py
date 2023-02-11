import sys

from flask import Flask
from flask_cors import CORS

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from project.auth.user import User
from project.common.constants import ResponseConstants
from project.database.connection import init_session
from project.database.database_manager import DatabaseManager
from project.database.gateways.user_gateway import UserGateway
from project.extensions import (
    bcrypt,
    login_manager
)
from project.flask.blueprints.auth.authentication_blueprint import auth_blueprint
from project.flask.blueprints.blog.blog_blueprint import blog_blueprint
from project.flask.blueprints.category.category_blueprint import category_blueprint
from project.flask.blueprints.email.email_blueprint import email_blueprint, ping_blueprint
from project.flask.blueprints.picture.picture_blueprint import picture_blueprint
from project.settings import CERT_PATH, CERT_KEY_PATH, SMTP_REQUESTS_LIMIT

app = None


def create_app(config_object="project.settings"):
    app = Flask(__name__)
    app.config.from_object(config_object)
    CORS(app, supports_credentials=True)

    register_extensions(app)
    register_blueprints(app)

    limiter = Limiter(get_remote_address, app=app)
    limiter.limit(SMTP_REQUESTS_LIMIT, error_message=ResponseConstants.DAILY_LIMIT_EXCEEDED)(email_blueprint)
    return app


def register_extensions(app):
    bcrypt.init_app(app)
    login_manager.init_app(app)

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


if __name__ == "__main__":
    arguments = sys.argv[1:] if len(sys.argv) > 1 else []
    should_reset = "--reset" == arguments[0] if arguments else False

    app = create_app()

    with app.app_context():
        Session = init_session()

    if should_reset:
        DatabaseManager(app).reset_database()

    certificate_path = r'D:\Coding\rumen_website_backend\git_ignored_temp\official_rumenplamenovart.com-2023-02-09.pem'
    certificate_key_path = r'D:\Coding\rumen_website_backend\git_ignored_temp\rumenplamenovart.com-2023-02-09.key'
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=(certificate_path, certificate_key_path))
    # app.run(debug=True, host='0.0.0.0', port=5000)#, ssl_context=(CERT_PATH, CERT_KEY_PATH))

