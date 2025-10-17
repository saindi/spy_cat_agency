from fastapi import APIRouter

from app.api.routers.cat import router as cat_router
from app.api.routers.mission import router as mission_router

__all__ = ["router"]


router = APIRouter(prefix="/api")

router.include_router(cat_router)
router.include_router(mission_router)
