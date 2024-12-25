import pytest

from backend.src.schemas.subscriptions import SubscriptionCreate


@pytest.mark.order(7)
async def test_subscription_crud(db):
    users = await db.users.get_all(limit=2, page=1, router_prefix="/api/users")
    author, subscriber = users.results[0], users.results[1]
    sub_data = SubscriptionCreate(author_id=author.id, subscriber_id=subscriber.id)
    await db.subscriptions.create(data=sub_data, recipes_limit=3)
    await db.commit()

    user_subs = await db.subscriptions.get_user_subs(
        user_id=subscriber.id,
        limit=3,
        page=1,
        recipes_limit=3,
        offset=0,
        router_prefix="/api/subscriptions",
    )
    assert (
        len(user_subs.results) == 1
    ), "неверное количество подписок пользователя после создания подписки"
    assert (
        user_subs.results[-1].id == author.id
    ), "значение id пользователя отличается от исходных данных"
    assert user_subs.results[-1].username == author.username, (
        "значение username пользователя отличается от исходных " "данных"
    )
    assert (
        user_subs.results[-1].email == author.email
    ), "значение email пользователя отличается от исходных данных"
    assert user_subs.results[-1].first_name == author.first_name, (
        "значение first_name пользователя отличается от " "исходных данных"
    )
    assert user_subs.results[-1].last_name == author.last_name, (
        "значение last_name пользователя отличается от " "исходных данных"
    )
    assert user_subs.results[-1].is_subscribed is True, (
        "при успешном создании подписки значение поля is_subscribed " "должно быть True"
    )

    await db.subscriptions.delete(author_id=author.id, subscriber_id=subscriber.id)
    user_subs = await db.subscriptions.get_user_subs(
        user_id=subscriber.id,
        limit=3,
        page=1,
        recipes_limit=3,
        offset=0,
        router_prefix="/api/subscriptions",
    )
    assert (
        len(user_subs.results) == 0
    ), "неверное количество подписок пользователя после отмены подписки"
