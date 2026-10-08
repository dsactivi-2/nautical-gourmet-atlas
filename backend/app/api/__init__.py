from fastapi import APIRouter
from app.api import auth, users, categories, filters, partners, favorites, visits, treasures, context

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/me", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(filters.router, prefix="/filters", tags=["filters"])
api_router.include_router(partners.router, prefix="/partners", tags=["partners"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(visits.router, prefix="/visits", tags=["visits"])
api_router.include_router(treasures.router, prefix="/treasures", tags=["treasures"])
api_router.include_router(context.router, prefix="/context", tags=["context"])
