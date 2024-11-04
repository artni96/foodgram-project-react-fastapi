from fastapi import APIRouter
from backend.src.schemas.recipes import RecipeCreateRequest, RecipeCreate
from backend.src.schemas.tags import RecipeTagCreate
from backend.src.api.dependencies import UserDep, DBDep


router = APIRouter(prefix='/recipes', tags=['Рецепты',])

@router.get('/{id}')
async def get_recipe(
    db: DBDep,
    id: int
):
    result = await db.recipes.get_one_or_none(id=id)
    return result


@router.post('/')
async def create_recipe(
    db: DBDep,
    current_user: UserDep,
    recipe_data: RecipeCreateRequest
):
    _recipe_data = RecipeCreate(**recipe_data.model_dump())
    recipe = await db.recipes.create(data=_recipe_data)
    tags_data = recipe_data.tag
    recipe_tags_to_create = [RecipeTagCreate(
        recipe_id=recipe.id, tag_id=tag_id)
        for tag_id in tags_data
    ]
    await db.recipe_tags.bulk_create(recipe_tags_to_create)
    await db.commit()

    return {'status': 'OK'}
