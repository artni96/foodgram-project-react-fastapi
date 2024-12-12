from backend.src.exceptions.base import FoodgramBaseException


class EmailNotRegisteredException(FoodgramBaseException):
    detail = 'Пользователь с указанным email не найден'


class IncorrectPasswordException(FoodgramBaseException):
    detail = 'Неверный пароль'


class IncorrectTokenException(FoodgramBaseException):
    detail = 'Невалидный токен'


class ExpiredTokenException(FoodgramBaseException):
    detail = 'Необходимо авторизоваться'


class OnlyForAdminException(FoodgramBaseException):
    detail = 'Доступно только администраторам'
