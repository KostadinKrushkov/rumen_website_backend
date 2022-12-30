from functools import wraps

import jwt
from flask import make_response, jsonify, request
from flask_login import current_user, logout_user
import bcrypt as bcr

from project.auth.user import User
from project.common.constants import ResponseConstants, StatusCodes
from project.database.gateways.user_gateway import UserGateway
from project.flask.blueprints.auth.authentication_exceptions import InvalidAuthToken, MissingAuthToken
from project.flask.blueprints.response_objects import AuthenticationResponse


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


def set_cors_headers_and_token(response, token):
    response.headers['Access-Control-Allow-Origin'] = 'https://localhost:4200'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Request-Headers'] = 'X-Requested-With, accept, content-type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
    response.set_cookie('token', token, httponly=True, samesite='None', secure=True)


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
        response = AuthenticationResponse(status='fail',
                                          message=ResponseConstants.MISSING_TOKEN,
                                          status_code=StatusCodes.UNAUTHENTICATED)
    except jwt.ExpiredSignatureError:
        response = AuthenticationResponse(status='fail',
                                          message=ResponseConstants.EXPIRED_TOKEN,
                                          status_code=StatusCodes.UNAUTHENTICATED)
    except (InvalidAuthToken, jwt.InvalidTokenError):
        response = AuthenticationResponse(status='fail',
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
            return make_response(jsonify(response.__dict__), response.status_code)

        # TODO enable it and test it when you add ssl
        # if not current_user.is_authenticated:
        #     response = AuthenticationResponse(status='fail',
        #                                       message=ResponseConstants.ERROR_USER_IS_NOT_AUTHENTICATED,
        #                                       status_code=StatusCodes.UNAUTHENTICATED)
        # elif not current_user.is_verified:
        #     response = AuthenticationResponse(status='fail',
        #                                       message=ResponseConstants.ERROR_USER_IS_NOT_ACTIVE,
        #                                       status_code=StatusCodes.UNAUTHORIZED)
        # elif not current_user.is_admin:
        #     response = AuthenticationResponse(status='fail',
        #                                       message=ResponseConstants.ERROR_USER_IS_NOT_AUTHORIZED,
        #                                       status_code=StatusCodes.UNAUTHORIZED)
        # else:
        return func()
        # return make_response(jsonify(response.__dict__), response.status_code)

    return wrapper


