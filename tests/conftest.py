import os

import pytest

from db_utils.fixture_db import client, db_session, engine, setup_database
from main import app
from settings_app import UPLOAD_DIR
from utils import get_upload_dir

__all__ = [
    "engine",
    "setup_database",
    "db_session",
    "client",
]

UPLOAD_DIR_TEST = os.path.join(os.getcwd(), UPLOAD_DIR + "_test")


@pytest.fixture(scope="function")
def upload_dir(client):
    """Создает и настраивает тестовую базу данных для всех тестов."""

    def override_get_upload_dir():
        yield UPLOAD_DIR_TEST

    app.dependency_overrides[get_upload_dir] = override_get_upload_dir
    yield
    del app.dependency_overrides[get_upload_dir]  # Удаляем переопределение после теста


@pytest.fixture(scope="function", autouse=True)
def setup_upload_dir_test(upload_dir):
    # Фикстура для подготовки директории
    if not os.path.exists(UPLOAD_DIR_TEST):
        os.makedirs(UPLOAD_DIR_TEST)
    yield
    for file in os.listdir(UPLOAD_DIR_TEST):
        file_path = os.path.join(UPLOAD_DIR_TEST, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    if os.path.exists(UPLOAD_DIR_TEST):
        os.rmdir(UPLOAD_DIR_TEST)
