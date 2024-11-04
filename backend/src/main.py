import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI

sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.src.api.routers.ingredients import \
    router as ingredient_router  # noqa
from backend.src.api.routers.only_for_admins import \
    router as admin_router  # noqa
from backend.src.api.routers.subscriptions import subscription_router  # noqa
from backend.src.api.routers.tags import router as tag_touter  # noqa
from backend.src.api.routers.users import user_router  # noqa

app = FastAPI()
app.include_router(user_router)
app.include_router(subscription_router)
app.include_router(ingredient_router)
app.include_router(admin_router)
app.include_router(tag_touter)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
