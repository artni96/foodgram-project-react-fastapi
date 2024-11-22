import pytest

from backend.src.schemas.tags import TagCreate

@pytest.mark.order(5)
async def test_tags_crud(db):
    tag_data = {
        "name": "Завтрак",
        "color": "#f5945c",
        "slug": "breakfast"
    }
    tag_data = TagCreate.model_validate(tag_data)
    new_tag = await db.tags.create(tag_data) # only for admins
    assert new_tag.name == tag_data.name
    assert new_tag.slug == tag_data.slug
    assert new_tag.color == tag_data.color
    assert isinstance(new_tag.id, int)

    get_tag_by_id = await db.tags.get_one_or_none(id=new_tag.id)
    assert get_tag_by_id.name == tag_data.name
    assert get_tag_by_id.slug == tag_data.slug
    assert get_tag_by_id.color == tag_data.color

    get_tag_list = await db.tags.get_all()
    assert len(get_tag_list) == 1

    await db.tags.delete(id=new_tag.id) # only for admins
    get_tag_list = await db.tags.get_all()
    assert not get_tag_list