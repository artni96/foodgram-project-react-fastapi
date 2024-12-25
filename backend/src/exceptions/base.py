class FoodgramBaseException(Exception):
    detail = "Базовое исключение"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectAlreadyExistsException(FoodgramBaseException):
    detail = "Объект с указанными данными уже существует"


class ObjectNotFoundException(FoodgramBaseException):
    detail = "Объект не найден"
