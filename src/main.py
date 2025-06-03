from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError as FastAPIRequestValidationError

from .config import settings
from .utils.logger import logger  # importe le logger
from .utils.exceptions import ItemNotFoundError  # importe ton exception personnalisée

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
async def startup_event():
    logger.info("Application démarrée")  # log au démarrage

@app.get("/")
def read_root():
    logger.debug("Route racine appelée")  # log debug sur la racine
    return {"message": "Welcome to the Library Management System API"}

# Gestionnaires d'exceptions personnalisés

@app.exception_handler(ItemNotFoundError)
async def item_not_found_exception_handler(request: Request, exc: ItemNotFoundError):
    logger.error(f"ItemNotFoundError: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "type": "ItemNotFoundError"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"error": "Validation failed", "details": exc.errors()}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

# Exemple d'utilisation d'exception personnalisée

@app.get("/items/{item_id}")
def get_item(item_id: int):
    fake_db = {1: "Book A", 2: "Book B"}
    if item_id not in fake_db:
        raise ItemNotFoundError(item_id)
    logger.info(f"Item {item_id} retourné")
    return {"item_id": item_id, "name": fake_db[item_id]}
