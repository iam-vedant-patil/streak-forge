from backend.app.api.users import router as users_router
from fastapi import FastAPI

app = FastAPI(
    title="Streak Forge API",
    description="Backend API for the Streak Forge daily streak tracker.",
    version="0.1.0",
)

app.include_router(users_router)

@app.get("/")
def root():
    return {
        "message": "Streak Forge API is running successfully!",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
