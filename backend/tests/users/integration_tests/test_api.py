import pytest
from fastapi import status

from backend.src.services.users import current_user

MAX_EMAIL_LENGTH = 254
USER_PARAMS_MAX_LENGTH = 150

@pytest.mark.parametrize(
    'username, email, password, first_name, last_name, status_code, detail',
    [
        (
            'user2',
            'user2@ya.ru',
            'string',
            'Вася',
            'Пупкин',
            status.HTTP_201_CREATED,
            ''
        ),
        (
            f'user3',
            f'{"".join(["t"]*(MAX_EMAIL_LENGTH+1))}@ya.ru',
            f'string',
            '',
            '',
            status.HTTP_400_BAD_REQUEST,
            f'Максимальная длина поля email - {MAX_EMAIL_LENGTH} символа'
        ),
        (
            f'{"".join(["t"] * (USER_PARAMS_MAX_LENGTH+1))}',
            f'user4@ya.ru',
            f'string',
            '',
            '',
            status.HTTP_400_BAD_REQUEST,
            f'Максимальная длина поля username - {USER_PARAMS_MAX_LENGTH} символов'
        ),
        (
            f'user5',
            f'user5@ya.ru',
            f'{"".join(["t"] * (USER_PARAMS_MAX_LENGTH+1))}',
            '',
            '',
            status.HTTP_400_BAD_REQUEST,
            f'Максимальная длина поля email - {USER_PARAMS_MAX_LENGTH} символов'
        ),
    ]
)
async def test_user_regestration(
    ac,
    db,
    username,
    email,
    password,
    first_name,
    last_name,
    status_code,
    detail
):
    print(email)
    new_user = await ac.post(
        '/api/users',
        json={
            'username': username,
            'email': email,
            'password': password
        }
    )
    assert new_user.status_code == status_code, detail


@pytest.mark.parametrize(
    'username, email, password, first_name, last_name, status_code',
    [
        ('user1', 'user1@ya.ru', 'string', 'Вася', 'Пупкин', status.HTTP_201_CREATED),
    ]
)
async def test_auth_flow(
        ac,
        username,
        email,
        password,
        first_name,
        last_name,
        status_code
):
    new_user = await ac.post(
        '/api/users',
        json={
            'username': username,
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name
        }
    )
    assert new_user.status_code == status_code
    assert new_user.json()['username'] == username
    assert new_user.json()['email'] == email
    assert new_user.json()['first_name'] == first_name
    assert new_user.json()['last_name'] == last_name
    assert 'id' in new_user.json()

    jwt_token = await ac.post(
        '/api/users/token/login',
        data = {
            "username": email,
            "password": password
        }
    )
    assert jwt_token.status_code == status.HTTP_200_OK
    assert isinstance(jwt_token.json()['access_token'], str)

    current_user_info = await ac.get(
        '/api/users/me',
        headers={'Authorization': f'Bearer {jwt_token.json()["access_token"]}'}
    )
    assert current_user_info.status_code == status.HTTP_200_OK
    user_info = current_user_info.json()
    assert user_info['email'] == email
    assert user_info['username'] == username
    assert user_info['first_name'] == first_name
    assert user_info['last_name'] == last_name
    assert 'id' in user_info
    assert user_info['is_subscribed'] == False

    new_password = 'string123'
    password_chaning = await ac.post(
        '/api/users/set_password',
        json={
            'current_password': password,
            'new_password': new_password
        },
        headers={'Authorization': f'Bearer {jwt_token.json()["access_token"]}'}
    )
    assert password_chaning.status_code == status.HTTP_204_NO_CONTENT

    logout = await ac.post(
        '/api/users/token/logout',
        headers={'Authorization': f'Bearer {jwt_token.json()["access_token"]}'}
    )
    assert logout.status_code == status.HTTP_204_NO_CONTENT
