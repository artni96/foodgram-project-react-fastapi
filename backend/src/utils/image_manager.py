import base64
import random
import string

from fastapi import HTTPException, status
import os


class ImageManager:

    def base64_to_file(self, base64_string, image_name):
        if (
            isinstance(base64_string, str) and
            base64_string.startswith('data:image')
        ):
            format, imgstr = base64_string.split(';base64,')
            ext = format.split('/')[-1]
            image_bytes = base64.b64decode(imgstr)

            with open(
                f'backend/src/media/recipes/images/{image_name}.{ext}',
                'wb'
            ) as f:
                f.write(image_bytes)
            return f'{image_name}.{ext}'
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Неверный формат картинки'
            )

    def delete_file(self, file_name_with_ext):
        file_path = f'backend/src/media/recipes/images/{file_name_with_ext}'
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise FileNotFoundError('Файл не найден')

    def file_to_base64(self, file_name_with_ext):
        with open(file_name_with_ext, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            return encoded_string

    def create_random_name(self):
        random_name = ''
        while len(random_name) < 10:
            random_name += random.choice(string.ascii_letters)
        return random_name
