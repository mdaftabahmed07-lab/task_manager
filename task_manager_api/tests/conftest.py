import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.session import Base, get_db
from app.main import app

# In-memory SQLite — no Postgres needed
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    # 1. Create tables in the test DB
    Base.metadata.create_all(bind=test_engine)

    # 2. Skip the Postgres create_all in lifespan; use our test DB session
    app.state.skip_create_all = True
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # 3. Cleanup
    app.dependency_overrides.clear()
    app.state.skip_create_all = False
    Base.metadata.drop_all(bind=test_engine)


# ── helpers ────────────────────────────────────────────────────────────────

def register_and_login(client, email="test@example.com", password="password123"):
    client.post("/auth/register", json={
        "full_name": "Test User",
        "email": email,
        "password": password,
    })
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
