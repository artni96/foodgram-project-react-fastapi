import pytest
from fastapi import status


@pytest.mark.order(6)
async def test_get_tag(ac, tags_fixture):
    tags_result = await ac.get('/api/tags')
    assert tags_result.status_code == status.HTTP_200_OK

    assert len(tags_result.json()) == 3
    tag_by_id = await ac.get(f'/api/tags/{tags_result.json()[-1]["id"]}')
    assert tags_result.status_code == status.HTTP_200_OK
    assert 'id' in tag_by_id.json()
    assert 'name' in tag_by_id.json()
    assert 'color' in tag_by_id.json()
    assert 'slug' in tag_by_id.json()
    assert len(tag_by_id.json()) == 4
