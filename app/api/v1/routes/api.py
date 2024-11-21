from fastapi import APIRouter
from app.api.v1.routes.endpoints.category import router as category_router

api_router = APIRouter()
api_router.include_router(category_router)