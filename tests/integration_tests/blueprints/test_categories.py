from unittest import mock
from unittest.mock import patch

import pytest

from project.common.constants import ResponseConstants, StatusCodes
from project.database.dtos.category_dto import CategoryDTO
from project.database.gateways.category_gateway import CategoryGateway
from tests.integration_tests.api_requests import send_post_category_request, send_get_category_by_name_request, \
    send_update_category_request, send_delete_category_request
from tests.integration_tests.testing_utils import assert_response_matches_expected

stub_category_name = 'Category 1'
stubbed_category = {
    'name': stub_category_name,
    'weight': 1,
    'enabled': True,
    'is_subcategory': False
}


@pytest.fixture
def create_starting_category(authorized_client):
    response = send_post_category_request(authorized_client, stubbed_category)
    assert response['status_code'] == StatusCodes.SUCCESSFULLY_CREATED


class TestCategoryAPI:
    gateway = CategoryGateway()

    def _assert_category_is_saved(self, expected_category):
        category_dto = self.gateway.get_by_name(expected_category.get('name'))
        self._assert_category_matches_expected(expected_category, category_dto)

    @staticmethod
    def _assert_category_matches_expected(expected_category, category):
        assert category.name == expected_category.get('name')
        assert category.weight == expected_category.get('weight')
        assert category.enabled == expected_category.get('enabled')
        assert category.is_subcategory == expected_category.get('is_subcategory')

    def test_get_category_by_name_successfully(self, create_starting_category, unauthenticated_client):
        response = send_get_category_by_name_request(unauthenticated_client, stubbed_category)
        self._assert_category_matches_expected(stubbed_category, CategoryDTO(**response['json']))

        assert_response_matches_expected(response, code=StatusCodes.SUCCESS, status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.GET_CATEGORY_BY_NAME_SUCCESS)

    def test_get_category_by_name_fail_on_missing_name(self, unauthenticated_client):
        wrong_category = stubbed_category.copy()
        wrong_category['name'] = 'Wrong name'
        response = send_get_category_by_name_request(unauthenticated_client, wrong_category)
        assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.GET_CATEGORY_BY_NAME_NOT_FOUND)

    def test_get_category_by_name_fail_on_internal_error(self, unauthenticated_client):
        error_mock = mock.Mock()
        error_mock.side_effect = Exception
        with patch.object(CategoryGateway, 'get_by_name', error_mock):
            response = send_get_category_by_name_request(unauthenticated_client, stubbed_category)
            assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                             message=ResponseConstants.GET_CATEGORY_BY_NAME_FAIL)

    def test_create_category_successfully(self, authorized_client):
        response = send_post_category_request(authorized_client, stubbed_category)
        self._assert_category_is_saved(stubbed_category)
        assert_response_matches_expected(response, code=StatusCodes.SUCCESSFULLY_CREATED, status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.POST_CATEGORY_SUCCESS)

    def test_create_category_fails_on_duplicate_key(self, create_starting_category, authorized_client):
        response = send_post_category_request(authorized_client, stubbed_category)
        assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.POST_CATEGORY_FAIL_DUPLICATE_OR_OTHER)

    def test_create_category_fails_on_internal_error(self, authorized_client):
        error_mock = mock.Mock()
        error_mock.side_effect = Exception
        with patch.object(CategoryGateway, 'save', error_mock):
            response = send_post_category_request(authorized_client, stubbed_category)
            assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                             message=ResponseConstants.POST_CATEGORY_FAIL)

    def test_create_category_fails_on_unauthenticated_client(self, unauthenticated_client):

        response = send_post_category_request(unauthenticated_client, stubbed_category)
        assert_response_matches_expected(response, code=StatusCodes.UNAUTHENTICATED, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.ERROR_USER_IS_NOT_AUTHENTICATED)

    def test_create_category_fails_on_unauthorized_client(self, authenticated_client):
        response = send_post_category_request(authenticated_client, stubbed_category)
        assert_response_matches_expected(response, code=StatusCodes.UNAUTHORIZED, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.ERROR_USER_IS_NOT_AUTHORIZED)

    def test_update_category_successfully(self, create_starting_category, authorized_client):
        updated_category = stubbed_category.copy()
        updated_category['weight'] = 99
        response = send_update_category_request(authorized_client, updated_category)
        self._assert_category_is_saved(updated_category)
        assert_response_matches_expected(response, code=StatusCodes.SUCCESSFULLY_CREATED, status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.UPDATE_CATEGORY_SUCCESS)

    def test_update_category_fails_on_name_not_found(self, create_starting_category, authorized_client):
        wrong_category = stubbed_category.copy()
        wrong_category['weight'] = 99
        wrong_category['name'] = "Wrong name"
        response = send_update_category_request(authorized_client, wrong_category)
        # Check the original category values haven't changed
        self._assert_category_is_saved(stubbed_category)

        assert_response_matches_expected(response, code=StatusCodes.NOT_FOUND, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.UPDATE_CATEGORY_NOT_FOUND)

    def test_update_category_fails_on_internal_error(self, create_starting_category, authorized_client):
        new_category = stubbed_category.copy()
        new_category['weight'] = 99
        error_mock = mock.Mock()
        error_mock.side_effect = Exception

        with patch.object(CategoryGateway, 'update', error_mock):
            response = send_update_category_request(authorized_client, new_category)

            assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                             message=ResponseConstants.UPDATE_CATEGORY_FAIL)

    def test_update_category_fails_on_unauthenticated_user(self, create_starting_category, unauthenticated_client):
        response = send_update_category_request(unauthenticated_client, stubbed_category)
        assert_response_matches_expected(response, code=StatusCodes.UNAUTHENTICATED, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.ERROR_USER_IS_NOT_AUTHENTICATED)

    def test_update_category_fails_on_unauthorized_user(self, create_starting_category, authenticated_client):
        response = send_update_category_request(authenticated_client, stubbed_category)
        assert_response_matches_expected(response, code=StatusCodes.UNAUTHORIZED, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.ERROR_USER_IS_NOT_AUTHORIZED)

    def test_delete_category_successfully(self, create_starting_category, authorized_client):
        response = send_delete_category_request(authorized_client, stubbed_category)
        assert_response_matches_expected(response, code=StatusCodes.SUCCESS, status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.DELETE_CATEGORY_SUCCESS)

    def test_delete_category_fail_on_missing_category_name(self, create_starting_category, authorized_client):
        response = send_delete_category_request(authorized_client, stubbed_category, {})
        assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.DELETE_CATEGORY_WRONG_PARAMETER)

    def test_delete_category_fail_on_category_not_found(self, create_starting_category, authorized_client):
        response = send_delete_category_request(authorized_client, stubbed_category, {'name': 'Wrong name'})
        assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.DELETE_CATEGORY_FAIL_NOT_FOUND)

    def test_delete_category_fail_on_internal_error(self, create_starting_category, authorized_client):
        error_mock = mock.Mock()
        error_mock.side_effect = Exception
        with patch.object(CategoryGateway, 'delete_by_name', error_mock):
            response = send_delete_category_request(authorized_client, stubbed_category)
            assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                             message=ResponseConstants.DELETE_CATEGORY_FAIL)

    def test_delete_category_fails_on_unauthenticated_user(self, create_starting_category, unauthenticated_client):
        response = send_delete_category_request(unauthenticated_client, stubbed_category)
        assert_response_matches_expected(response, code=StatusCodes.UNAUTHENTICATED, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.ERROR_USER_IS_NOT_AUTHENTICATED)

    def test_delete_category_fails_on_unauthorized_user(self, create_starting_category, authenticated_client):
        response = send_delete_category_request(authenticated_client, stubbed_category)
        assert_response_matches_expected(response, code=StatusCodes.UNAUTHORIZED, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.ERROR_USER_IS_NOT_AUTHORIZED)
