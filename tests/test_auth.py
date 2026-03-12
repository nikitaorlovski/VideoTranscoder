import pytest
from app.schemas import UserRegister


@pytest.mark.asyncio
async def test_registration_valid(client):
    user = UserRegister(
        email="orlovski15555@gmail.com",
        password="1567234",
        username="killchik",
    )
    response = await client.post("/api/v1/auth/register", json=user.model_dump())
    data = response.json()
    print(data)
    assert response.status_code == 200
    assert data["token_type"] == "bearer"


@pytest.mark.parametrize(
    "username,email,password",
    [
        pytest.param("killchik", "orlovski15555", "123456", id="invalid email"),
        pytest.param(
            "killchiks", "orlovski155556@gmail.com", "1234", id="invalid password"
        ),
    ],
)
@pytest.mark.asyncio
async def test_invalid_registration(client, username, email, password, user_factory):
    await user_factory(email="orlovski@gmail.com")
    invalid_user = {
        "username": username,
        "email": email,
        "password": password,
    }
    response = await client.post("/api/v1/auth/register", json=invalid_user)
    assert response.status_code == 422, response.text


@pytest.mark.asyncio
async def test_registration_duplicate_email(client, user_factory):
    await user_factory(email="orlovski@gmail.com")
    invalid_user = {
        "username": "killchik",
        "email": "orlovski@gmail.com",
        "password": "1234567",
    }
    response = await client.post("/api/v1/auth/register", json=invalid_user)
    assert response.status_code == 409, response.text


@pytest.mark.asyncio
async def test_auth_valid(client, user_factory):
    await user_factory(email="orlovski@gmail.com", password="killchik")
    response = await client.post(
        "/api/v1/auth/login",
        data={"email": "orlovski@gmail.com", "password": "killchik"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["token_type"] == "bearer"


@pytest.mark.parametrize(
    "email,password",
    [
        pytest.param("orlovskis@gmail.com", "killchik", id="invalid email"),
        pytest.param("orlovski@gmail.com", "killchiks", id="invalid password"),
    ],
)
@pytest.mark.asyncio
async def test_auth_invalid(client, email, password, user_factory):
    await user_factory(email="orlovski@gmail.com", password="killchik")
    response = await client.post(
        "/api/v1/auth/login",
        data={"email": email, "password": password},
    )
    assert response.status_code == 401, response.text
