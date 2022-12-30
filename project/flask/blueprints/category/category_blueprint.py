from flask import Blueprint, request, make_response, jsonify
from pyodbc import IntegrityError

from project.common.constants import ResponseConstants, StatusCodes
from project.database.dtos.category_dto import CategoryDTO
from project.database.gateways.category_gateway import CategoryGateway
from project.flask.blueprints.auth.authentication_utils import authorization_required
from project.flask.blueprints.category.category_exceptions import CategoryNotFound, CategoryMissingName
from project.flask.blueprints.response_objects import BasicResponse

category_blueprint = Blueprint('category', __name__)
gateway = CategoryGateway()


def get_category_by_name(category_name):
    return gateway.get_by_name(category_name)


def get_all_categories():
    try:
        all_categories = gateway.get_all()
        serialized_categories = [category.__dict__ for category in all_categories]
        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.GET_ALL_CATEGORIES_SUCCESS,
                                 status_code=StatusCodes.SUCCESSFULLY_CREATED,
                                 json=serialized_categories)
        return make_response(jsonify(response.__dict__), response.status_code)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_ALL_CATEGORIES_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
        return make_response(jsonify(response.__dict__), response.status_code)


def get_category():
    name = request.args.get('name')
    if not name:
        return get_all_categories()

    try:
        category = get_category_by_name(name)
        if category is None:
            raise CategoryNotFound()
        serialized_category = category.__dict__
        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.GET_CATEGORY_BY_NAME_SUCCESS,
                                 status_code=StatusCodes.SUCCESS,
                                 json=serialized_category)
    except CategoryNotFound:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_CATEGORY_BY_NAME_NOT_FOUND,
                                 status_code=StatusCodes.BAD_REQUEST)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_CATEGORY_BY_NAME_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


@authorization_required
def add_category():
    try:
        category_json = request.get_json()
        category = CategoryDTO(name=category_json['name'],
                               weight=category_json['weight'],
                               enabled=category_json['enabled'],
                               is_subcategory=category_json['is_subcategory'])

        if gateway.save(category) == 1:
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.POST_CATEGORY_SUCCESS,
                                     status_code=StatusCodes.SUCCESSFULLY_CREATED)
        else:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.POST_CATEGORY_FAIL_DUPLICATE_OR_OTHER,
                                     status_code=StatusCodes.BAD_REQUEST)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.POST_CATEGORY_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


@authorization_required
def update_category():
    try:
        category_json = request.get_json()
        category = CategoryDTO(name=category_json['name'],
                               weight=category_json['weight'],
                               enabled=category_json['enabled'],
                               is_subcategory=category_json['is_subcategory'])

        if gateway.update(category) == 1:
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.UPDATE_CATEGORY_SUCCESS,
                                     status_code=StatusCodes.SUCCESSFULLY_CREATED)
        else:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.UPDATE_CATEGORY_NOT_FOUND,
                                     status_code=StatusCodes.NOT_FOUND)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.UPDATE_CATEGORY_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


@authorization_required
def delete_category():
    try:
        category_name = request.args.get('name')
        if not category_name:
            raise CategoryMissingName()

        if gateway.delete_by_name(category_name) == 1:
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.DELETE_CATEGORY_SUCCESS,
                                     status_code=StatusCodes.SUCCESS)
        else:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.DELETE_CATEGORY_FAIL_NOT_FOUND,
                                     status_code=StatusCodes.BAD_REQUEST)
    except IntegrityError:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.DELETE_CATEGORY_FAIL_IS_IN_USE,
                                 status_code=StatusCodes.BAD_REQUEST)
    except CategoryMissingName:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.DELETE_CATEGORY_WRONG_PARAMETER,
                                 status_code=StatusCodes.BAD_REQUEST)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.DELETE_CATEGORY_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


category_blueprint.add_url_rule('/category', view_func=get_category, methods=['GET'])
category_blueprint.add_url_rule('/category', view_func=add_category, methods=['POST'])
category_blueprint.add_url_rule('/category', view_func=update_category, methods=['PUT'])
category_blueprint.add_url_rule('/category', view_func=delete_category, methods=['DELETE'])
