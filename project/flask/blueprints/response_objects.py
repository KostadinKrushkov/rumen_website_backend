class BasicResponse:
    def __init__(self, status, message, status_code, json=None):
        self.status = status
        self.message = message
        self.status_code = status_code
        self.json = json
