import datetime
from unittest import mock
from mock import patch, Mock

from flask_login import current_user

from project.auth.user import User
from project.common.constants import ResponseConstants, StatusCodes
from project.database.gateways.user_gateway import UserGateway
from project.flask.blueprints.auth.authentication_utils import does_hash_match_pass
from tests.integration_tests.api_requests import send_login_user_request, send_logout_user_request, \
    send_register_user_request, send_post_blog_request
from tests.integration_tests.testing_utils import _assert_response_matches_expected

user = {
    'email': 'john.does.not.exist@gmail.com',
    'username': 'aninterestingusername',
    'password': 'Some1234password'
}


class TestAuthenticationAPI:
    gateway = UserGateway()

    def test_register_successfully(self, client):
        num_of_users = len(list(self.gateway.get_all()))

        response = send_register_user_request(client, user)

        users = list(self.gateway.get_all())
        assert response['status_code'] == StatusCodes.SUCCESSFULLY_CREATED
        assert response['status'] == ResponseConstants.SUCCESS
        assert response['message'] == ResponseConstants.SUCCESSFULLY_REGISTERED
        assert len(users) == num_of_users + 1
        assert user.get('email') == users[-1].email
        assert user.get('username') == users[-1].username
        assert does_hash_match_pass(users[-1].password, user.get('password'))

    def test_register_fails_on_duplicate_username(self, client):
        send_register_user_request(client, user)
        response = send_register_user_request(client, user)
        assert response['status_code'] == StatusCodes.BAD_REQUEST
        assert response['status'] == ResponseConstants.FAILURE
        assert response['message'] == ResponseConstants.ERROR_USER_ALREADY_EXISTS

    def test_register_fails_on_incorrect_credentials(self, client):
        other_user = user.copy()
        other_user['password'] = "qwerty"
        response = send_register_user_request(client, other_user)
        assert response['status_code'] == StatusCodes.BAD_REQUEST
        assert response['status'] == ResponseConstants.FAILURE
        assert response['message'] == ResponseConstants.INCORRECT_CREDENTIALS_FOR_REGISTER

    def test_fails_on_internal_server_error(self, client):
        error_mock = mock.Mock()
        error_mock.side_effect = Exception
        with patch.object(UserGateway, 'save', error_mock):
            response = send_register_user_request(client, user)

        assert response['status_code'] == StatusCodes.BAD_REQUEST
        assert response['status'] == ResponseConstants.FAILURE
        assert response['message'] == ResponseConstants.GENERIC_SERVER_ERROR

    def test_login_and_logout_successfully(self, client):
        send_register_user_request(client, user)

        assert not current_user.is_authenticated

        login_response = send_login_user_request(client, user)
        assert login_response['status_code'] == StatusCodes.SUCCESS
        assert login_response['status'] == ResponseConstants.SUCCESS
        assert login_response['message'] == ResponseConstants.SUCCESSFULLY_LOGGED_IN
        assert current_user.is_authenticated

        logout_response = send_logout_user_request(client)
        assert logout_response['status_code'] == StatusCodes.SUCCESS
        assert logout_response['status'] == ResponseConstants.SUCCESS
        assert logout_response['message'] == ResponseConstants.SUCCESSFULLY_LOGGED_OUT
        assert not current_user.is_authenticated

    def test_login_fails_on_user_not_found(self, client):
        self.gateway.delete_by_email(user['email'])
        response = send_login_user_request(client, user)
        assert response['status_code'] == StatusCodes.BAD_REQUEST
        assert response['status'] == ResponseConstants.FAILURE
        assert response['message'] == ResponseConstants.INCORRECT_CREDENTIALS_FOR_LOGIN

    def test_login_fails_on_password_does_not_match(self, client):
        send_register_user_request(client, user)
        other_user = user.copy()
        other_user['password'] = 'Asdfqwer12341@3'

        response = send_login_user_request(client, other_user)
        assert response['status_code'] == StatusCodes.BAD_REQUEST
        assert response['status'] == ResponseConstants.FAILURE
        assert response['message'] == ResponseConstants.INCORRECT_CREDENTIALS_FOR_LOGIN

    def test_login_fails_on_internal_server_error(self, client):
        send_register_user_request(client, user)

        error_mock = mock.Mock()
        error_mock.side_effect = Exception
        with patch.object(UserGateway, 'get_by_username', error_mock):
            response = send_login_user_request(client, user)

        assert response['status_code'] == StatusCodes.BAD_REQUEST
        assert response['status'] == ResponseConstants.FAILURE
        assert response['message'] == ResponseConstants.GENERIC_SERVER_ERROR

    def test_token_validation_fails_on_missing_token(self, client):
        client.delete_cookie('localhost', 'token')
        response = send_post_blog_request(client, {})
        _assert_response_matches_expected(response, code=StatusCodes.UNAUTHENTICATED, status=ResponseConstants.FAILURE,
                                          message=ResponseConstants.MISSING_TOKEN)

    def test_token_validation_fails_on_invalid_token(self, client):
        client.set_cookie('localhost', 'token', 'WrongToken')
        response = send_post_blog_request(client, {})
        _assert_response_matches_expected(response, code=StatusCodes.INVALID_TOKEN, status=ResponseConstants.FAILURE,
                                          message=ResponseConstants.INVALID_TOKEN)

    def test_token_validation_fails_on_expired_token(self, unauthenticated_client):
        older_date = datetime.timedelta(days=-1, seconds=0)

        with patch('project.auth.user.EXPIRATION_DATETIME_DELTA', older_date):
            auth_token = User.encode_auth_token(1)

            unauthenticated_client.set_cookie('localhost', 'token', auth_token)
            response = send_post_blog_request(unauthenticated_client, {})
            _assert_response_matches_expected(response, code=StatusCodes.UNAUTHENTICATED,
                                              status=ResponseConstants.FAILURE,
                                              message=ResponseConstants.EXPIRED_TOKEN)
