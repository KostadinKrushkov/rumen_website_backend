import json


def _format_response_to_dict(response):
    formatted_response = json.loads(response.data.decode('utf-8'))
    formatted_response['status_code'] = response.status_code
    return formatted_response


def assert_response_matches_expected(response, code, status, message):
    assert response['status_code'] == code
    assert response['status'] == status
    assert response['message'] == message
