import sys

from flask import make_response, jsonify


def disable_during_tests(func):

    def wrapper(*args, **kwargs):
        if getattr(sys, '_called_from_test', False):
            return

        return func(*args, **kwargs)
    return wrapper


def jsonify_response(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        return generated_jsonified_response(response)

    wrapper.__name__ = func.__name__
    return wrapper


def generated_jsonified_response(response):
    return make_response(jsonify(response.__dict__), response.status_code)