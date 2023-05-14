import pytest
from unittest import mock
from unittest.mock import patch

from project.common.constants import ResponseConstants, StatusCodes
from project.database.dtos.picture_dto import PictureDTO
from project.database.gateways.category_gateway import CategoryGateway
from project.database.gateways.favourite_pictures_gateway import FavouritePicturesGateway
from project.database.gateways.picture_gateway import PictureGateway
from project.settings import Config
from tests.integration_tests.blueprints.test_categories import stub_category_name, stubbed_category
from tests.integration_tests.api_requests import create_category_and_send_post_picture_request, \
    send_post_picture_request, send_get_picture_by_title_request, \
    send_update_picture_request, send_delete_picture_request, send_get_home_pictures, send_update_home_pictures
from tests.integration_tests.testing_utils import assert_response_matches_expected

stub_picture = {
    'title': 'To be or not to be',
    'description': "Whether ’tis nobler in the mind to suffer The slings and arrows of outrageous fortune, "
                   "Or to take arms against a sea of troubles, And, by opposing, end them?",
    'category': stub_category_name,
    'image': "Some image"
}


@pytest.fixture
def create_starting_picture(authorized_client):
    response = create_category_and_send_post_picture_request(authorized_client, stub_picture, stubbed_category)
    assert response['status_code'] == StatusCodes.SUCCESSFULLY_CREATED


