# TODO add integartion testing
from flask import Blueprint, request, make_response, jsonify

import smtplib, ssl

from project.common.constants import ResponseConstants, StatusCodes
from project.flask.blueprints.auth.authentication_exceptions import InvalidRecaptchaException
from project.flask.blueprints.auth.authentication_utils import validate_recaptcha
from project.flask.blueprints.response_objects import BasicResponse, AuthenticationResponse
from project.settings import BACKEND_EMAIL, BACKEND_EMAIL_PASS, BUSINESS_EMAIL


email_blueprint = Blueprint('email', __name__)
ping_blueprint = Blueprint('ping', __name__)


def send_email_view():
    request_data = request.get_json()
    person = request_data.get('name')
    email = request_data.get('email')
    message = request_data.get('message')
    recaptcha = request_data.get('recaptcha')  # todo add integration/unit tests  for this

    try:
        validate_recaptcha(recaptcha)

        subject = f'Message sent from {person} with email {email}'
        full_message = f'Subject: {subject}\n\n{message}\n\nRegards, {person}'

        if send_email(full_message):
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.SUCCESSFULLY_SENT_EMAIL,
                                     status_code=StatusCodes.SUCCESSFULLY_CREATED)
        else:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.ERROR_FAILED_TO_SEND_EMAIL,
                                     status_code=StatusCodes.INTERNAL_SERVER_ERROR)
    except InvalidRecaptchaException:
        response = AuthenticationResponse(status='fail',
                                          message=ResponseConstants.INVALID_RECAPTCHA_ERROR,
                                          status_code=StatusCodes.BAD_REQUEST)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.POST_PICTURE_FAIL,
                                 status_code=StatusCodes.INTERNAL_SERVER_ERROR)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


def send_email(message):
    gmail_port = 465
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', gmail_port, context=context) as server:
        server.login(BACKEND_EMAIL, BACKEND_EMAIL_PASS)
        server.sendmail(BACKEND_EMAIL, BUSINESS_EMAIL, message)
        server.quit()

    return True


email_blueprint.add_url_rule('/send_email', view_func=send_email_view, methods=['POST'])


def ping():
    return "Ping"


ping_blueprint.add_url_rule('/ping', view_func=ping, methods=['GET', 'POST'])

