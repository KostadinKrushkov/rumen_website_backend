from project.common.constants import ResponseConstants


class BasicResponse:
    def __init__(self, status, message, status_code, json=None):
        self.status = status
        self.message = message
        self.status_code = status_code
        self.json = json
        self.is_error = True if self.status == ResponseConstants.FAILURE else False


class AuthenticationResponse(BasicResponse):   # TODO consider removing this in favor of BasicResponse since token is passed in cookie now
    def __init__(self, status, message, status_code, json=None, token=None):
        self.token = token
        super().__init__(status, message, status_code, json)
