import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app import crud, schemas

# ═══════════════════════════════════════════════════════════════
# TEST-DATABASE (In-Memory, frisch für jeden Test)
# ═══════════════════════════════════════════════════════════════

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Überschreibt die echte DB-Verbindung mit der Test-DB."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# FastAPI-Dependency überschreiben
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """Erstellt frische Tabellen vor jedem Test, löscht sie danach."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Gibt einen Test-Client zurück."""
    return TestClient(app)


@pytest.fixture(scope="function")
def test_user(db):
    """Erstellt einen Standard-Test-User."""
    user_in = schemas.UserCreate(
        username="testuser",
        email="test@test.de",
        password="geheim123"
    )
    return crud.create_user(db=db, user=user_in)


@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """Loggt den Test-User ein und gibt den Auth-Header zurück."""
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "geheim123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}