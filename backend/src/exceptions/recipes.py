from backend.src.exceptions.base import FoodgramBaseException


class MainDataRecipeAtModifyingException(FoodgramBaseException):
    detail = 'Проверьте поля name, text, cooking_time, image'


class RecipeNotFoundException(FoodgramBaseException):
    detail = 'Рецепт с указанным id не найден.'


class OnlyAuthorCanEditRecipeException(FoodgramBaseException):
    detail = 'Редактирование рецепта доступна только его автору.'


class RecipeAlreadyIsInShoppingListException(FoodgramBaseException):
    detail = 'Рецепт уже в списке покупок.'


class RecipeAlreadyIsFavoritedException(FoodgramBaseException):
    detail = 'Рецепт уже в избранном.'


class RecipeNotFavoritedException(FoodgramBaseException):
    detail = 'Рецепт не найден в избранном'


class RecipeNotInShoppingListException(FoodgramBaseException):
    detail = 'Рецепт не найден в списке покупок'
