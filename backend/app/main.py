from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.tasks import router as tasks_router
from backend.app.api.users import router as users_router

app = FastAPI(
    title="Streak Forge API",
    description="Backend API for the Streak Forge daily streak tracker.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users_router)
app.include_router(tasks_router)

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
