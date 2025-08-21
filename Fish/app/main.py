from fastapi import FastAPI
from app.api import workspace_routes
from app.api import user_routes
from app.api import source_routes
from app.api import document_routes
from app.core.config import settings
from app.db.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SwordFish API",
    description="A FastAPI application for SwordFish project",
    version="1.0.0",
    debug=settings.DEBUG
)


app.include_router(user_routes.router)
app.include_router(workspace_routes.router)
app.include_router(source_routes.router)
app.include_router(document_routes.router)


@app.get("/")
async def root():
    return {"message": "Welcome to SwordFish API!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "swordfish-api"}

