from fastapi import APIRouter

from service.api.v1 import manage

api_router = APIRouter(prefix='/api/v1')
api_router.include_router(manage.router)
