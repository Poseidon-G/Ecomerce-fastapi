from fastapi import APIRouter
from app.api.v1.routes.endpoints.auth import router as auth_router
from app.api.v1.routes.endpoints.category import router as category_router
from app.api.v1.routes.endpoints.user import router as user_router
from app.api.v1.routes.endpoints.product import router as product_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(category_router)
api_router.include_router(product_router)