import pytest
from werkzeug.datastructures import FileStorage

from application import create_app


@pytest.fixture()
def app():
    app = create_app("tests/test_configurations.ini")
    context = app.test_request_context()
    context.push()
    yield app
    context.pop()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def cardio_file():
    return FileStorage(stream=open("tests/test_files/cardio.csv", "rb"),
                       filename="cardio.csv")