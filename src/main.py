from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.routes import api_router
from .models import base, books, users, loans  # Importer les modèles pour Alembic
from src.logging_config import setup_logging
from src.exceptions import CustomException, custom_exception_handler

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Enregistre le handler pour CustomException
app.add_exception_handler(CustomException, custom_exception_handler)

# Configuration CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8000", "http://localhost:5000", "http://127.0.0.1:5000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Inclusion des routes API
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Library Management System API"}