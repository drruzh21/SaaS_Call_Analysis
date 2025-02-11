from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    api_keys,
    login,
    proxy,
    tasks,
    users,
    users_gpt_filter_prompt,
)

api_router = APIRouter()
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    users_gpt_filter_prompt.router,
    prefix="/users",
    tags=["users"]
)
api_router.include_router(proxy.router, prefix="/proxy", tags=["proxy"])
api_router.include_router(tasks.router, prefix="/celery", tags=["celery"])


if __name__ == "__main__":
    print("hi")
