from unittest import mock
from unittest.mock import patch

import pytest

from project.common.constants import ResponseConstants, StatusCodes
from project.database.database_controller import DatabaseController
from project.database.dtos.blog_dto import BlogDTO
from project.database.gateways.blog_gateway import BlogGateway
from project.flask.blueprints.blog.blog_blueprint_utils import get_blog_dto_from_json
from tests.integration_tests.api_requests import send_post_blog_request, send_get_blog_request, \
    send_get_blog_by_title_request, send_update_blog_request, send_delete_blog_request
from tests.integration_tests.blueprints.test_stubs import get_stub_blog
from tests.integration_tests.testing_utils import assert_response_matches_expected

stubbed_blog = get_stub_blog()


@pytest.fixture
def create_starting_blog(authorized_client):
    response = send_post_blog_request(authorized_client, stubbed_blog)
    assert response['status_code'] == StatusCodes.SUCCESSFULLY_CREATED


class TestBlogAPI:
    gateway = BlogGateway()

    def _assert_blog_is_saved(self, expected_blog, blogs_list=None):
        blogs_list = blogs_list if blogs_list is not None else list(self.gateway.get_all())
        blog = blogs_list[0] if isinstance(blogs_list[0], BlogDTO) else BlogDTO.from_dict(blogs_list[0])

        self._assert_blog_matches_expected(expected_blog, blog)

    @staticmethod
    def _assert_blog_matches_expected(expected_blog, blog):
        assert blog.title == expected_blog.get('title')
        assert blog.content == expected_blog.get('content')

    def test_get_blog_by_title_successfully(self, unauthenticated_client, create_starting_blog):
        response = send_get_blog_by_title_request(unauthenticated_client, stubbed_blog)
        self._assert_blog_is_saved(response['json'])
        assert_response_matches_expected(response, code=StatusCodes.SUCCESS, status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.GET_BLOG_BY_TITLE_SUCCESS)

    def test_get_blog_fail_on_missing_title(self, unauthenticated_client):
        blog = stubbed_blog.copy()
        blog['title'] = 'Wrong title'
        response = send_get_blog_by_title_request(unauthenticated_client, blog)
        assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.GET_BLOG_BY_TITLE_NOT_FOUND)

    def test_get_blog_fail_on_internal_error(self, unauthenticated_client):
        error_mock = mock.Mock()
        error_mock.side_effect = Exception
        with patch.object(BlogGateway, 'get_by_title', error_mock):
            response = send_get_blog_by_title_request(unauthenticated_client, stubbed_blog)
            assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                             message=ResponseConstants.GET_BLOG_BY_TITLE_FAIL)

    def test_get_blogs_successfully(self, unauthenticated_client, create_starting_blog):
        response = send_get_blog_request(unauthenticated_client)
        self._assert_blog_is_saved(get_blog_dto_from_json(stubbed_blog).frontend_object, response['json'])
        assert_response_matches_expected(response, code=StatusCodes.SUCCESS, status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.GET_ALL_BLOGS_SUCCESS)

    def test_get_blogs_fails_on_internal_error(self, unauthenticated_client):
        error_mock = mock.Mock()
        error_mock.side_effect = Exception
        with patch.object(BlogGateway, 'get_all_compressed', error_mock):
            response = send_get_blog_request(unauthenticated_client)
        assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.GET_ALL_BLOGS_FAIL)

    def test_create_blog_successfully(self, authorized_client):
        response = send_post_blog_request(authorized_client, stubbed_blog)
        self._assert_blog_is_saved(stubbed_blog)
        assert_response_matches_expected(response, code=StatusCodes.SUCCESSFULLY_CREATED, status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.POST_BLOG_SUCCESS)

    def test_create_blog_fails_on_duplicate_key(self, authorized_client, create_starting_blog):
        response = send_post_blog_request(authorized_client, stubbed_blog)
        assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.POST_BLOG_FAIL_DUPLICATE)

    def test_create_blog_fails_on_internal_error(self, authorized_client):
        error_mock = mock.Mock()
        error_mock.side_effect = Exception
        with patch.object(BlogGateway, 'save', error_mock):
            response = send_post_blog_request(authorized_client, stubbed_blog)
            assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                             message=ResponseConstants.POST_BLOG_FAIL)

    def test_create_blog_fails_on_unauthenticated_user(self, unauthenticated_client):
        response = send_post_blog_request(unauthenticated_client, stubbed_blog)
        assert_response_matches_expected(response, code=StatusCodes.UNAUTHENTICATED, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.ERROR_USER_IS_NOT_AUTHENTICATED)

    def test_create_blog_fails_on_unauthorized_user(self, authenticated_client):
        response = send_post_blog_request(authenticated_client, stubbed_blog)
        assert_response_matches_expected(response, code=StatusCodes.UNAUTHORIZED, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.ERROR_USER_IS_NOT_AUTHORIZED)

    def test_update_blog_successfully(self, create_starting_blog, authorized_client):
        blog = stubbed_blog.copy()
        blog['content'] = "Actually, if you are a cow..."
        response = send_update_blog_request(authorized_client, blog)
        self._assert_blog_is_saved(blog)
        assert_response_matches_expected(response, code=StatusCodes.SUCCESS, status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.UPDATE_BLOG_SUCCESS)

    def test_update_blog_fails_on_not_found(self, authorized_client):
        response = send_update_blog_request(authorized_client, stubbed_blog)
        assert_response_matches_expected(response, code=StatusCodes.NOT_FOUND, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.UPDATE_BLOG_NOT_FOUND)

    def test_update_blog_fails_on_internal_error(self, authorized_client):
        error_mock = mock.Mock()
        error_mock.side_effect = Exception
        with patch.object(DatabaseController, 'execute_get_row_count', error_mock):
            response = send_update_blog_request(authorized_client, stubbed_blog)
        assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.UPDATE_BLOG_FAIL)

    def test_update_blog_fails_on_unauthenticated_user(self, create_starting_blog, unauthenticated_client):
        response = send_update_blog_request(unauthenticated_client, stubbed_blog)
        assert_response_matches_expected(response, code=StatusCodes.UNAUTHENTICATED, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.ERROR_USER_IS_NOT_AUTHENTICATED)

    def test_update_blog_fails_on_unauthorized_user(self, create_starting_blog, authenticated_client):
        response = send_update_blog_request(authenticated_client, stubbed_blog)
        assert_response_matches_expected(response, code=StatusCodes.UNAUTHORIZED, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.ERROR_USER_IS_NOT_AUTHORIZED)

    def test_delete_blog_successfully(self, create_starting_blog, authorized_client):
        response = send_delete_blog_request(authorized_client, stubbed_blog)
        assert list(self.gateway.get_all()) == []
        assert_response_matches_expected(response, code=StatusCodes.SUCCESS, status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.DELETE_BLOG_SUCCESS)

    def test_delete_fails_on_missing_title_param(self, create_starting_blog, authorized_client):
        response = send_delete_blog_request(authorized_client, stubbed_blog, {})
        assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.DELETE_BLOG_WRONG_PARAMETER)

    def test_delete_fails_on_blog_not_found(self, authorized_client):
        response = send_delete_blog_request(authorized_client, stubbed_blog)
        assert_response_matches_expected(response, code=StatusCodes.NOT_FOUND, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.DELETE_BLOG_FAIL_NOT_FOUND)

    def test_delete_fails_on_internal_error(self, authorized_client):
        error_mock = mock.Mock()
        error_mock.side_effect = Exception
        with patch.object(DatabaseController, 'execute_get_row_count', error_mock):
            response = send_delete_blog_request(authorized_client, stubbed_blog)
        assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.DELETE_BLOG_FAIL)

    def test_delete_blog_fails_on_unauthenticated_user(self, create_starting_blog, unauthenticated_client):
        response = send_delete_blog_request(unauthenticated_client, stubbed_blog)
        assert_response_matches_expected(response, code=StatusCodes.UNAUTHENTICATED, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.ERROR_USER_IS_NOT_AUTHENTICATED)

    def test_delete_blog_fails_on_unauthorized_user(self, create_starting_blog, authenticated_client):
        response = send_delete_blog_request(authenticated_client, stubbed_blog)
        assert_response_matches_expected(response, code=StatusCodes.UNAUTHORIZED, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.ERROR_USER_IS_NOT_AUTHORIZED)
