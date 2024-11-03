from fastapi import FastAPI
import uvicorn
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.src.api.routers.users import user_router # noqa
from backend.src.api.routers.subscriptions import subscription_router # noqa
from backend.src.api.routers.ingredients import router as ingredient_router


app = FastAPI()
app.include_router(user_router)
app.include_router(subscription_router)
app.include_router(ingredient_router)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
