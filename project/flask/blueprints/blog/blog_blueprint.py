import logging

from flask import Blueprint, request

from project.common.constants import ResponseConstants, StatusCodes, EndpointPaths
from project.common.decorators import jsonify_response, log_execution_time
from project.database.gateways.blog_gateway import BlogGateway
from project.flask.blueprints.auth.authentication_utils import authorization_required
from project.flask.blueprints.blog.blog_blueprint_utils import get_blog_dto_from_json
from project.flask.blueprints.blog.blog_exceptions import BlogNotFound, BlogMissingTitle, DuplicateBlogTitle
from project.flask.blueprints.response_objects import BasicResponse
from project.settings import Config

blog_blueprint = Blueprint('blog', __name__)
gateway = BlogGateway()


@log_execution_time
def get_all_blogs(compressed=True):
    cursor_blog_title = request.args.get('cursor_blog_title', '')
    limit = int(request.args.get('limit', Config.NUM_ITEMS_TO_EXTEND_LOAD))

    try:
        if compressed:
            all_blogs = gateway.get_all_compressed()
        else:
            all_blogs = gateway.get_all()

        serialized_blogs = []
        passed_cursor_blog = False if cursor_blog_title else True
        for blog in all_blogs:
            if len(serialized_blogs) < limit and passed_cursor_blog:
                serialized_blogs.append(blog.frontend_object)

            if blog.title == cursor_blog_title:
                passed_cursor_blog = True

        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.GET_ALL_BLOGS_SUCCESS,
                                 status_code=StatusCodes.SUCCESS,
                                 json=serialized_blogs)
    except Exception as e:
        logging.error(f'Getting all blogs failed with exception "{e}".')
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_ALL_BLOGS_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    return response


@jsonify_response
@log_execution_time
def get_blogs():
    title = request.args.get('title')
    if not title:
        return get_all_blogs()
    try:
        blog = gateway.get_by_title(title)
        if blog is None:
            raise BlogNotFound()
        serialized_blog = blog.frontend_object
        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.GET_BLOG_BY_TITLE_SUCCESS,
                                 status_code=StatusCodes.SUCCESS,
                                 json=serialized_blog)
    except BlogNotFound:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_BLOG_BY_TITLE_NOT_FOUND,
                                 status_code=StatusCodes.BAD_REQUEST)
    except Exception as e:
        logging.error(f'Getting blog "{title}" failed with exception "{e}".')
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_BLOG_BY_TITLE_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    return response


@authorization_required
def add_blog():
    blog_json = request.get_json()

    try:
        blog = get_blog_dto_from_json(blog_json)

        if gateway.save(blog):
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.POST_BLOG_SUCCESS,
                                     status_code=StatusCodes.SUCCESSFULLY_CREATED)
        else:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.POST_BLOG_FAIL_DUPLICATE,
                                     status_code=StatusCodes.BAD_REQUEST)
    except DuplicateBlogTitle:
        logging.error(
            f'Failed to save blog as there was already an existing blog with title {blog_json.get("title")}')
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.POST_BLOG_FAIL_DUPLICATE,
                                 status_code=StatusCodes.BAD_REQUEST)
    except Exception as e:
        logging.error(f'Adding a blog with params "{blog_json}" failed with exception "{e}".')
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.POST_BLOG_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    return response


@authorization_required
def update_blog():
    blog_json = request.get_json()

    try:
        blog = get_blog_dto_from_json(blog_json)

        if gateway.update(blog):
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.UPDATE_BLOG_SUCCESS,
                                     status_code=StatusCodes.SUCCESS)
        else:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.UPDATE_BLOG_NOT_FOUND,
                                     status_code=StatusCodes.NOT_FOUND)
    except Exception as e:
        logging.error(f'Updating a blog with params "{blog_json}", failed with exception "{e}".')
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.UPDATE_BLOG_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    return response


@authorization_required
def delete_blog():
    title = request.args.get('title')
    try:
        if not title:
            raise BlogMissingTitle()

        if BlogGateway().delete_by_title(title):
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.DELETE_BLOG_SUCCESS,
                                     status_code=StatusCodes.SUCCESS)
        else:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.DELETE_BLOG_FAIL_NOT_FOUND,
                                     status_code=StatusCodes.NOT_FOUND)
    except BlogMissingTitle:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.DELETE_BLOG_WRONG_PARAMETER,
                                 status_code=StatusCodes.BAD_REQUEST)
    except Exception as e:
        logging.error(f'Deleting a blog with request args "{request.args}" failed with exception "{e}".')
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.DELETE_BLOG_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    return response


blog_blueprint.add_url_rule(EndpointPaths.BLOG, view_func=get_blogs, methods=['GET'])
blog_blueprint.add_url_rule(EndpointPaths.BLOG, view_func=add_blog, methods=['POST'])
blog_blueprint.add_url_rule(EndpointPaths.BLOG, view_func=update_blog, methods=['PUT'])
blog_blueprint.add_url_rule(EndpointPaths.BLOG, view_func=delete_blog, methods=['DELETE'])
