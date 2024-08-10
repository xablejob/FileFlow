import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from db_utils.database import Base, get_db
from main import app
from settings_app import TEST_DATABASE_URL


@pytest.fixture(scope="session")
def engine():
    """Создает движок базы данных для тестирования."""
    return create_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="session")
def setup_database(engine):
    """Создает и настраивает тестовую базу данных для всех тестов."""
    if not database_exists(engine.url):
        create_database(engine.url)

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)
    drop_database(engine.url)


@pytest.fixture(scope="function")
def db_session(engine, setup_database):
    """Создает новую сессию базы данных для каждого теста."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    try:
        yield session
    except Exception:
        transaction.rollback()
        raise
    finally:
        session.close()
        connection.close()
        if transaction.is_active:
            transaction.rollback()


@pytest.fixture(scope="function")
def client(db_session):
    """Создает тестовый клиент FastAPI с переопределенной зависимостью базы данных."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    del app.dependency_overrides[get_db]  # Удаляем переопределение после теста
