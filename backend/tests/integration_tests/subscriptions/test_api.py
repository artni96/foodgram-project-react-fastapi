from fastapi import status
from sqlalchemy import select

from backend.src.models.users import UserModel


async def test_auth_subsrtibe(auth_ac, ac, db):
    current_user = await auth_ac.get(
        '/api/users/me'
    )
    users_to_subscribe_stmt = select(UserModel.id).filter(
        UserModel.id != current_user.json()['id']
    )
    users_to_subscribe = await db.session.execute(users_to_subscribe_stmt)
    users_to_subscribe = users_to_subscribe.scalars().all()

    user_to_subscribe = users_to_subscribe[-1]
    new_sub = await auth_ac.post(
        f'/api/users/{user_to_subscribe}/subscribe'
    )
    followed_user = await db.users.get_one_or_none(user_id=user_to_subscribe)
    assert new_sub.status_code == status.HTTP_201_CREATED
    assert new_sub.json()['username'] == followed_user.username
    assert new_sub.json()['email'] == followed_user.email
    assert new_sub.json()['id'] == followed_user.id
    assert new_sub.json()['first_name'] == followed_user.first_name
    assert new_sub.json()['last_name'] == followed_user.last_name
    # assert 'recipes' in new_sub.json() нужно добавить в респонс
    # assert 'recipes_count' in new_sub.json() нужно добавить в респонс



    new_sub_by_not_auth = await ac.post(
        f'/api/users/{users_to_subscribe[-1]}/subscribe'
    )
    assert new_sub_by_not_auth.status_code == status.HTTP_401_UNAUTHORIZED

    follow_yourself = await auth_ac.post(
        f'/api/users/{current_user.json()["id"]}/subscribe'
    )
    assert follow_yourself.status_code == status.HTTP_400_BAD_REQUEST

    follow_non_existent_user = await auth_ac.post(
        f'/api/users/{users_to_subscribe[-1] + 1}/subscribe'
    )
    assert follow_non_existent_user.status_code == status.HTTP_404_NOT_FOUND

    unfollow = await auth_ac.delete(
        f'/api/users/{users_to_subscribe[-1]}/subscribe'
    )
    assert unfollow.status_code == status.HTTP_204_NO_CONTENT
