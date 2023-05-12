import logging

from flask import Blueprint, request

from project.common.constants import ResponseConstants, StatusCodes, EndpointPaths
from project.common.decorators import jsonify_response, log_execution_time
from project.database.gateways.picture_gateway import PictureGateway
from project.flask.blueprints.auth.authentication_utils import authorization_required
from project.flask.blueprints.category.category_exceptions import CategoryNotFound
from project.flask.blueprints.picture.picture_blueprint_utils import get_picture_dto_from_json
from project.flask.blueprints.picture.picture_exceptions import PictureNotFound, DuplicatePictureTitle
from project.flask.blueprints.response_objects import BasicResponse
from project.settings import Config

picture_blueprint = Blueprint('picture', __name__)
gateway = PictureGateway()


def get_pictures():
    categories = request.args.getlist('category')
    years = request.args.getlist('year')
    cursor_picture_title = request.args.get('cursor_picture_title', '')
    limit = int(request.args.get('limit', Config.NUM_PICTURES_TO_EXTEND_LOAD))

    try:
        serialized_pictures = [picture.as_frontend_object().__dict__ for picture in
                               gateway.get_pictures(categories=categories, years=years,
                                                    cursor_picture_title=cursor_picture_title, limit=limit)]

        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.GET_ALL_PICTURES_SUCCESS,
                                 status_code=StatusCodes.SUCCESS,
                                 json=serialized_pictures)
    except Exception as e:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_ALL_PICTURES_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    return response


@jsonify_response
@log_execution_time
def get_home_pictures():
    picture_titles = open(Config.HOME_PICTURES_PATH).read().splitlines()

    try:
        home_pictures_dtos = []
        for picture in [picture.as_frontend_object().__dict__ for picture in gateway.get_all()]:
            if picture.get('title') in picture_titles:
                home_pictures_dtos.append(picture)

        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.GET_FAVOURITE_PICTURES_SUCCESS,
                                 status_code=StatusCodes.SUCCESS,
                                 json=home_pictures_dtos)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_FAVOURITE_PICTURES_FAIL,
                                 status_code=StatusCodes.INTERNAL_SERVER_ERROR)

    return response


@jsonify_response
@log_execution_time
def get_picture():
    title = request.args.get('title')
    if not title:
        return get_pictures()
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

    return response


@jsonify_response
@log_execution_time
def get_picture_years():
    try:
        years = [row['year'] for row in gateway.get_distinct_picture_years()]
        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.GET_PICTURE_YEARS_SUCCESS,
                                 status_code=StatusCodes.SUCCESS,
                                 json=years)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_PICTURE_YEARS_FAIL,
                                 status_code=StatusCodes.INTERNAL_SERVER_ERROR)

    return response


@authorization_required
def add_picture():
    picture_json = request.get_json()

    try:
        picture = get_picture_dto_from_json(picture_json)

        gateway.save(picture)
        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.POST_PICTURE_SUCCESS,
                                 status_code=StatusCodes.SUCCESSFULLY_CREATED)
    except DuplicatePictureTitle:
        logging.error(
            f'Failed to save picture as there was already an existing picture with title {picture_json.get("title")}')
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.POST_PICTURE_FAIL_DUPLICATE_OR_OTHER,
                                 status_code=StatusCodes.BAD_REQUEST)
    except CategoryNotFound as e:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=str(e),
                                 status_code=StatusCodes.NOT_FOUND)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.POST_PICTURE_FAIL,
                                 status_code=StatusCodes.INTERNAL_SERVER_ERROR)
    return response


@authorization_required
def update_picture():
    picture_json = request.get_json()
    try:
        picture = get_picture_dto_from_json(picture_json)
    except CategoryNotFound as e:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=str(e),
                                 status_code=StatusCodes.NOT_FOUND)
        return response
    try:
        if gateway.update(picture):
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.UPDATE_PICTURE_SUCCESS,
                                     status_code=StatusCodes.SUCCESSFULLY_CREATED)
        else:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.UPDATE_PICTURE_NOT_FOUND,
                                     status_code=StatusCodes.NOT_FOUND)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.UPDATE_PICTURE_FAIL,
                                 status_code=StatusCodes.INTERNAL_SERVER_ERROR)

    return response


@authorization_required
def update_favourite_pictures():
    pictures_json = request.get_json()
    filename = Config.HOME_PICTURES_PATH

    try:
        with open(filename, 'w+') as file:
            file.writelines('\n'.join([picture['title'] for picture in pictures_json]))
        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.UPDATE_FAVOURITE_PICTURES_SUCCESS,
                                 status_code=StatusCodes.SUCCESSFULLY_CREATED)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.UPDATE_FAVOURITE_PICTURES_FAIL,
                                 status_code=StatusCodes.INTERNAL_SERVER_ERROR)
    return response


@authorization_required
def delete_picture():
    title = request.args.get('title')
    if not title:
        return BasicResponse(status=ResponseConstants.FAILURE,
                             message=ResponseConstants.DELETE_PICTURE_WRONG_PARAMETER,
                             status_code=StatusCodes.BAD_REQUEST)

    try:
        if gateway.delete_by_title(title):
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.DELETE_PICTURE_SUCCESS,
                                     status_code=StatusCodes.SUCCESS)
        else:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.DELETE_PICTURE_FAIL_NOT_FOUND,
                                     status_code=StatusCodes.NOT_FOUND)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.DELETE_PICTURE_FAIL,
                                 status_code=StatusCodes.INTERNAL_SERVER_ERROR)

    return response


picture_blueprint.add_url_rule(EndpointPaths.HOME_PICTURES, view_func=get_home_pictures, methods=['GET'])
picture_blueprint.add_url_rule(EndpointPaths.HOME_PICTURES, view_func=update_favourite_pictures, methods=['PUT'])
picture_blueprint.add_url_rule(EndpointPaths.PICTURE_YEARS, view_func=get_picture_years, methods=['GET'])
picture_blueprint.add_url_rule(EndpointPaths.PICTURE, view_func=get_picture, methods=['GET'])
picture_blueprint.add_url_rule(EndpointPaths.PICTURE, view_func=add_picture, methods=['POST'])
picture_blueprint.add_url_rule(EndpointPaths.PICTURE, view_func=update_picture, methods=['PUT'])
picture_blueprint.add_url_rule(EndpointPaths.PICTURE, view_func=delete_picture, methods=['DELETE'])
