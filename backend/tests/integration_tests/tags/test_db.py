import pytest

from backend.src.schemas.tags import TagCreate


@pytest.mark.order(5)
async def test_tags_crud(db):
    tag_data = {"name": "ЗОЖ", "color": "#f5945c", "slug": "healthy-life-style"}
    tag_data = TagCreate.model_validate(tag_data)
    new_tag = await db.tags.create(tag_data)  # only for admins
    assert (
        new_tag.name == tag_data.name
    ), "значение name тега отличается от исходных данных"
    assert (
        new_tag.slug == tag_data.slug
    ), "значение slug тега отличается от исходных данных"
    assert (
        new_tag.color == tag_data.color
    ), "значение color тега отличается от исходных данных"
    assert isinstance(new_tag.id, int)

    get_tag_by_id = await db.tags.get_one_or_none(id=new_tag.id)
    assert (
        get_tag_by_id.name == tag_data.name
    ), "возвращается неверное значение name тега"
    assert (
        get_tag_by_id.slug == tag_data.slug
    ), "возвращается неверное значение slug тега"
    assert (
        get_tag_by_id.color == tag_data.color
    ), "возвращается неверное значение color тега"

    get_tag_list = await db.tags.get_all()
    assert (
        len(get_tag_list) == 4
    ), "возвращается неверное количество тегов после создания нового тега"

    await db.tags.delete(id=new_tag.id)  # only for admins
    get_tag_list = await db.tags.get_all()
    assert (
        len(get_tag_list) == 3
    ), "возвращается неверное количество тегов после удаления одного тега"
