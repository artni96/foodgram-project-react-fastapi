from backend.src.exceptions.base import FoodgramBaseException


class TagNotFoundException(FoodgramBaseException):
    detail = 'Указанных тегов нет в БД.'
