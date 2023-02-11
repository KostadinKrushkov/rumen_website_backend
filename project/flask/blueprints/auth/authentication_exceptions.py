class UserNotFoundException(Exception):
    pass


class PasswordDoesNotMatchException(Exception):
    pass


class IncorrectFormData(Exception):
    pass


class MissingAuthToken(Exception):
    pass


class InvalidAuthToken(Exception):
    pass


class InvalidRecaptchaException(Exception):
    pass