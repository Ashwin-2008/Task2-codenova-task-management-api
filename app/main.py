
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models.task import Task
from app.routers.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables when the application starts.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Task Management API",
    description=(
        "A REST API for managing tasks with priorities, statuses, "
        "due dates, filtering, sorting, and pagination."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Welcome to CodeNova Task Management API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


app.include_router(tasks_router)
