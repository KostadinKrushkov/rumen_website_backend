from flask import Blueprint, request, make_response, jsonify

from project.common.constants import ResponseConstants, StatusCodes
from project.database.gateways.picture_gateway import PictureGateway
from project.flask.blueprints.auth.authentication_utils import authorization_required
from project.flask.blueprints.category.category_exceptions import CategoryNotFound
from project.flask.blueprints.picture.picture_blueprint_utils import get_picture_dto_from_json
from project.flask.blueprints.picture.picture_exceptions import PictureNotFound
from project.flask.blueprints.response_objects import BasicResponse

picture_blueprint = Blueprint('picture', __name__)
gateway = PictureGateway()


def get_all_pictures():
    try:
        serialized_pictures = [picture.as_frontend_object().__dict__ for picture in gateway.get_all()]

        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.GET_ALL_PICTURES_SUCCESS,
                                 status_code=StatusCodes.SUCCESS,
                                 json=serialized_pictures)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_ALL_PICTURES_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


def get_home_pictures():  # TODO unit or integ test
    filename = r'project/flask/blueprints/picture/home_displayed_pictures.txt'
    picture_titles = open(filename).read().splitlines()

    try:
        home_pictures_dtos = []
        for picture in [picture.as_frontend_object().__dict__ for picture in gateway.get_all()]:
            if picture.get('title') in picture_titles:
                home_pictures_dtos.append(picture)

        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.GET_PICTURE_BY_TITLE_SUCCESS,
                                 status_code=StatusCodes.SUCCESS,
                                 json=home_pictures_dtos)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_PICTURE_FOR_HOME,
                                 status_code=StatusCodes.INTERNAL_SERVER_ERROR)

    return make_response(jsonify(response.__dict__), response.status_code)


def get_picture():
    title = request.args.get('title')
    if not title:
        return get_all_pictures()

    try:
        picture = gateway.get_by_title(title)
        if picture is None:
            raise PictureNotFound()
        serialized_picture = picture.__dict__
        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.GET_PICTURE_BY_TITLE_SUCCESS,
                                 status_code=StatusCodes.SUCCESS,
                                 json=serialized_picture)
    except PictureNotFound:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_PICTURE_BY_TITLE_NOT_FOUND,
                                 status_code=StatusCodes.BAD_REQUEST)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_PICTURE_BY_TITLE_FAIL,
                                 status_code=StatusCodes.INTERNAL_SERVER_ERROR)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


@authorization_required
def add_picture():
    try:
        picture_json = request.get_json()
        picture = get_picture_dto_from_json(picture_json)

        if gateway.save(picture) == 1:
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.POST_PICTURE_SUCCESS,
                                     status_code=StatusCodes.SUCCESSFULLY_CREATED)
        else:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.POST_PICTURE_FAIL_DUPLICATE_OR_OTHER,
                                     status_code=StatusCodes.BAD_REQUEST)
    except CategoryNotFound as e:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=str(e),
                                 status_code=StatusCodes.NOT_FOUND)
    except Exception as e:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.POST_PICTURE_FAIL,
                                 status_code=StatusCodes.INTERNAL_SERVER_ERROR)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


@authorization_required
def update_picture():
    picture_json = request.get_json()
    try:
        picture = get_picture_dto_from_json(picture_json)
    except CategoryNotFound as e:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=str(e),
                                 status_code=StatusCodes.NOT_FOUND)
        return make_response(jsonify(response.__dict__), response.status_code)
    try:
        if gateway.update(picture) == 1:
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.UPDATE_PICTURE_SUCCESS,
                                     status_code=StatusCodes.SUCCESSFULLY_CREATED)
            return make_response(jsonify(response.__dict__), response.status_code)
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.UPDATE_PICTURE_NOT_FOUND,
                                 status_code=StatusCodes.NOT_FOUND)
        return make_response(jsonify(response.__dict__), response.status_code)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.UPDATE_PICTURE_FAIL,
                                 status_code=StatusCodes.INTERNAL_SERVER_ERROR)
        return make_response(jsonify(response.__dict__), response.status_code)


@authorization_required
def delete_picture():
    title = request.args.get('title')
    if not title:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.DELETE_PICTURE_WRONG_PARAMETER,
                                 status_code=StatusCodes.BAD_REQUEST)
        return make_response(jsonify(response.__dict__), response.status_code)

    try:
        if gateway.delete_by_title(title) == 1:
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.DELETE_PICTURE_SUCCESS,
                                     status_code=StatusCodes.SUCCESS)
            return make_response(jsonify(response.__dict__), response.status_code)
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.DELETE_PICTURE_FAIL_NOT_FOUND,
                                 status_code=StatusCodes.NOT_FOUND)
        return make_response(jsonify(response.__dict__), response.status_code)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.DELETE_PICTURE_FAIL,
                                 status_code=StatusCodes.INTERNAL_SERVER_ERROR)
        return make_response(jsonify(response.__dict__), response.status_code)


picture_blueprint.add_url_rule('/home/pictures', view_func=get_home_pictures, methods=['GET'])
picture_blueprint.add_url_rule('/picture', view_func=get_picture, methods=['GET'])
picture_blueprint.add_url_rule('/picture', view_func=add_picture, methods=['POST'])
picture_blueprint.add_url_rule('/picture', view_func=update_picture, methods=['PUT'])
picture_blueprint.add_url_rule('/picture', view_func=delete_picture, methods=['DELETE'])
