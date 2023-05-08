import json
import logging

from flask import Blueprint, request
from pyodbc import IntegrityError

from project.common.constants import ResponseConstants, StatusCodes, EndpointPaths
from project.common.decorators import jsonify_response
from project.database.gateways.category_gateway import CategoryGateway
from project.flask.blueprints.auth.authentication_utils import authorization_required
from project.flask.blueprints.category.category_blueprint_utils import get_category_dto_from_json
from project.flask.blueprints.category.category_exceptions import CategoryNotFound, CategoryMissingName, \
    DuplicateCategoryName
from project.flask.blueprints.response_objects import BasicResponse

category_blueprint = Blueprint('category', __name__)
gateway = CategoryGateway()


def get_category_by_name(category_name):
    return gateway.get_by_name(category_name)


def get_all_categories():
    return _get_categories(False)


def get_enabled_categories():
    return _get_categories(True)


def _get_categories(enabled_only):
    try:
        categories = gateway.get_enabled() if enabled_only else gateway.get_all()
        serialized_categories = [category.__dict__ for category in categories]
        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.GET_CATEGORIES_SUCCESS,
                                 status_code=StatusCodes.SUCCESSFULLY_CREATED,
                                 json=serialized_categories)
    except Exception as e:
        logging.error(f'Getting all categories failed with exception "{e}".')
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_CATEGORIES_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    return response


@jsonify_response
def get_category():
    name = request.args.get('name')
    enabled_only = request.args.get('enabled_only', default=False, type=json.loads)

    if not name:
        return get_enabled_categories() if enabled_only else get_all_categories()

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
    return response


@authorization_required
def add_category():
    category_json = request.get_json()

    try:
        category = get_category_dto_from_json(category_json)

        gateway.save(category)
        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.POST_CATEGORY_SUCCESS,
                                 status_code=StatusCodes.SUCCESSFULLY_CREATED)
    except DuplicateCategoryName:
        logging.error(f'Failed to save category as there was already an existing category with name {category_json.get("name")}')
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.POST_CATEGORY_FAIL_DUPLICATE_OR_OTHER,
                                 status_code=StatusCodes.BAD_REQUEST)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.POST_CATEGORY_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    return response


@authorization_required
def update_category():
    category_json = request.get_json()

    try:
        category = get_category_dto_from_json(category_json)

        if gateway.update(category):
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
    return response


@authorization_required
def delete_category():
    try:
        category_name = request.args.get('name')
        if not category_name:
            raise CategoryMissingName()

        if gateway.delete_by_name(category_name):
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
    return response


category_blueprint.add_url_rule(EndpointPaths.CATEGORY, view_func=get_category, methods=['GET'])
category_blueprint.add_url_rule(EndpointPaths.CATEGORY, view_func=add_category, methods=['POST'])
category_blueprint.add_url_rule(EndpointPaths.CATEGORY, view_func=update_category, methods=['PUT'])
category_blueprint.add_url_rule(EndpointPaths.CATEGORY, view_func=delete_category, methods=['DELETE'])
