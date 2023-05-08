import sys
import requests
import jwt
import bcrypt as bcr
from flask import request
from flask_login import current_user, logout_user
from functools import wraps
from sqlalchemy.exc import ProgrammingError

from project.auth.user import User
from project.common.constants import ResponseConstants, StatusCodes
from project.common.decorators import disable_during_tests, generated_jsonified_response
from project.database.gateways.user_gateway import UserGateway
from project.flask.blueprints.auth.authentication_exceptions import InvalidAuthToken, MissingAuthToken, \
    InvalidRecaptchaException
from project.flask.blueprints.response_objects import BasicResponse
from project.settings import Config


def hash_pass(password):
    salt = bcr.gensalt()
    encoded_pass = password.encode()
    return bcr.hashpw(encoded_pass, salt).decode()


def does_hash_match_pass(hashed_pass, password):
    if not hashed_pass or not password:
        return False

    encoded_pass = password.encode()
    encoded_hash = hashed_pass.encode()
    return encoded_hash == bcr.hashpw(encoded_pass, encoded_hash)


def set_cors_headers_and_token(response, token, token_name='token', httponly=True):
    response.headers['Access-Control-Allow-Origin'] = 'https://localhost:4200'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Request-Headers'] = 'X-Requested-With, accept, content-type'
    response.headers['Access-Control-Allow-Headers'] = 'X-Requested-With, accept, content-type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.set_cookie(token_name, token, httponly=httponly, samesite='None', secure=True, path='/')


def validate_token_get_response_on_fail():
    response = None
    token = request.cookies.get('token')

    try:
        if not token:
            raise MissingAuthToken()
        user_id = User.decode_auth_token(token)
        if not UserGateway().get_by_id(user_id):
            raise InvalidAuthToken()
    except MissingAuthToken:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.MISSING_TOKEN,
                                 status_code=StatusCodes.UNAUTHENTICATED)
    except (jwt.ExpiredSignatureError, ProgrammingError):
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.EXPIRED_TOKEN,
                                 status_code=StatusCodes.INVALID_TOKEN)
    except (InvalidAuthToken, jwt.InvalidTokenError):
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.INVALID_TOKEN,
                                 status_code=StatusCodes.INVALID_TOKEN)
    if response is not None:
        logout_user()
    return response


def authorization_required(func):
    @wraps(func)
    def wrapper():
        response = validate_token_get_response_on_fail()

        if response is not None:
            return generated_jsonified_response(response)

        if not current_user.is_authenticated:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.ERROR_USER_IS_NOT_AUTHENTICATED,
                                     status_code=StatusCodes.UNAUTHENTICATED)
        elif not current_user.is_verified:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.ERROR_USER_IS_NOT_ACTIVE,
                                     status_code=StatusCodes.UNAUTHORIZED)
        elif not current_user.is_admin:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.ERROR_USER_IS_NOT_AUTHORIZED,
                                     status_code=StatusCodes.UNAUTHORIZED)
        else:
            response = func()
        return generated_jsonified_response(response)

    return wrapper


@disable_during_tests
def validate_recaptcha(recaptcha):
    if getattr(sys, '_called_from_test', False):
        return

    recaptcha_response = None
    if recaptcha:
        recaptcha_response = requests.post(url=Config.VERIFY_RECAPTCHA_URL,
                                           data={'secret': Config.RECAPTCHA_SECRET_KEY, 'response': recaptcha})

    if not recaptcha_response or recaptcha_response.status_code != StatusCodes.SUCCESS:
        raise InvalidRecaptchaException()
