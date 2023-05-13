from project.database.database_controller import DatabaseController


class BaseGateway:
    def __init__(self):
        self.db_controller = DatabaseController

    def clear_cache(self):
        raise NotImplemented

    def save(self, obj):
        self.clear_cache()

    def update(self, obj):
        self.clear_cache()

    def get_all(self):
        raise NotImplemented

    def delete(self, obj):
        self.clear_cache()

