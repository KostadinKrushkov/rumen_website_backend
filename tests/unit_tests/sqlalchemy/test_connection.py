import sys

from sqlalchemy.engine import Engine
from project.database.connection import initialize_engine
from project.settings import TEST_DB_NAME, DB_NAME


class TestConnection:
    def test_get_engine_for_prod(self):
        sys._called_from_test = False
        self._assert_engine_created_for_database(DB_NAME)

    def test_get_engine_for_testing(self):
        sys._called_from_test = True
        self._assert_engine_created_for_database(TEST_DB_NAME)

    @staticmethod
    def _assert_engine_created_for_database(database):
        engine = initialize_engine()
        assert isinstance(engine, Engine)
        assert engine.url.database == database



