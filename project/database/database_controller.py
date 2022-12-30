from sqlalchemy.exc import ResourceClosedError
from project.database.connection import initialize_engine
from project.database.database_utils import sanitize_sql


class DatabaseController:
    """This controller is used to execute all sql queries"""

    @staticmethod
    @sanitize_sql
    def execute_get_response(sql):
        with initialize_engine().connect() as con:
            response = con.execute(sql)
            try:
                data = response.fetchall()
            except ResourceClosedError:  # object doesn't return any data
                return
            return data

    @staticmethod
    @sanitize_sql
    def execute_get_row_count(sql):
        try:
            cursor = initialize_engine().execute(sql)
        except ResourceClosedError:  # object doesn't return any data
            return
        return cursor.rowcount

    @staticmethod
    @sanitize_sql
    def execute(sql):
        engine = initialize_engine()
        with engine.connect() as connection:
            try:
                connection.execute(sql)
            except Exception as e:
                print(e)
            return
