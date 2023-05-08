import smtplib
import ssl

from flask import Blueprint, request

from project.common.constants import ResponseConstants, StatusCodes, EndpointPaths
from project.common.decorators import jsonify_response
from project.flask.blueprints.auth.authentication_exceptions import InvalidRecaptchaException
from project.flask.blueprints.auth.authentication_utils import validate_recaptcha
from project.flask.blueprints.response_objects import BasicResponse
from project.settings import Config

email_blueprint = Blueprint('email', __name__)


@jsonify_response
def send_email_view():
    request_data = request.get_json()
    person = request_data.get('name')
    email = request_data.get('email')
    message = request_data.get('message')
    recaptcha = request_data.get('recaptcha')

    try:
        validate_recaptcha(recaptcha)

        subject = f'Message sent from {person} with email {email}'
        full_message = f'Subject: {subject}\n\n{message}\n\nRegards, {person}'

        send_email(full_message)
        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.SUCCESSFULLY_SENT_EMAIL,
                                 status_code=StatusCodes.SUCCESSFULLY_CREATED)

    except InvalidRecaptchaException:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.INVALID_RECAPTCHA_ERROR,
                                 status_code=StatusCodes.BAD_REQUEST)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.ERROR_FAILED_TO_SEND_EMAIL,
                                 status_code=StatusCodes.INTERNAL_SERVER_ERROR)
    return response


def send_email(message):
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', Config.GMAIL_PORT, context=context) as server:
        server.login(Config.BACKEND_EMAIL, Config.BACKEND_EMAIL_PASS)
        server.sendmail(Config.BACKEND_EMAIL, Config.BUSINESS_EMAIL, message)
        server.quit()
    return True


email_blueprint.add_url_rule(EndpointPaths.SEND_EMAIL, view_func=send_email_view, methods=['POST'])


