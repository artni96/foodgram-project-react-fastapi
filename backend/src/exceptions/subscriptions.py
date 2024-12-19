from backend.src.exceptions.base import FoodgramBaseException


class UniqueConstraintSubscriptionException(FoodgramBaseException):
    detail = 'Вы уже подписаны на данного пользователя!'


class FollowingYourselfException(FoodgramBaseException):
    detail = 'Вы не можете подписаться на себя'


class SubscriptionNotFoundException(FoodgramBaseException):
    detail = 'Подписка не найдена'
