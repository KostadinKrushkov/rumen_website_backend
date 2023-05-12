import logging

from flask import Blueprint, request, make_response, jsonify
from flask_login import login_user, logout_user, login_required

from project.auth.user import User
from project.common.constants import ResponseConstants, StatusCodes, EndpointPaths
from project.database.dtos.user_dto import UserDTO
from project.database.gateways.user_gateway import UserGateway
from project.flask.blueprints.auth.authentication_exceptions import IncorrectFormData, InvalidRecaptchaException, \
    UserNotFoundException, PasswordDoesNotMatchException
from project.flask.blueprints.auth.authentication_utils import hash_pass, \
    set_cors_headers_and_token, validate_recaptcha, does_hash_match_pass
from project.flask.blueprints.response_objects import BasicResponse
from project.flask.blueprints.auth.credentials_validator import CredentialsValidator

auth_blueprint = Blueprint('auth', __name__, url_prefix=EndpointPaths.AUTH)
validator = CredentialsValidator()
gateway = UserGateway()


def register():
    """Normal users can only be registered with this endpoint. To become an admin user either update manually or use the
    user gateway's update method"""
    request_data = request.get_json()
    user_json = request_data.get('user')
    auth_token = None

    try:
        recaptcha = request_data.get('recaptcha')
        validate_recaptcha(recaptcha)

        if not validator.validate_user_credentials(user_json):
            raise IncorrectFormData(ResponseConstants.INCORRECT_CREDENTIALS_FOR_REGISTER)

        user_json['password'] = hash_pass(user_json.get('password'))
        user_dto = UserDTO(email=user_json.get('email').lower(),
                           username=user_json.get('username'),
                           password=user_json.get('password'))

        if gateway.save(user_dto) != 1:
            raise IncorrectFormData(ResponseConstants.ERROR_USER_ALREADY_EXISTS)

        new_user = gateway.get_by_username(user_dto.username)
        login_user(User.from_dto(new_user), remember=True)

        # generate the auth token
        auth_token = User.encode_auth_token(new_user.id)
        response = BasicResponse(status=ResponseConstants.SUCCESS, message=ResponseConstants.SUCCESSFULLY_REGISTERED,
                                 status_code=StatusCodes.SUCCESSFULLY_CREATED)
    except InvalidRecaptchaException:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.INVALID_RECAPTCHA_ERROR,
                                 status_code=StatusCodes.BAD_REQUEST)
    except IncorrectFormData as e:
        response = BasicResponse(status=ResponseConstants.FAILURE, message=str(e), status_code=StatusCodes.BAD_REQUEST)
    except Exception as e:
        response = BasicResponse(status=ResponseConstants.FAILURE, message=ResponseConstants.GENERIC_SERVER_ERROR,
                                 status_code=StatusCodes.BAD_REQUEST)
    finally:
        full_response = make_response(jsonify(response.__dict__), response.status_code)

    if auth_token is not None:
        set_cors_headers_and_token(full_response, auth_token)

    return full_response


def login():
    request_data = request.get_json()
    user_json = request_data.get('user')
    auth_token = None
    response = None

    try:
        recaptcha = request_data.get('recaptcha')
        validate_recaptcha(recaptcha)

        # check if user already exists
        saved_user = gateway.get_by_username(user_json.get('username'))

        if not saved_user:
            raise UserNotFoundException()

        if not does_hash_match_pass(saved_user.password, user_json.get('password')):
            raise PasswordDoesNotMatchException()

        login_user(User.from_dto(saved_user), remember=True)

        auth_token = User.encode_auth_token(saved_user.id)
        message = ResponseConstants.SUCCESSFULLY_LOGGED_IN_AS_ADMIN \
            if saved_user.is_admin and saved_user.is_verified else ResponseConstants.SUCCESSFULLY_LOGGED_IN

        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=message,
                                 status_code=StatusCodes.SUCCESS)
    except (UserNotFoundException, PasswordDoesNotMatchException):
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.INCORRECT_CREDENTIALS_FOR_LOGIN,
                                 status_code=StatusCodes.BAD_REQUEST)
    except InvalidRecaptchaException:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.INVALID_RECAPTCHA_ERROR,
                                 status_code=StatusCodes.BAD_REQUEST)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GENERIC_SERVER_ERROR,
                                 status_code=StatusCodes.BAD_REQUEST)
    finally:
        logging.debug(f'Login request for user: {user_json.get("username")}, response {response}')
        full_response = make_response(jsonify(response.__dict__), response.status_code)

    # ### Used for development due to problems with not using domain name
    # saved_user = gateway.get_by_username(user_json.get('username'))
    # login_user(User.from_dto(saved_user), remember=True)
    #
    # auth_token = User.encode_auth_token(saved_user.id)
    # message = ResponseConstants.SUCCESSFULLY_LOGGED_IN_AS_ADMIN \
    #     if saved_user.is_admin and saved_user.is_verified else ResponseConstants.SUCCESSFULLY_LOGGED_IN
    # response = BasicResponse(status='success',
    #                          message=message,
    #                          status_code=StatusCodes.SUCCESS)
    # full_response = make_response(jsonify(response.__dict__), response.status_code)
    # ###

    if auth_token is not None:
        set_cors_headers_and_token(full_response, auth_token)

    return full_response


@login_required
def logout():
    logout_user()
    response = BasicResponse(ResponseConstants.SUCCESS, ResponseConstants.SUCCESSFULLY_LOGGED_OUT, StatusCodes.SUCCESS)
    return make_response(jsonify(response.__dict__), response.status_code)


auth_blueprint.add_url_rule(EndpointPaths.REGISTER, view_func=register, methods=['POST'])
auth_blueprint.add_url_rule(EndpointPaths.LOGIN, view_func=login, methods=['POST', 'GET'])
auth_blueprint.add_url_rule(EndpointPaths.LOGOUT, view_func=logout, methods=['POST'])
