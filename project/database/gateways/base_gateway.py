from project.database.database_controller import DatabaseController


class BaseGateway:
    def __init__(self):
        self.db_controller = DatabaseController

    def save(self, obj):
        raise NotImplemented

    def update(self, obj):
        raise NotImplemented

    def get_all(self):
        raise NotImplemented

    def delete(self, obj):
        raise NotImplemented
