from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.compare import router as compare_router
from app.api.v1.geo import router as geo_router
from app.api.v1.itineraries import router as itineraries_router
from app.api.v1.search import router as search_router
from app.api.v1.subscriptions import router as subscriptions_router
from app.api.v1.trips import router as trips_router
from app.api.v1.users import router as users_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(geo_router, prefix="/geo", tags=["geo"])
router.include_router(search_router, prefix="/search", tags=["search"])
router.include_router(compare_router, prefix="/compare", tags=["compare"])
router.include_router(trips_router, prefix="/trips", tags=["trips"])
router.include_router(itineraries_router, prefix="/itineraries", tags=["itineraries"])
router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(subscriptions_router, prefix="/subscriptions", tags=["subscriptions"])
router.include_router(users_router, prefix="/users", tags=["users"])
