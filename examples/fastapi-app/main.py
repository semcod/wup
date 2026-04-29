from fastapi import FastAPI
from app.users.routes import router as users_router

app = FastAPI(title="FastAPI Example", version="1.0.0")

app.include_router(users_router, prefix="/users", tags=["users"])


@app.get("/")
async def root():
    return {"message": "FastAPI Example App", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
