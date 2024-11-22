import pytest
from fastapi import HTTPException


@pytest.mark.order(4)
async def test_user_repository(db):
    limit, page = 3, 1
    user_list = await db.users.get_all(limit=limit, page=page, router_prefix='/api/users')
    assert user_list
    assert user_list.count
    assert user_list.result
    assert user_list.next or not user_list.next
    assert user_list.previous or not user_list.previous
    assert user_list.count >= len(user_list.result)
    assert user_list.result[-1].email
    assert user_list.result[-1].username
    assert user_list.result[-1].id
    assert user_list.result[-1].first_name or not user_list.result[-1].first_name
    assert user_list.result[-1].last_name or not user_list.result[-1].last_name
    assert user_list.result[-1].is_subscribed or not user_list.result[-1].is_subscribed
    assert len(user_list.result) <= limit

    get_one_user_or_none = await db.users.get_one_or_none(user_id=user_list.result[-1].id)
    assert get_one_user_or_none.id
    assert get_one_user_or_none.email
    assert get_one_user_or_none.username
    assert get_one_user_or_none.first_name or not get_one_user_or_none.first_name
    assert get_one_user_or_none.last_name or not get_one_user_or_none.last_name
    assert get_one_user_or_none.is_subscribed or not get_one_user_or_none.is_subscribed

    get_one_user_or_none = await db.users.get_one_or_none(user_id=user_list.result[-1].id + 1)
    assert not get_one_user_or_none

    get_user_hashed_password = await db.users.get_user_hashed_password(
        user_id=user_list.result[-1].id
    )
    assert isinstance(get_user_hashed_password.hashed_password, str)
