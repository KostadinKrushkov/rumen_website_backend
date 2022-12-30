from flask import Blueprint, request, make_response, jsonify

from project.common.constants import ResponseConstants, StatusCodes
from project.database.dtos.blog_dto import BlogDTO
from project.database.gateways.blog_gateway import BlogGateway
from project.flask.blueprints.auth.authentication_utils import authorization_required
from project.flask.blueprints.blog.blog_exceptions import BlogNotFound, BlogMissingTitle
from project.flask.blueprints.response_objects import BasicResponse

blog_blueprint = Blueprint('blog', __name__)
gateway = BlogGateway()


def get_all_blogs():
    try:
        all_blogs = gateway.get_all()
        serialized_blogs = [blog.__dict__ for blog in all_blogs]
        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.GET_ALL_BLOGS_SUCCESS,
                                 status_code=StatusCodes.SUCCESS,
                                 json=serialized_blogs)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_ALL_BLOGS_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


def get_blog():
    title = request.args.get('title')
    if not title:
        return get_all_blogs()
    try:
        blog = gateway.get_by_title(title)
        if blog is None:
            raise BlogNotFound()
        serialized_blog = blog.__dict__
        response = BasicResponse(status=ResponseConstants.SUCCESS,
                                 message=ResponseConstants.GET_BLOG_BY_TITLE_SUCCESS,
                                 status_code=StatusCodes.SUCCESS,
                                 json=serialized_blog)
    except BlogNotFound:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_BLOG_BY_TITLE_NOT_FOUND,
                                 status_code=StatusCodes.BAD_REQUEST)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.GET_BLOG_BY_TITLE_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


@authorization_required
def add_blog():
    blog_json = request.get_json()
    blog = BlogDTO(blog_json['title'], blog_json['content'], blog_json['image'])

    try:
        if gateway.save(blog) == 1:
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.POST_BLOG_SUCCESS,
                                     status_code=StatusCodes.SUCCESSFULLY_CREATED)
        else:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.POST_BLOG_FAIL_DUPLICATE,
                                     status_code=StatusCodes.BAD_REQUEST)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.POST_BLOG_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


@authorization_required
def update_blog():
    blog_json = request.get_json()
    blog = BlogDTO(blog_json['title'], blog_json['content'], blog_json['image'])

    try:
        if gateway.update(blog) == 1:
            response = BasicResponse(status=ResponseConstants.SUCCESS,
                                     message=ResponseConstants.UPDATE_BLOG_SUCCESS,
                                     status_code=StatusCodes.SUCCESS)
        else:
            response = BasicResponse(status=ResponseConstants.FAILURE,
                                     message=ResponseConstants.UPDATE_BLOG_NOT_FOUND,
                                     status_code=StatusCodes.NOT_FOUND)
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.UPDATE_BLOG_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


@authorization_required
def delete_blog():
    title = request.args.get('title')
    try:
        if not title:
            raise BlogMissingTitle()

        if BlogGateway().delete_by_title(title) == 1:
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
    except Exception:
        response = BasicResponse(status=ResponseConstants.FAILURE,
                                 message=ResponseConstants.DELETE_BLOG_FAIL,
                                 status_code=StatusCodes.BAD_REQUEST)
    finally:
        return make_response(jsonify(response.__dict__), response.status_code)


blog_blueprint.add_url_rule('/blog', view_func=get_blog, methods=['GET'])
blog_blueprint.add_url_rule('/blog', view_func=add_blog, methods=['POST'])
blog_blueprint.add_url_rule('/blog', view_func=update_blog, methods=['PUT'])
blog_blueprint.add_url_rule('/blog', view_func=delete_blog, methods=['DELETE'])
