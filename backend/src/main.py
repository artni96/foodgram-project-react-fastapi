import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.src.api.routers.ingredients import \
    router as ingredient_router  # noqa
from backend.src.api.routers.only_for_admins import \
    router as admin_router  # noqa
from backend.src.api.routers.recipes import router as recipe_router  # noqa
from backend.src.api.routers.subscriptions import subscription_router  # noqa
from backend.src.api.routers.tags import router as tag_touter  # noqa
from backend.src.api.routers.users import user_router  # noqa
from backend.src.constants import MOUNT_PATH  # noqa

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    MOUNT_PATH,
    StaticFiles(directory='backend/src/media/recipes/images')
)
app.include_router(subscription_router)
app.include_router(user_router)
app.include_router(ingredient_router)
app.include_router(admin_router)
app.include_router(tag_touter)
app.include_router(recipe_router)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
