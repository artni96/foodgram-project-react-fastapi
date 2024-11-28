import pytest
from fastapi import status


@pytest.mark.order(6)
async def test_get_tag(ac):
    tags_result = await ac.get('/api/tags')
    assert tags_result.status_code == status.HTTP_200_OK, 'статус ответа отличается от 200'

    assert len(tags_result.json()) == 3, 'неверное количество тегов в ответе'
    tag_by_id = await ac.get(f'/api/tags/{tags_result.json()[-1]["id"]}')
    assert tags_result.status_code == status.HTTP_200_OK,'статус ответа отличается от 200'
    assert len(tag_by_id.json()) == 4, 'Корректные поля в ответе: id, name, color, slug'
    assert 'id' in tag_by_id.json(), 'В ответе должно быть поле id'
    assert 'name' in tag_by_id.json(), 'В ответе должно быть поле name'
    assert 'color' in tag_by_id.json(), 'В ответе должно быть поле color'
    assert 'slug' in tag_by_id.json(), 'В ответе должно быть поле slug'
