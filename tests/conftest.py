import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.models.base import Base
from src.db.session import get_db
from src.main import app
from src.models.users import User
from src.models.books import Book


@pytest.fixture(scope="session")
def engine():
    """
    Crée un moteur SQLAlchemy pour les tests.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db_session(engine):
    """
    Crée une nouvelle session de base de données pour un test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Crée un client de test pour FastAPI.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides = {}


@pytest.fixture
def user(db_session):
    user = User(email="testuser@example.com", full_name="Test User", hashed_password="hashed", is_active=True)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def book(db_session):
    book = Book(title="Test Book", author="Author", isbn="1234567890", publication_year=2020, quantity=3)
    db_session.add(book)
    db_session.commit()
    return book