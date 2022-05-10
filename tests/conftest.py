import pytest

from app.db import db


@pytest.fixture(autouse=True)
def clear_db_after_each_test():
    yield
    db.clear()
