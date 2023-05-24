import logging
from sqlalchemy.exc import ResourceClosedError

from project.database.connection import initialize_engine
from project.database.database_utils import sanitize_sql


class DatabaseController:
    """This controller is used to execute all sql queries"""

    @staticmethod
    @sanitize_sql
    def execute_get_response(sql):
        logging.debug(f'Executing {sql}.')

        with initialize_engine().connect() as con:
            logging.debug(f'Connected to the database.')
            response = con.execute(sql)
            try:
                logging.debug(f'Fetching the response data.')
                data = response.fetchall()
            except ResourceClosedError:  # object doesn't return any data
                return

            logging.debug(f'Database response data: {data}')
            return data

    @staticmethod
    @sanitize_sql
    def execute_get_row_count(sql, *args, **kwargs):
        try:
            cursor = initialize_engine().execute(sql, *args, **kwargs)
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
