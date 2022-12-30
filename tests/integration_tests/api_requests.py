from tests.integration_tests.testing_utils import _format_response_to_dict


# Authentication
def send_login_user_request(client, user):
    return _format_response_to_dict(client.post('/auth/login', json=user))


def send_logout_user_request(client):
    try:
        return _format_response_to_dict(client.post('/auth/logout'))
    except Exception as e:
        return -1


def send_register_user_request(client, user):
    return _format_response_to_dict(client.post('/auth/register', json=user))


# Blogs
def send_post_blog_request(client, blog):
    return _format_response_to_dict(client.post('/blog', json=blog))


def send_get_blog_request(client):
    return _format_response_to_dict(client.get('/blog'))


def send_get_blog_by_title_request(client, blog, params=None):
    params = params if params is not None else {'title': blog['title']}
    return _format_response_to_dict(client.get('/blog', query_string=params))


def send_update_blog_request(client, blog):
    return _format_response_to_dict(client.put('/blog', json=blog))


def send_delete_blog_request(client, blog, params=None):
    params = params if params is not None else {'title': blog['title']}
    return _format_response_to_dict(client.delete('/blog', query_string=params))


# Categories
def send_post_category_request(client, category):
    return _format_response_to_dict(client.post('/category', json=category))


def send_get_category_request(client):
    return _format_response_to_dict(client.get('/category'))


def send_get_category_by_name_request(client, category, params=None):
    params = params if params is not None else {'name': category['name']}
    return _format_response_to_dict(client.get('/category', query_string=params))


def send_update_category_request(client, category):
    return _format_response_to_dict(client.put('/category', json=category))


def send_delete_category_request(client, category, params=None):
    params = params if params is not None else {'name': category['name']}
    return _format_response_to_dict(client.delete('/category', query_string=params))


# Pictures
def create_category_and_send_post_picture_request(client, picture, test_category):
    send_post_category_request(client, test_category)
    return send_post_picture_request(client, picture)


def send_post_picture_request(client, picture):
    return _format_response_to_dict(client.post('/picture', json=picture))


def send_get_picture_request(client):
    return _format_response_to_dict(client.get('/picture'))


def send_get_picture_by_title_request(client, picture, params=None):
    params = params if params is not None else {'title': picture['title']}
    return _format_response_to_dict(client.get('/picture', query_string=params))


def send_update_picture_request(client, picture):
    return _format_response_to_dict(client.put('/picture', json=picture))


def send_delete_picture_request(client, picture, params=None):
    params = params if params is not None else {'title': picture['title']}
    return _format_response_to_dict(client.delete('/picture', query_string=params))
