import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from project.settings import DB_USER, DB_PASSWORD, DB_SERVER, DB_NAME, DB_DRIVER, TEST_DB_NAME

engine_url = 'mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver={DB_DRIVER}&autocommit=true'
Base = declarative_base()


def initialize_engine():
    db_name = TEST_DB_NAME if getattr(sys, '_called_from_test', False) else DB_NAME

    return create_engine(engine_url.format(
        DB_USER=DB_USER,
        DB_PASSWORD=DB_PASSWORD,
        DB_SERVER=DB_SERVER,
        DB_NAME=db_name,
        DB_DRIVER=DB_DRIVER))


def init_session():
    engine = initialize_engine()
    session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    return session
