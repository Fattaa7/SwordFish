from fastapi import FastAPI
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


@app.get("/")
async def root():
    return {"message": "Welcome to SwordFish API!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "swordfish-api"}

