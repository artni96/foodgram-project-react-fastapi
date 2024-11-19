import pytest
from fastapi import status


@pytest.mark.parametrize(
    'username, email, password, first_name, last_name, status_code',
    [
        ('user1', 'user1@ya.ru', 'string', 'Вася', 'Пупкин', status.HTTP_201_CREATED),
        ('user1', 'user1@ya.ru', 'string', '', '', status.HTTP_400_BAD_REQUEST),
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
            'password': password
        }
    )
    if new_user.status_code == status.HTTP_201_CREATED:
        assert new_user.status_code == status_code
        assert new_user.json()['username'] == username
        assert new_user.json()['email'] == email
        assert not new_user.json()['first_name']
        assert not new_user.json()['last_name']
        assert 'id' in new_user.json()


    if new_user.status_code == status.HTTP_400_BAD_REQUEST:
        assert new_user.json()['detail'] == 'Пользователь с указанными данными уже существует.'
