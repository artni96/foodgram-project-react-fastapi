import pytest


@pytest.mark.order(3)
async def test_user_repository(db):
    limit, page = 3, 1
    user_list = await db.users.get_all(limit=limit, page=page, router_prefix='/api/users')
    assert user_list, 'результат с списком пользователей не найден'
    assert user_list.count, 'поле count не найдено'
    assert user_list.results, 'поле results не найдено'
    assert user_list.next or not user_list.next, 'поле next не найдено'
    assert user_list.previous or not user_list.previous, 'поле previous не найдено'
    assert user_list.count >= len(user_list.results), ('в количество пользователей в results не должно превышать '
                                                      'значение count')
    assert user_list.results[-1].email, 'поле email не найдено'
    assert user_list.results[-1].username, 'поле username не найдено'
    assert user_list.results[-1].id, 'поле id не найдено'
    assert user_list.results[-1].first_name or not user_list.results[-1].first_name, 'поле first_name не найдено'
    assert user_list.results[-1].last_name or not user_list.results[-1].last_name, 'поле last_name не найдено'
    assert user_list.results[-1].is_subscribed or not user_list.results[-1].is_subscribed, 'поле is_subscribed не найдено'
    assert len(user_list.results) <= limit, 'limit при фильтрации не работает'

    get_one_user_or_none = await db.users.get_one_or_none(user_id=user_list.results[-1].id)
    print(get_one_user_or_none)
    assert get_one_user_or_none.id, 'поле id не найдено'
    assert get_one_user_or_none.email, 'поле email не найдено'
    assert get_one_user_or_none.username, 'поле username не найдено'
    assert get_one_user_or_none.first_name or not get_one_user_or_none.first_name, 'поле first_name не найдено'
    assert get_one_user_or_none.last_name or not get_one_user_or_none.last_name, 'поле last_name не найдено'
    assert get_one_user_or_none.is_subscribed or not get_one_user_or_none.is_subscribed, 'поле is_subscribed не найдено'

    get_one_user_or_none = await db.users.get_one_or_none(user_id=user_list.results[-1].id + 1)
    assert not get_one_user_or_none, 'При запросе несуществующего пользователя должно возвращаться None'
    #
    get_user_hashed_password = await db.users.get_user_hashed_password(
        id=user_list.results[-1].id
    )
    assert isinstance(get_user_hashed_password.hashed_password, str), 'корректный тип hashed_password - str'
