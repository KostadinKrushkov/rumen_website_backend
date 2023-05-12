class BasicResponse:
    def __init__(self, status, message, status_code, json=None):
        self.status = status
        self.message = message
        self.status_code = status_code
        self.json = json

    def __repr__(self):
        return f'Response: {self.status_code} | {self.status} | {self.message} | {self.json}'

