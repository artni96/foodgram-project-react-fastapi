import pytest
from fastapi import status
from sqlalchemy import select

from backend.src.models.users import UserModel
from backend.tests.conftest import MAX_EMAIL_LENGTH, USER_PARAMS_MAX_LENGTH


@pytest.mark.order(4)
@pytest.mark.parametrize(
    "username, email, password, first_name, last_name, status_code, detail",
    [
        (
            "user2",
            "user2@ya.ru",
            "string",
            "Вася",
            "Пупкин",
            status.HTTP_201_CREATED,
            "",
        ),
        (
            "user3",
            f'{"".join(["t"] * (MAX_EMAIL_LENGTH + 1))}@ya.ru',
            "string",
            "",
            "",
            status.HTTP_400_BAD_REQUEST,
            f"Максимальная длина поля email - {MAX_EMAIL_LENGTH} символа",
        ),
        (
            f'{"".join(["t"] * (USER_PARAMS_MAX_LENGTH + 1))}',
            "user4@ya.ru",
            "string",
            "",
            "",
            status.HTTP_400_BAD_REQUEST,
            f"Максимальная длина поля username - {USER_PARAMS_MAX_LENGTH} символов",
        ),
        (
            "user5",
            "user5@ya.ru",
            f'{"".join(["t"] * (USER_PARAMS_MAX_LENGTH + 1))}',
            "",
            "",
            status.HTTP_400_BAD_REQUEST,
            f"Максимальная длина поля email - {USER_PARAMS_MAX_LENGTH} символов",
        ),
    ],
)
async def test_user_regestration(
    ac, db, username, email, password, first_name, last_name, status_code, detail
):
    new_user = await ac.post(
        "/api/users",
        json={
            "username": username,
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    assert new_user.status_code == status_code, detail


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "username, email, password, first_name, last_name, status_code",
    [
        ("user1", "user1@ya.ru", "string", "Вася", "Пупкин", status.HTTP_201_CREATED),
    ],
)
async def test_auth_flow(
    ac, username, email, password, first_name, last_name, status_code, db
):
    new_user = await ac.post(
        "/api/users",
        json={
            "username": username,
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    assert (
        new_user.status_code == status_code
    ), f"статус ответа отличается от {status_code}"
    assert new_user.json()["username"] == username, "В ответе должно быть поле username"
    assert new_user.json()["email"] == email, "В ответе должно быть поле email"
    assert (
        new_user.json()["first_name"] == first_name
    ), "В ответе должно быть поле first_name"
    assert (
        new_user.json()["last_name"] == last_name
    ), "В ответе должно быть поле last_name"
    assert "id" in new_user.json(), "В ответе должно быть поле id"

    jwt_token = await ac.post(
        "/api/auth/token/login", json={"email": email, "password": password}
    )
    assert (
        jwt_token.status_code == status.HTTP_201_CREATED
    ), "статус ответа отличается от 201"
    assert isinstance(jwt_token.json()["auth_token"], str), "неверный формат jwt-токена"

    current_user_info = await ac.get(
        "/api/users/me",
        headers={"Authorization": f'Token {jwt_token.json()["auth_token"]}'},
    )
    assert (
        current_user_info.status_code == status.HTTP_200_OK
    ), "статус ответа отличается от 200"
    user_info = current_user_info.json()
    assert user_info["email"] == email, "В ответе должно быть поле email"
    assert user_info["username"] == username, "В ответе должно быть поле username"
    assert user_info["first_name"] == first_name, "В ответе должно быть поле first_name"
    assert user_info["last_name"] == last_name, "В ответе должно быть поле last_name"
    assert "id" in user_info, "В ответе должно быть поле id"
    assert not user_info["is_subscribed"], (
        "При запросе /api/users/me значение поля is_subscribed должно быть " "False"
    )
    #
    current_user_info = await ac.get(
        f'/api/users/{user_info["id"]}',
        headers={"Authorization": f'Token {jwt_token.json()["auth_token"]}'},
    )
    assert current_user_info.status_code == status.HTTP_200_OK

    user_list = await ac.get(
        "/api/users",
        headers={"Authorization": f'Token {jwt_token.json()["auth_token"]}'},
    )
    assert (
        user_list.status_code == status.HTTP_200_OK
    ), "статус ответа отличается от 200"
    assert (
        len(user_list.json()["results"]) == 3
    ), "неверное количество пользователей в поле results"

    new_password = "string123"
    password_chaning = await ac.post(
        "/api/users/set_password",
        json={"current_password": password, "new_password": new_password},
        headers={"Authorization": f'Token {jwt_token.json()["auth_token"]}'},
    )
    assert (
        password_chaning.status_code == status.HTTP_204_NO_CONTENT
    ), "статус ответа отличается от 204"

    logout = await ac.post(
        "/api/auth/token/logout",
        headers={"Authorization": f'Token {jwt_token.json()["auth_token"]}'},
    )
    assert (
        logout.status_code == status.HTTP_204_NO_CONTENT
    ), "статус ответа отличается от 204"
    await db.users.delete(id=user_info["id"])
    user_list_stmt = select(UserModel)
    user_list = await db.session.execute(user_list_stmt)
    user_list = user_list.scalars().all()
    await db.commit()
    assert len(user_list) == 2


@pytest.mark.order(2)
async def test_not_auth_flow(ac):
    user_list = await ac.get("/api/users")
    assert (
        user_list.status_code == status.HTTP_200_OK
    ), "статус ответа отличается от 200"

    user_list = await ac.get(
        "/api/users",
    )
    assert (
        user_list.status_code == status.HTTP_200_OK
    ), "статус ответа отличается от 200"
    current_user_info = await ac.get(
        f'/api/users/{user_list.json()["results"][-1]["id"]}',
    )
    assert (
        current_user_info.status_code == status.HTTP_200_OK
    ), "статус ответа отличается от 200"
    user_id_to_check = user_list.json()["results"][-1]["id"]
    current_user_info = await ac.get(
        f"/api/users/{user_id_to_check}",
    )
    assert (
        current_user_info.status_code == status.HTTP_200_OK
    ), "статус ответа отличается от 200"
    non_existent_user_id = user_id_to_check + 1
    non_existent_user_info = await ac.get(
        f"/api/users/{non_existent_user_id}",
    )
    assert (
        non_existent_user_info.status_code == status.HTTP_404_NOT_FOUND
    ), "статус ответа отличается от 404"
