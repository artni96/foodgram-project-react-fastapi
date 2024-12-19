from backend.src.exceptions.base import FoodgramBaseException


class MainDataRecipeAtModifyingException(FoodgramBaseException):
    detail = 'Проверьте поля name, text, cooking_time, image'


class RecipeNotFoundException(FoodgramBaseException):
    detail = 'Рецепт с указанным id не найден.'
