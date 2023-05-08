import urllib.parse
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from project.settings import Config

Base = declarative_base()


def initialize_engine():
    db_name = Config.TEST_DB_NAME if getattr(sys, '_called_from_test', False) else Config.DB_NAME
    params = urllib.parse.quote_plus(
        f"DRIVER={Config.DB_DRIVER};SERVER={Config.DB_SERVER};DATABASE={db_name};UID={Config.DB_USER};PWD={Config.DB_PASSWORD}")
    engine_url = "mssql+pyodbc:///?odbc_connect={PARAMS}".format(PARAMS=params)

    return create_engine(engine_url)


# Alternative way to query the database with cursor.
# cursor = None
# def get_cursor_from_connection_to_db():
#     global cursor
#     engine = initialize_engine()
#     connection = engine.raw_connection()
#     cursor = connection.cursor()
#     return cursor
#
# # Example
# cursor = get_cursor_from_connection_to_db()
# cursor.execute(str(sql))
# columns = [column[0] for column in cursor.description]
#
# results = []
# for row in cursor.fetchall():
#     results.append(dict(zip(columns, row)))
#
# return results


def init_session():
    engine = initialize_engine()
    session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    return session
