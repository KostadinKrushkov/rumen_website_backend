from project.database.database_controller import DatabaseController
from project.database.initial_tables import tables_to_create_in_order, tables_to_delete_in_order


class DatabaseManager:
    """This controller is used to initialize or reset the database to the initial state"""
    def __init__(self, flask_app):
        self.app = flask_app
        self.context = self.app.config

    def reset_database(self):
        with self.app.app_context():
            self.drop_all_tables()
            self.create_all_tables()

    def reset_data_without_users(self):
        with self.app.app_context():
            self.drop_tables(tables_to_delete_in_order[:-1])
            self.create_tables(tables_to_create_in_order[1:])

    @classmethod
    def drop_all_tables(cls):
        cls.drop_tables(tables_to_delete_in_order)

    @staticmethod
    def drop_tables(tables_list):
        sql = '\n'.join(tables_list)
        DatabaseController.execute(sql)

    @classmethod
    def create_all_tables(cls):
        cls.create_tables(tables_to_create_in_order)

    @staticmethod
    def create_tables(tables):
        sql = '\n'.join(tables)
        DatabaseController.execute(sql)
