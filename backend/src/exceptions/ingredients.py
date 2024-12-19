from backend.src.exceptions.base import FoodgramBaseException


class IngredientNotFoundException(FoodgramBaseException):
    detail = 'Указанных ингредиентов нет в БД.'
