from flask import Blueprint, request, make_response, jsonify
from flask_login import login_user, logout_user, login_required

from project.auth.user import User
from project.common.constants import ResponseConstants, StatusCodes
from project.database.dtos.user_dto import UserDTO
from project.database.gateways.user_gateway import UserGateway
from project.flask.blueprints.auth.authentication_exceptions import PasswordDoesNotMatchException, UserNotFoundException, \
    IncorrectFormData
from project.flask.blueprints.auth.authentication_utils import does_hash_match_pass, hash_pass, \
    set_cors_headers_and_token
from project.flask.blueprints.response_objects import AuthenticationResponse
from project.flask.blueprints.auth.credentials_validator import CredentialsValidator

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')
validator = CredentialsValidator()
gateway = UserGateway()


def register():
    """Normal users can only be registered with this endpoint. To become an admin user either update manually or use the
    user gateway's update method"""
    user_json = request.get_json()

    try:
        if not validator.validate_user_credentials(user_json):
            raise IncorrectFormData(ResponseConstants.INCORRECT_CREDENTIALS_FOR_REGISTER)

        user_json['password'] = hash_pass(user_json.get('password'))
        user_dto = UserDTO(email=user_json.get('email').lower(),
                           username=user_json.get('username'),
                           password=user_json.get('password'))

        if gateway.save(user_dto) != 1:
            raise IncorrectFormData(ResponseConstants.ERROR_USER_ALREADY_EXISTS)

        new_user = gateway.get_by_username(user_dto.username)

        # generate the auth token
        auth_token = User.encode_auth_token(new_user.id)
        response = AuthenticationResponse(status='success', message=ResponseConstants.SUCCESSFULLY_REGISTERED,
                                          status_code=StatusCodes.SUCCESSFULLY_CREATED,
                                          token=auth_token)
    except IncorrectFormData as e:
        response = AuthenticationResponse(status='fail', message=str(e), status_code=StatusCodes.BAD_REQUEST)
    except Exception:
        response = AuthenticationResponse(status='fail', message=ResponseConstants.GENERIC_SERVER_ERROR,
                                          status_code=StatusCodes.BAD_REQUEST)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


def login():
    user_json = request.get_json()
    auth_token = None

    try:
        # check if user already exists
        saved_user = gateway.get_by_username(user_json.get('username'))

        if not saved_user:
            raise UserNotFoundException()

        if not does_hash_match_pass(saved_user.password, user_json.get('password')):
            raise PasswordDoesNotMatchException()

        login_user(User.from_dto(saved_user), remember=True)  # TODO check after adding ssl if remember is necessary

        auth_token = User.encode_auth_token(saved_user.id)
        message = ResponseConstants.SUCCESSFULLY_LOGGED_IN_AS_ADMIN \
            if saved_user.is_admin and saved_user.is_verified else ResponseConstants.SUCCESSFULLY_LOGGED_IN  # TODO check if integration tests are working properly for this part
        # TODO to be removed when the ssl problem is fixed so the users can be autheorized correctly
        message = ResponseConstants.SUCCESSFULLY_LOGGED_IN_AS_ADMIN
        #
        response = AuthenticationResponse(status='success',
                                          message=message,
                                          status_code=StatusCodes.SUCCESS)
    except (UserNotFoundException, PasswordDoesNotMatchException):
        response = AuthenticationResponse(status='fail',
                                          message=ResponseConstants.INCORRECT_CREDENTIALS_FOR_LOGIN,
                                          status_code=StatusCodes.BAD_REQUEST)
    except Exception:
        response = AuthenticationResponse(status='fail',
                                          message=ResponseConstants.GENERIC_SERVER_ERROR,
                                          status_code=StatusCodes.BAD_REQUEST)
    finally:
        full_response = make_response(jsonify(response.__dict__), response.status_code)

    if auth_token is not None:
        set_cors_headers_and_token(full_response, auth_token)

    return full_response


@login_required
def logout():
    logout_user()
    response = AuthenticationResponse('success', ResponseConstants.SUCCESSFULLY_LOGGED_OUT, StatusCodes.SUCCESS)
    return make_response(jsonify(response.__dict__), response.status_code)


auth_blueprint.add_url_rule('/register', view_func=register, methods=['POST'])
auth_blueprint.add_url_rule('/login', view_func=login, methods=['POST', 'GET'])
auth_blueprint.add_url_rule('/logout', view_func=logout, methods=['POST'])
