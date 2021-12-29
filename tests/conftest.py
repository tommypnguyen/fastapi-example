import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import config, database, oauth2, models
from app.main import app

settings = config.Settings()

SQLALCHEMY_DATABASE_URL = (
    "postgresql://{username}:{password}@{hostname}:{port}/{database_name}_test".format(
        username=settings.database_username,
        password=settings.database_password,
        hostname=settings.database_hostname,
        port=settings.database_port,
        database_name=settings.database_name,
    )
)

# Establishes connection with DB
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Handles session w/ DB
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    database.Base.metadata.drop_all(bind=engine)
    database.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[database.get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "testemail@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    data = res.json()
    data["password"] = user_data["password"]
    assert res.status_code == 201
    return data


@pytest.fixture
def test_user2(client):
    user_data = {"email": "testemail2@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    data = res.json()
    data["password"] = user_data["password"]
    assert res.status_code == 201
    return data


@pytest.fixture
def token(test_user):
    return oauth2.create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": "Bearer {}".format(token)}
    return client


@pytest.fixture
def test_posts(test_user, test_user2, session):
    posts_data = [
        {
            "title": "1st title",
            "content": "1st content",
            "user_id": test_user["id"],
            "id": 1,
        },
        {
            "title": "2nd title",
            "content": "2nd content",
            "user_id": test_user2["id"],
            "id": 2,
        },
    ]
    session.add_all([models.Post(**post) for post in posts_data])
    session.commit()
    return posts_data
