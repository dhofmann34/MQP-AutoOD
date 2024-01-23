import pytest
from application import create_app


@pytest.fixture()
def app():
    app = create_app("test_configurations.ini")
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
