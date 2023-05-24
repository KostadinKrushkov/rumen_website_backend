import logging
import sys
import datetime

from flask import make_response, jsonify


def lazy_property(func):
    """Decorator for lazy properties."""

    property_name = '_' + func.__name__

    @property
    def lazy_property_wrapper(self):
        if not hasattr(self, property_name):
            setattr(self, property_name, func(self))
        return getattr(self, property_name)
    return lazy_property_wrapper


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


def log_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now()

        result = func(*args, **kwargs)

        time_delta = start_time - datetime.datetime.now()
        logging.debug(f'Execution time for {str(func)} took {abs(time_delta.total_seconds())} seconds')
        return result

    wrapper.__name__ = func.__name__
    return wrapper


def generated_jsonified_response(response):
    return make_response(jsonify(response.__dict__), response.status_code)
