import os
import sys
import pytest

from project.app import create_app
from project.auth.user import User
from project.database.database_controller import DatabaseController
from project.database.database_manager import DatabaseManager
from project.database.gateways.user_gateway import UserGateway
from project.settings import Config
from tests.integration_tests.api_requests import send_register_user_request, send_login_user_request, \
    send_logout_user_request

admin_user_dict = {
    'username': "kostadin",
    'password': "Thisisagreatpassword12345!@#$%",
    'email': "kostadin@gmail.com",
}

normal_user_dict = {
    'username': "normal",
    'password': "Thisisagreatpassword12345!@#$%",
    'email': "normal_user@gmail.com",
}

user_context = {}
user_gateway = UserGateway()


def pytest_sessionstart():
    """This fixture puts the application in testing mode, creates the database and registers an admin user."""
    sys._called_from_test = True

    create_testing_files()
    reset_database_and_setup_users()


def pytest_sessionfinish():
    for user in user_gateway.get_all():
        user_gateway.delete(user)

    remove_testing_files()
    del sys._called_from_test


@pytest.fixture(autouse=True)
def run_before_and_after_tests(client):
    """Fixture to execute asserts before and after a test is run"""
    # Setup:
    try:
        # Some tests drop all tables so the setup needs to be recreated after them.
        DatabaseController.execute_get_response('SELECT * FROM users')
    except:
        reset_database_and_setup_users()

    yield

    # Teardown


@pytest.fixture
def client():
    """This fixture resets the category, blog and picture data.
    The returned unauthenticated client could be used to access the API."""

    app = create_app()
    app.config.update({
        'TESTING': True,
    })

    with app.test_client() as client:
        with app.app_context():
            DatabaseManager(app).reset_data_without_users()
        client.set_cookie(Config.STATIC_IP_ADDRESS, 'token', user_context.get('token'))
        yield client


@pytest.fixture
def authorized_client(client):
    """This fixture returns a client with full admin permissions"""
    login_admin_user(client)
    return client


@pytest.fixture
def authenticated_client(client):
    """This fixture returns a client with normal user permissions"""
    login_normal_user(client)
    return client


@pytest.fixture
def unauthenticated_client(client):
    """This fixture returns a client without a user"""
    send_logout_user_request(client)
    return client


def reset_database_and_setup_users():
    app = create_app()
    app.config.update({
        'TESTING': True,
    })

    with app.test_client() as starting_client:
        with app.app_context():
            DatabaseManager(app).reset_database()

    send_register_user_request(starting_client, {'recaptcha': None, 'user': admin_user_dict})
    send_register_user_request(starting_client, {'recaptcha': None, 'user': normal_user_dict})

    user = user_gateway.get_by_username(admin_user_dict['username'])
    auth_token = User.encode_auth_token(user.id)
    user_context['token'] = auth_token


def create_testing_files():
    for file_path in Config.TESTING_FILES:
        open(file_path, 'w').close()


def remove_testing_files():
    for file_path in Config.TESTING_FILES:
        os.remove(file_path)


def login_normal_user(test_client):
    update_user(admin_user_dict['username'], 1, 0)
    user_params = {'recaptcha': None, 'user': admin_user_dict}
    return send_login_user_request(test_client, user_params)


def login_admin_user(test_client):
    update_user(admin_user_dict['username'], 1, 1)
    user_params = {'recaptcha': None, 'user': admin_user_dict}
    return send_login_user_request(test_client, user_params)


def update_user(username, is_verified, is_admin):
    user = user_gateway.get_by_username(username)
    user.is_verified = is_verified
    user.is_admin = is_admin
    user_gateway.update(user)
