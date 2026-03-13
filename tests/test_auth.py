from fastapi import HTTPException
from app.dependencies import get_current_auth_user
from jwt.exceptions import InvalidTokenError
import pytest
from fastapi.security import HTTPAuthorizationCredentials
from app.dependencies import get_current_token_payload
from app.dependencies import get_user_service, validate_current_user
from app.domain.exceptions import UserAlreadyExists
from app.schemas import UserRegister
from app.services.user_service import UserService
from main import app


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


@pytest.mark.asyncio
async def test_registration_user_service_email_duplicated(mocker):
    user = UserRegister(
        email="orlovski@gmail.com",
        password="1567234",
        username="killchik",
    )
    repo = mocker.Mock()
    repo.get_user_by_email = mocker.AsyncMock(return_value=mocker.Mock())

    service = UserService(repo)

    with pytest.raises(UserAlreadyExists):
        await service.register(user)

    repo.get_user_by_email.assert_awaited_once_with("orlovski@gmail.com")
    repo.register.assert_not_called()


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
async def test_registration_duplicate_email_hits_router_except(client, mocker):
    service_mock = mocker.Mock()
    service_mock.register = mocker.AsyncMock(side_effect=UserAlreadyExists())

    async def override_get_user_service():
        return service_mock

    app.dependency_overrides[get_user_service] = override_get_user_service

    try:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "killchik",
                "email": "orlovski@gmail.com",
                "password": "1234567",
            },
        )

        assert response.status_code == 409
        assert response.json() == {"detail": "User already exists"}
        service_mock.register.assert_called_once()
    finally:
        app.dependency_overrides.clear()


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


@pytest.mark.asyncio
async def test_validate_current_user_user_not_found(mocker):
    service = mocker.Mock()
    service.get_user_by_email = mocker.AsyncMock(return_value=None)

    with pytest.raises(HTTPException, match="Invalid email or password") as exc:
        await validate_current_user(
            email="test@example.com",
            password="secret",
            service=service,
        )

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_validate_current_user_wrong_password(mocker):
    user = mocker.Mock()
    user.password = "hashed-password"

    service = mocker.Mock()
    service.get_user_by_email = mocker.AsyncMock(return_value=user)

    mocker.patch("app.dependencies.verify_password", return_value=False)

    with pytest.raises(HTTPException, match="Invalid email or password") as exc:
        await validate_current_user(
            email="test@example.com",
            password="wrong-password",
            service=service,
        )

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_validate_current_user_success(mocker):
    user = mocker.Mock()
    user.password = "hashed-password"

    service = mocker.Mock()
    service.get_user_by_email = mocker.AsyncMock(return_value=user)

    mocker.patch("app.dependencies.verify_password", return_value=True)

    result = await validate_current_user(
        email="test@example.com",
        password="correct-password",
        service=service,
    )

    assert result is user


@pytest.mark.asyncio
async def test_get_current_token_payload_success(mocker):
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="good-token",
    )

    mocker.patch(
        "app.dependencies.decode_jwt",
        return_value={"sub": "1", "email": "test@example.com"},
    )

    result = await get_current_token_payload(credentials=credentials)

    assert result == {"sub": "1", "email": "test@example.com"}


@pytest.mark.asyncio
async def test_get_current_token_payload_invalid_token(mocker):
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="bad-token",
    )

    mocker.patch(
        "app.dependencies.decode_jwt",
        side_effect=InvalidTokenError("bad signature"),
    )

    with pytest.raises(HTTPException, match="Invalid token") as exc:
        await get_current_token_payload(credentials=credentials)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_auth_user_not_found(mocker):
    service = mocker.Mock()
    service.get_user_by_email = mocker.AsyncMock(return_value=None)

    with pytest.raises(HTTPException, match="Token invalid") as exc:
        await get_current_auth_user(
            payload={"email": "missing@example.com"},
            service=service,
        )

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_auth_user_success(mocker):
    user = mocker.Mock()

    service = mocker.Mock()
    service.get_user_by_email = mocker.AsyncMock(return_value=user)

    result = await get_current_auth_user(
        payload={"email": "test@example.com"},
        service=service,
    )

    assert result is user
