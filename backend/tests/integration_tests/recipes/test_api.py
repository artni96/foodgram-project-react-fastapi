import pytest
from fastapi import status

from backend.tests.conftest import PARAMS_MAX_LENGTH


@pytest.mark.parametrize(
    "name, text, cooking_time, tags, ingredients, image, status_code",
    [
        (
            "test name",
            "test text",
            10,
            [2, 3],
            [{"id": 1, "amount": 100}, {"id": 2, "amount": 200}],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1"
            "/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_201_CREATED,
        ),
        (
            "test name",
            "test text",
            10,
            [1, 2],
            [{"id": 21, "amount": 100}, {"id": 22, "amount": 200}],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1"
            "/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_400_BAD_REQUEST,
        ),
        (
            "test name",
            "test text",
            10,
            [1, 5],
            [{"id": 1, "amount": 100}, {"id": 2, "amount": 200}],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1"
            "/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_400_BAD_REQUEST,
        ),
        (
            f'{"".join(["t"] * (PARAMS_MAX_LENGTH+1))}',
            "test text",
            10,
            [2, 3],
            [{"id": 1, "amount": 100}, {"id": 2, "amount": 200}],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1"
            "/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_400_BAD_REQUEST,
        ),
    ],
)
@pytest.mark.order(9)
async def test_recipe_creating(
    auth_ac, name, text, cooking_time, tags, ingredients, image, status_code
):
    new_recipe = await auth_ac.post(
        "/api/recipes",
        json={
            "name": name,
            "text": text,
            "cooking_time": cooking_time,
            "tags": tags,
            "ingredients": ingredients,
            "image": image,
        },
    )
    assert (
        new_recipe.status_code == status_code
    ), f"статус ответа отличается от {status_code}"
    if new_recipe.status_code == status.HTTP_201_CREATED:
        assert new_recipe.json()["name"] == name, "в ответе отсутствует поле name"
        assert new_recipe.json()["text"] == text, "в ответе отсутствует поле text"
        assert (
            new_recipe.json()["cooking_time"] == cooking_time
        ), "в ответе отсутствует поле cooking_time"
        assert "image" in new_recipe.json(), "в ответе отсутствует поле image"


@pytest.mark.parametrize(
    "name, text, cooking_time, tags, ingredients, image, status_code",
    [
        (
            "updated name",
            "updated text",
            20,
            [1, 1, 1, 1],
            [{"id": 5, "amount": 100}, {"id": 5, "amount": 200}],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1"
            "/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_200_OK,
        ),
        (
            "updated name",
            "updated text",
            20,
            [1, 2, 3, 4],
            [{"id": 6, "amount": 200}, {"id": 6, "amount": 300}],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1"
            "/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_400_BAD_REQUEST,
        ),
        (
            f'{"".join(["t"] * (PARAMS_MAX_LENGTH+1))}',
            "updated text",
            20,
            [4, 4, 4, 4],
            [{"id": 5, "amount": 100}, {"id": 5, "amount": 200}],
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1"
            "/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            status.HTTP_400_BAD_REQUEST,
        ),
    ],
)
@pytest.mark.order(10)
async def test_recipe_updating(
    auth_ac, name, text, cooking_time, tags, ingredients, image, status_code
):
    recipes = await auth_ac.get("/api/recipes")
    recipe_to_update = recipes.json()["results"][0]["id"]
    updated_recipe = await auth_ac.patch(
        f"/api/recipes/{recipe_to_update}",
        json={
            "name": name,
            "text": text,
            "cooking_time": cooking_time,
            "tags": tags,
            "ingredients": ingredients,
            "image": image,
        },
    )
    assert (
        updated_recipe.status_code == status_code
    ), f"статус ответа отличается от {status_code}"
    if updated_recipe.status_code == status.HTTP_200_OK:
        assert updated_recipe.json()["name"] == name, "в ответе отсутствует поле name"
        assert updated_recipe.json()["text"] == text, "в ответе отсутствует поле text"
        assert (
            updated_recipe.json()["cooking_time"] == cooking_time
        ), "в ответе отсутствует поле cooking_time"
        assert "image" in updated_recipe.json(), "в ответе отсутствует поле image"


@pytest.mark.order(11)
async def test_recipe_removing(auth_ac):
    recipes = await auth_ac.get("/api/recipes")
    recipe_to_delete = recipes.json()["results"][0]["id"]
    removed_recipe = await auth_ac.delete(f"/api/recipes/{recipe_to_delete}")
    assert removed_recipe.status_code == status.HTTP_204_NO_CONTENT


