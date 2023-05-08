from project.database.database_controller import DatabaseController
from project.database.database_manager import DatabaseManager
from project.database.initial_tables import tables_to_create_in_order, tables_to_delete_in_order
from project.settings import Config


class TestDatabaseManager:
    GET_TABLE_NAMES_SQL = "SELECT TABLE_NAME  FROM [%s].INFORMATION_SCHEMA.TABLES" % Config.TEST_DB_NAME

    def test_create_all_tables(self, client):
        DatabaseManager.drop_all_tables()
        num_tables = len(DatabaseController.execute_get_response(self.GET_TABLE_NAMES_SQL))

        DatabaseManager.create_all_tables()
        result_num_tables = len(DatabaseController.execute_get_response(self.GET_TABLE_NAMES_SQL))
        assert num_tables + len(tables_to_create_in_order) == result_num_tables

    def test_drop_all_tables(self, client):
        DatabaseManager.create_all_tables()
        num_tables = len(DatabaseController.execute_get_response(self.GET_TABLE_NAMES_SQL))
        DatabaseManager.drop_all_tables()

        resulting_num_tables = len(DatabaseController.execute_get_response(self.GET_TABLE_NAMES_SQL))
        assert resulting_num_tables == num_tables - len(tables_to_delete_in_order)






