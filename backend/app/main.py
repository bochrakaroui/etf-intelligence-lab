from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.issuers import router as issuers_router
from app.api.routes import router
from app.core.config import get_settings
from app.repositories.cached_repository import CachedParquetETFRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    repository = CachedParquetETFRepository(settings.data_dir, settings.database_path)
    repository.bootstrap()
    app.state.repository = repository
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])
app.include_router(router)
app.include_router(issuers_router)




