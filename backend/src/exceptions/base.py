class FoodgramBaseException(Exception):
    detail = 'Базовое исключение'


class ObjectAlreadyExistsException(FoodgramBaseException):
    detail = 'Объект с указанными данными уже существует.'
