import psycopg2
import pytest
from werkzeug.datastructures import FileStorage
from application import create_app

test_ids = ['40508fa7-2b6f-4629-8187-77fe6c541333', '106fae0e-d2f0-4a0a-90f2-9d6034adece4',
            '0cf6108a-6f56-4c9d-8bda-90b72cc058c3', '01531373-f08f-410e-8275-96d5d8df3621',
            '13bc99cc-5c41-409d-b7c2-ba5fb72f0fed', '0eb957c1-1aea-457a-8935-6fb26230da8f']


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
