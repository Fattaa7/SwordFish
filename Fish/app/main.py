from fastapi import FastAPI
from app.api import conversation_routes
from app.api import workspace_routes
from app.api import user_routes
from app.api import source_routes
from app.api import document_routes
from app.core.config import settings
from app.db.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SwordFish API",
    description="A FastAPI application for SwordFish project",
    version="1.0.0",
    debug=settings.DEBUG
)

app.mount("/files", StaticFiles(directory="/tmp"), name="files")

origins = [
    "http://localhost:3000",  # Vue dev server
    "http://127.0.0.1:3000",  # just in case
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # Allow all methods (POST, GET, etc.)
    allow_headers=["*"],   # Allow all headers (Authorization, etc.)
)

app.include_router(user_routes.router)
app.include_router(workspace_routes.router)
app.include_router(source_routes.router)
app.include_router(document_routes.router)
app.include_router(conversation_routes.router)


@app.get("/")
async def root():
    return {"message": "Welcome to SwordFish API!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "swordfish-api"}