# @pytest.mark.order(12)
class TestFilteredRecipe:
    recipes_data = {
        "author": {1: 3, 2: 4},
        "tags": {1: 4, 2: 4, 3: 4},
        "recipes_count": 7,
    }

    @pytest.mark.order(12)
    async def test_filtered_recipe_list(self, ac, recipe_bulk_creating_fixture):
        recipes_to_test = await ac.get("/api/recipes")
        assert (
            recipes_to_test.status_code == status.HTTP_200_OK
        ), "статус ответа отличается от 200"
        assert len(recipes_to_test.json()["results"]) == 3, (
            "неверное дефолтное количество рецептов в results (в "
            "проекте по дефолту - 3 рецепта)"
        )
        assert (
            "limit=3" in recipes_to_test.json()["next"]
        ), "неверное значение (ссылка) в поле next"
        assert (
            "page=2" in recipes_to_test.json()["next"]
        ), "неверное значение (ссылка) в поле next"
        assert not recipes_to_test.json()[
            "previous"
        ], "поле previous у первой страницы должно отсутсвовать"
        assert (
            recipes_to_test.json()["count"] == self.recipes_data["recipes_count"]
        ), "неверное значение count"

    @pytest.mark.order(13)
    async def test_filter_recipes_by_limit_and_page(self, ac):
        recipes_to_test = await ac.get("/api/recipes?page=2&limit=2")
        assert (
            len(recipes_to_test.json()["results"]) == 2
        ), "неверное количество рецептов в results"
        assert (
            "page=3" in recipes_to_test.json()["next"]
        ), "неверное значение (ссылка) в поле next"
        assert (
            "limit=2" in recipes_to_test.json()["previous"]
            and "limit=2" in recipes_to_test.json()["previous"]
        ), "неверное значение (ссылка) в поле previous"
        assert (
            "limit=2" in recipes_to_test.json()["next"]
            and "limit=2" in recipes_to_test.json()["next"]
        ), "неверное значение (ссылка) в поле next"
        assert (
            recipes_to_test.json()["count"] == self.recipes_data["recipes_count"]
        ), "неверное значение count"

    @pytest.mark.order(14)
    async def test_filter_recipes_by_limit_and_last_page(self, ac):
        recipes_to_test = await ac.get("/api/recipes?page=4&limit=2")
        assert (
            len(recipes_to_test.json()["results"]) == 1
        ), "неверное количество рецептов в results"
        assert not recipes_to_test.json()[
            "next"
        ], "поле next у последней страницы должно отсутсвовать"
        assert "page=3" in recipes_to_test.json()["previous"]
        assert (
            "limit=2" in recipes_to_test.json()["previous"]
            and "limit=2" in recipes_to_test.json()["previous"]
        ), "неверное значение (ссылка) в поле previous"
        assert (
            recipes_to_test.json()["count"] == self.recipes_data["recipes_count"]
        ), "неверное значение count"

    @pytest.mark.order(15)
    async def test_filter_recipes_by_author(self, ac):
        filtered_recipes_by_author_1 = await ac.get("/api/recipes?author=1&limit=2")
        assert (
            filtered_recipes_by_author_1.status_code == status.HTTP_200_OK
        ), "статус ответа отличается от 200"
        assert (
            len(filtered_recipes_by_author_1.json()["results"]) == 2
        ), "неверное количество рецептов в results"
        assert (
            filtered_recipes_by_author_1.json()["count"] == 3
        ), "неверное значение count"

        filtered_recipes_by_author_2 = await ac.get(
            "/api/recipes?author=2&page=2&limit=1"
        )
        assert (
            filtered_recipes_by_author_2.status_code == status.HTTP_200_OK
        ), "статус ответа отличается от 200"
        assert "limit=1" in filtered_recipes_by_author_2.json()["previous"], (
            "неверное значение (ссылка) в поле " "previous"
        )
        assert (
            "page=3" in filtered_recipes_by_author_2.json()["next"]
            and "limit=1" in filtered_recipes_by_author_2.json()["next"]
        ), "неверное значение (ссылка) в поле next"
        assert (
            len(filtered_recipes_by_author_2.json()["results"]) == 1
        ), "неверное количество рецептов в results"
        assert (
            filtered_recipes_by_author_2.json()["count"] == 4
        ), "неверное значение count"

    @pytest.mark.order(16)
    async def test_filter_recipes_by_tags(self, ac):
        filtered_rec_by_breakfast = await ac.get("/api/recipes?tags=breakfast&limit=2")
        assert (
            filtered_rec_by_breakfast.status_code == status.HTTP_200_OK
        ), "статус ответа отличается от 200"
        assert (
            len(filtered_rec_by_breakfast.json()["results"]) == 2
        ), "неверное количество рецептов в results"
        assert filtered_rec_by_breakfast.json()["count"] == 4, "неверное значение count"
        assert (
            "page=2" in filtered_rec_by_breakfast.json()["next"]
        ), "неверное значение (ссылка) в поле next"
        assert not filtered_rec_by_breakfast.json()[
            "previous"
        ], "поле previous у первой страницы должно отсутсвовать"

        filtered_rec_by_breakfast_and_dinner = await ac.get(
            "/api/recipes?page=3&tags=dinner&tags=breakfast&limit=1"
        )
        assert (
            filtered_rec_by_breakfast_and_dinner.status_code == status.HTTP_200_OK
        ), "статус ответа отличается от 200"
        assert len(filtered_rec_by_breakfast_and_dinner.json()["results"]) == 1, (
            "неверное количество рецептов в " "results"
        )
        assert (
            filtered_rec_by_breakfast_and_dinner.json()["count"] == 6
        ), "неверное значение count"
        assert (
            "page=4" in filtered_rec_by_breakfast_and_dinner.json()["next"]
            and "limit=1" in filtered_rec_by_breakfast_and_dinner.json()["next"]
        ), "неверное значение (ссылка) в поле next"
        assert (
            "page=2" in filtered_rec_by_breakfast_and_dinner.json()["previous"]
            and "limit=1" in filtered_rec_by_breakfast_and_dinner.json()["previous"]
        ), "неверное значение (ссылка) в поле previous"

        filtered_rec_by_breakfast_dinner_lunch = await ac.get(
            "/api/recipes?tags=dinner&tags=breakfast&tags=lunch&page=2&limit=4"
        )
        assert (
            filtered_rec_by_breakfast_dinner_lunch.status_code == status.HTTP_200_OK
        ), "статус ответа" "отличается от 200"
        assert len(filtered_rec_by_breakfast_dinner_lunch.json()["results"]) == 3, (
            "неверное количество рецептов в " "results"
        )
        assert (
            filtered_rec_by_breakfast_dinner_lunch.json()["count"] == 7
        ), "неверное значение count"

    @pytest.mark.order(17)
    async def test_filter_by_is_in_shopping_cart(self, auth_ac, another_auth_ac):
        recipe_to_shopping_cart = await auth_ac.get(
            "/api/recipes?is_in_shopping_cart=1&limit=2"
        )
        assert recipe_to_shopping_cart.status_code == status.HTTP_200_OK, (
            "статус ответа отличается от 200 у " "пользователя 1"
        )
        assert len(recipe_to_shopping_cart.json()["results"]) == 2, (
            "неверное количество рецептов в results у " "пользователя 1"
        )
        assert (
            recipe_to_shopping_cart.json()["count"] == 4
        ), "неверное значение count у пользователя 1"
        assert not recipe_to_shopping_cart.json()["previous"], (
            "поле previous у первой страницы должно отсутсвовать в "
            "запросе у пользователя 1"
        )
        assert (
            "page=2" in recipe_to_shopping_cart.json()["next"]
            and "limit=2" in recipe_to_shopping_cart.json()["next"]
        ), "неверное значение (ссылка) в поле next"
        recipe_to_shopping_cart_by_another = await another_auth_ac.get(
            "/api/recipes?is_in_shopping_cart=1&limit=2&page=1"
        )
        assert recipe_to_shopping_cart_by_another.status_code == status.HTTP_200_OK, (
            "статус ответа отличается от 200 " "у пользователя 2"
        )
        assert len(recipe_to_shopping_cart_by_another.json()["results"]) == 2, (
            "неверное количество рецептов в results" " у пользователя 2"
        )
        assert (
            recipe_to_shopping_cart_by_another.json()["count"] == 3
        ), "неверное значение count у пользователя 2"
        assert not recipe_to_shopping_cart_by_another.json()["previous"], (
            "поле previous у первой страницы должно "
            "отсутсвовать в запросе у пользователя 2"
        )
        assert (
            "page=2" in recipe_to_shopping_cart_by_another.json()["next"]
            and "limit=2" in recipe_to_shopping_cart_by_another.json()["next"]
        ), "неверное значение (ссылка) в поле next"

    @pytest.mark.order(18)
    async def test_filter_by_is_favorited(self, auth_ac, another_auth_ac):
        recipe_to_shopping_cart = await auth_ac.get(
            "/api/recipes?is_favorited=1&limit=2&page=2"
        )
        assert recipe_to_shopping_cart.status_code == status.HTTP_200_OK, (
            "статус ответа отличается от 200 у " "пользователя 1"
        )
        assert len(recipe_to_shopping_cart.json()["results"]) == 1, (
            "неверное количество рецептов в results у " "пользователя 1"
        )
        assert (
            recipe_to_shopping_cart.json()["count"] == 3
        ), "неверное значение count у пользователя 1"
        assert not recipe_to_shopping_cart.json()["next"], (
            "поле next у последней страницы должно отсутсвовать в "
            "запросе у пользователя 1"
        )
        assert "limit=2" in recipe_to_shopping_cart.json()["previous"], (
            "неверное значение (ссылка) в поле previous в " "запросе у пользователя 1"
        )

        recipe_to_shopping_cart_by_another = await another_auth_ac.get(
            "/api/recipes?is_favorited=1&limit=1&page=2"
        )
        assert recipe_to_shopping_cart_by_another.status_code == status.HTTP_200_OK, (
            "статус ответа отличается от 200 " "у пользователя 2"
        )
        assert len(recipe_to_shopping_cart_by_another.json()["results"]) == 1, (
            "неверное количество рецептов в results" " у пользователя 2"
        )
        assert (
            recipe_to_shopping_cart_by_another.json()["count"] == 4
        ), "неверное значение count у пользователя 2"
        assert "limit=1" in recipe_to_shopping_cart_by_another.json()["previous"], (
            "неверное значение (ссылка) в поле "
            "previous в запросе у "
            "пользователя 2"
        )

        assert (
            "page=3" in recipe_to_shopping_cart_by_another.json()["next"]
            and "limit=1" in recipe_to_shopping_cart_by_another.json()["next"]
        ), "неверное значение (ссылка) в поле next в запросе у пользователя 2"

    @pytest.mark.order(19)
    async def test_full_filtering_recipes(
        self, auth_ac, another_auth_ac, test_recipe_with_all_params
    ):
        filtered_recipes = await auth_ac.get(
            "/api/recipes?is_in_shopping_cart=1&is_favorited=1&page=1&limit=2&tag=breakfast&tags=lunch"
        )
        assert (
            filtered_recipes.status_code == status.HTTP_200_OK
        ), "статус ответа отличается от 200 у пользователя 1"
        assert (
            len(filtered_recipes.json()["results"]) == 1
        ), "неверное количество рецептов в results у пользователя 1"
        assert (
            filtered_recipes.json()["count"] == 1
        ), "неверное значение count у пользователя 1"
        assert not filtered_recipes.json()[
            "next"
        ], "поля next не должно быть в ответе у пользователя 1"
        assert not filtered_recipes.json()[
            "previous"
        ], "поля previous не должно быть в ответе у пользователя 1"

        filtered_recipes_by_another = await another_auth_ac.get(
            "/api/recipes?is_in_shopping_cart=1&is_favorited=1&page=1&limit=2&tag=breakfast&tags=lunch"
        )
        assert filtered_recipes_by_another.status_code == status.HTTP_200_OK, (
            "статус ответа отличается от 200 у " "пользователя 2"
        )
        assert len(filtered_recipes_by_another.json()["results"]) == 0, (
            "неверное количество рецептов в results у " "пользователя 2"
        )
        assert (
            filtered_recipes_by_another.json()["count"] == 0
        ), "неверное значение count у пользователя 2"
        assert not filtered_recipes_by_another.json()[
            "next"
        ], "поля next не должно быть в ответе у пользователя 2"
        assert not filtered_recipes_by_another.json()["previous"], (
            "поля previous не должно быть в ответе у " "пользователя 2"
        )

    @pytest.mark.order(20)
    async def test_clean_up_recipes(self, db, removing_recipes_after_tests):
        assert (
            not removing_recipes_after_tests
        ), "все рецепты должны быть удалены после тестов"
