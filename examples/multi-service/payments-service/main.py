from fastapi import FastAPI
from app.payments.routes import router as payments_router

app = FastAPI(title="Payments Service", version="1.0.0")

app.include_router(payments_router, prefix="/payments", tags=["payments"])


@app.get("/")
async def root():
    return {"service": "payments", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
