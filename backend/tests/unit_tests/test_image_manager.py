import os

from backend.src.utils.image_manager import ImageManager

async def test_create_random_name(test_base64_fixture):
    test_base64_string = test_base64_fixture
    random_name = ImageManager().create_random_name(base64_string=test_base64_string)
    assert isinstance(random_name, str)

async def test_base64_to_file_and_vice_versa(test_base64_fixture):
    test_base64_string = test_base64_fixture
    generated_name = ImageManager().create_random_name(base64_string=test_base64_string)
    ImageManager().base64_to_file(base64_string=test_base64_string, image_name=generated_name)
    assert os.path.exists(f'src/media/recipes/images/{generated_name}')

    encoded_image = ImageManager().file_to_base64(generated_name)
    assert encoded_image == test_base64_string

    ImageManager().delete_file(generated_name)
    assert not os.path.exists(f'src/media/recipes/images/{generated_name}')
