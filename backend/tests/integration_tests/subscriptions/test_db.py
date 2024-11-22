import pytest

from backend.src.schemas.subscriptions import SubscriptionCreate


@pytest.mark.order(7)
async def test_subscription_crud(db):
    users = await db.users.get_all(limit=2, page=1, router_prefix='/api/users')
    author, subscriber = users.result[0], users.result[1]
    sub_data = SubscriptionCreate(author_id = author.id, subscriber_id=subscriber.id)
    await db.subscriptions.create(sub_data)
    await db.commit()

    user_subs = await db.subscriptions.get_user_subs(
        user_id=subscriber.id,
        limit=3,
        page=1,
        recipes_limit=3,
        offset=0,
        router_prefix='/api/subscriptions'
    )
    assert len(user_subs.result) == 1
    assert user_subs.result[-1].id == author.id
    assert user_subs.result[-1].username == author.username
    assert user_subs.result[-1].email == author.email
    assert user_subs.result[-1].first_name == author.first_name
    assert user_subs.result[-1].last_name == author.last_name
    assert user_subs.result[-1].is_subscribed == True

    await db.subscriptions.delete(author_id=author.id, subscriber_id=subscriber.id)
    user_subs = await db.subscriptions.get_user_subs(
        user_id=subscriber.id,
        limit=3,
        page=1,
        recipes_limit=3,
        offset=0,
        router_prefix='/api/subscriptions'
    )
    assert len(user_subs.result) == 0