class TestPicturesAPI:
    picture_gateway = PictureGateway()
    category_gateway = CategoryGateway()

    def _assert_picture_is_saved(self, expected_picture, pictures_list=None):
        pictures_list = pictures_list if pictures_list is not None else list(self.picture_gateway.get_all())
        picture = pictures_list[0] if isinstance(pictures_list[0], PictureDTO) else PictureDTO.from_dict(
            pictures_list[0])

        self._assert_picture_matches_expected(expected_picture, picture)

    def _assert_picture_matches_expected(self, expected_picture, picture):
        category = self.category_gateway.get_by_name(expected_picture.get('category'))

        assert picture.title == expected_picture.get('title')
        assert picture.description == expected_picture.get('description')
        assert picture.category_id == category.id if category is not None else None
        assert picture.image == expected_picture.get('image')

    def test_get_picture_by_title_successfully(self, create_starting_picture, unauthenticated_client):
        response = send_get_picture_by_title_request(unauthenticated_client, stub_picture)
        self._assert_picture_matches_expected(stub_picture, PictureDTO(**response['json']))

        assert_response_matches_expected(response, code=StatusCodes.SUCCESS, status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.GET_PICTURE_BY_TITLE_SUCCESS)

    def test_get_picture_by_title_fail_on_missing_title(self, unauthenticated_client):
        picture = stub_picture.copy()
        picture['title'] = 'Wrong title'
        response = send_get_picture_by_title_request(unauthenticated_client, picture)
        assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.GET_PICTURE_BY_TITLE_NOT_FOUND)

    def test_get_picture_by_title_fail_on_internal_error(self, unauthenticated_client):
        error_mock = mock.Mock()
        error_mock.side_effect = Exception
        with patch.object(PictureGateway, 'get_by_title', error_mock):
            response = send_get_picture_by_title_request(unauthenticated_client, stub_picture)
            assert_response_matches_expected(response, code=StatusCodes.INTERNAL_SERVER_ERROR,
                                             status=ResponseConstants.FAILURE,
                                             message=ResponseConstants.GET_PICTURE_BY_TITLE_FAIL)

    def test_create_picture_successfully(self, authorized_client):
        client = authorized_client
        response = create_category_and_send_post_picture_request(client, stub_picture, stubbed_category)
        self._assert_picture_is_saved(stub_picture)
        assert_response_matches_expected(response, code=StatusCodes.SUCCESSFULLY_CREATED,
                                         status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.POST_PICTURE_SUCCESS)

    def test_create_picture_fails_on_duplicate_key(self, create_starting_picture, authorized_client):
        response = send_post_picture_request(authorized_client, stub_picture)
        assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.POST_PICTURE_FAIL_DUPLICATE_OR_OTHER)

    def test_create_picture_fails_on_internal_error(self, authorized_client):
        error_mock = mock.Mock()
        error_mock.side_effect = Exception
        with patch.object(PictureGateway, 'save', error_mock):
            response = create_category_and_send_post_picture_request(authorized_client, stub_picture, stubbed_category)
            assert_response_matches_expected(response, code=StatusCodes.INTERNAL_SERVER_ERROR,
                                             status=ResponseConstants.FAILURE,
                                             message=ResponseConstants.POST_PICTURE_FAIL)

    def test_update_picture_successfully(self, create_starting_picture, authorized_client):
        picture = stub_picture.copy()
        picture['description'] = "A changed description"
        response = send_update_picture_request(authorized_client, picture)
        self._assert_picture_is_saved(picture)
        assert_response_matches_expected(response, code=StatusCodes.SUCCESSFULLY_CREATED,
                                         status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.UPDATE_PICTURE_SUCCESS)

    def test_update_picture_fails_on_title_not_found(self, create_starting_picture, authorized_client):
        picture = stub_picture.copy()
        picture['description'] = "A changed description"
        picture['title'] = "Wrong title"
        response = send_update_picture_request(authorized_client, picture)
        # Check the original picture values haven't changed
        self._assert_picture_is_saved(stub_picture)

        assert_response_matches_expected(response, code=StatusCodes.NOT_FOUND, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.UPDATE_PICTURE_NOT_FOUND)

    def test_update_picture_fails_on_internal_error(self, create_starting_picture, authorized_client):
        picture = stub_picture.copy()
        picture['title'] = "Wrong title"
        error_mock = mock.Mock()
        error_mock.side_effect = Exception

        with patch.object(PictureGateway, 'update', error_mock):
            response = send_update_picture_request(authorized_client, picture)

            assert_response_matches_expected(response, code=StatusCodes.INTERNAL_SERVER_ERROR, status=ResponseConstants.FAILURE,
                                             message=ResponseConstants.UPDATE_PICTURE_FAIL)

    def test_delete_picture_successfully(self, create_starting_picture, authorized_client):
        response = send_delete_picture_request(authorized_client, stub_picture)
        assert_response_matches_expected(response, code=StatusCodes.SUCCESS, status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.DELETE_PICTURE_SUCCESS)

    def test_delete_picture_fail_on_missing_picture_title(self, create_starting_picture, authorized_client):
        response = send_delete_picture_request(authorized_client, stub_picture, {})
        assert_response_matches_expected(response, code=StatusCodes.BAD_REQUEST, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.DELETE_PICTURE_WRONG_PARAMETER)

    def test_delete_picture_fail_on_picture_not_found(self, create_starting_picture, authorized_client):
        response = send_delete_picture_request(authorized_client, stub_picture, {'title': 'Wrong title'})
        assert_response_matches_expected(response, code=StatusCodes.NOT_FOUND, status=ResponseConstants.FAILURE,
                                         message=ResponseConstants.DELETE_PICTURE_FAIL_NOT_FOUND)

    def test_delete_picture_fail_on_internal_error(self, create_starting_picture, authorized_client):
        error_mock = mock.Mock()
        error_mock.side_effect = Exception
        with patch.object(PictureGateway, 'delete_by_title', error_mock):
            response = send_delete_picture_request(authorized_client, stub_picture)
            assert_response_matches_expected(response, code=StatusCodes.INTERNAL_SERVER_ERROR,
                                             status=ResponseConstants.FAILURE,
                                             message=ResponseConstants.DELETE_PICTURE_FAIL)

    def test_get_home_pictures_fails_on_internal_error(self, client):
        error_mock = mock.Mock()
        error_mock.side_effect = Exception

        with patch.object(FavouritePicturesGateway, 'get_all', error_mock):
            response = send_get_home_pictures(client)
            assert_response_matches_expected(response, code=StatusCodes.INTERNAL_SERVER_ERROR,
                                             status=ResponseConstants.FAILURE,
                                             message=ResponseConstants.GET_FAVOURITE_PICTURES_FAIL)

    def test_update_home_pictures_and_get_them_successfully(self, authorized_client, client):
        stub_picture2 = stub_picture.copy()
        stub_picture2['title'] = 'Damn skyr has a lot of protein'
        pictures = [stub_picture, stub_picture2]
        picture_titles = [stub_picture['title'], stub_picture2['title']]

        create_category_and_send_post_picture_request(client, stub_picture, stubbed_category)
        send_post_picture_request(authorized_client, stub_picture2)

        response = send_update_home_pictures(authorized_client, pictures)
        assert_response_matches_expected(response, code=StatusCodes.SUCCESSFULLY_CREATED,
                                         status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.UPDATE_FAVOURITE_PICTURES_SUCCESS)

        response = send_get_home_pictures(client)

        assert len(response['json']) == 2
        assert response['json'][0]['title'] in picture_titles
        assert response['json'][1]['title'] in picture_titles

        assert_response_matches_expected(response, code=StatusCodes.SUCCESS, status=ResponseConstants.SUCCESS,
                                         message=ResponseConstants.GET_FAVOURITE_PICTURES_SUCCESS)
