import sys
from http.client import responses
from pathlib import Path
from pyexpat.errors import messages

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine  # noqa

from backend.src.api.routers.ingredients import \
    router as ingredient_router  # noqa
from backend.src.api.routers.only_for_admins import \
    router as admin_router  # noqa
from backend.src.api.routers.recipes import favorite_recipe_router  # noqa
from backend.src.api.routers.recipes import recipe_router, shopping_cart_router
from backend.src.api.routers.subscriptions import subscription_router  # noqa
from backend.src.api.routers.tags import router as tag_touter  # noqa
from backend.src.api.routers.users import user_router  # noqa
from backend.src.constants import MOUNT_PATH  # noqa
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from backend.src.constants import MAX_EMAIL_LENGTH


origins = [
    "http://localhost",
    "http://localhost:8000",
]

app = FastAPI()
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(exc.errors())
    exc_dict = dict()
    for err in exc.errors():
        if 'String should have at most 150 characters' in err['msg']:
            print(True)
            message = f'Максимальная длина поля {err["loc"][1]} составляет {err["ctx"]["max_length"]} символов.'
            exc_dict[err['loc'][1]] = message
        if 'value is not a valid email address: The email address is too long before the @-sign' in err['msg']:
            message = f'Максимальная длина поля {err["loc"][1]} составляет {MAX_EMAIL_LENGTH} символов.'
            exc_dict[err['loc'][1]] = message
    content_dict = {}
    if len(exc_dict) > 0:
        content_dict['content'] = jsonable_encoder({"detail": exc_dict})
    else:
        content_dict['content'] =jsonable_encoder({"detail": exc.errors(), "body": exc.body})
    response = JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, **content_dict)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    MOUNT_PATH,
    StaticFiles(directory='src/media/recipes/images')
)
app.include_router(subscription_router)
app.include_router(user_router)
app.include_router(ingredient_router)
app.include_router(admin_router)
app.include_router(tag_touter)
app.include_router(favorite_recipe_router)
app.include_router(shopping_cart_router)
app.include_router(recipe_router)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
