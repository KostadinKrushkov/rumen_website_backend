from unittest import mock
from unittest.mock import patch

from project.common.constants import StatusCodes, ResponseConstants
from project.settings import Config
from tests.integration_tests.api_requests import send_email_request
from tests.integration_tests.testing_utils import assert_response_matches_expected

stub_email = {
    'name': 'Kostadin Krushkov',
    'email': 'kostadin01998@gmail.com',
    'message': 'I would love to get in touch.',
    'recaptcha': None
}


class TestEmailAPI:
    def test_send_email_successfully(self, unauthenticated_client):
        smtplib_mock = mock.Mock()
        server_mock = mock.Mock()
        context_manager = mock.Mock()
        context_manager.__enter__ = lambda _: server_mock
        context_manager.__exit__ = lambda _, __, ___, ____: server_mock
        smtplib_mock.SMTP_SSL = lambda _, __, context: context_manager

        expected_message = f'Subject: Message sent from {stub_email["name"]} with email {stub_email["email"]}\n\n{stub_email["message"]}\n\nRegards, {stub_email["name"]}'

        with patch('project.flask.blueprints.email.email_blueprint.smtplib', smtplib_mock):
            response = send_email_request(unauthenticated_client, stub_email)

            server_mock.sendmail.assert_called_once_with(Config.BACKEND_EMAIL, Config.BUSINESS_EMAIL, expected_message)
            server_mock.login.assert_called_once_with(Config.BACKEND_EMAIL, Config.BACKEND_EMAIL_PASS)
            server_mock.quit.assert_called_once_with()

            assert_response_matches_expected(response, code=StatusCodes.SUCCESSFULLY_CREATED,
                                             status=ResponseConstants.SUCCESS,
                                             message=ResponseConstants.SUCCESSFULLY_SENT_EMAIL)

    def test_send_email_fails_on(self, unauthenticated_client):
        smtplib_mock = mock.Mock()
        smtplib_mock.SMTP_SSL.side_effect = Exception("SMPT error")

        with patch('project.flask.blueprints.email.email_blueprint.smtplib', smtplib_mock):
            response = send_email_request(unauthenticated_client, stub_email)

            assert_response_matches_expected(response, code=StatusCodes.INTERNAL_SERVER_ERROR,
                                             status=ResponseConstants.FAILURE,
                                             message=ResponseConstants.ERROR_FAILED_TO_SEND_EMAIL)
