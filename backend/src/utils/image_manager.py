import base64
import random
import string

from fastapi import HTTPException, status
import os


class ImageManager:
    @staticmethod
    def base64_to_file(base64_string, image_name):
        if isinstance(base64_string, str) and base64_string.startswith("data:image"):
            format, imgstr = base64_string.split(";base64,")
            image_bytes = base64.b64decode(imgstr)

            with open(f"src/media/recipes/images/{image_name}", "wb") as f:
                f.write(image_bytes)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат картинки",
            )

    @staticmethod
    def delete_file(file_name_with_ext):
        file_path = f"src/media/recipes/images/{file_name_with_ext}"
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise FileNotFoundError("Файл не найден")

    @staticmethod
    def file_to_base64(file_name_with_ext: str):
        with open(f"src/media/recipes/images/{file_name_with_ext}", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            result = (
                f'data:image/{file_name_with_ext.split(".")[1]};base64,'
                + encoded_string.decode("utf-8")
            )
            return result

    @staticmethod
    def create_random_name(base64_string):
        random_name = ""
        while len(random_name) < 10:
            random_name += random.choice(string.ascii_letters)
        format = base64_string.split(";base64,")[0]
        ext = format.split("/")[-1]
        return f"{random_name}.{ext}"
