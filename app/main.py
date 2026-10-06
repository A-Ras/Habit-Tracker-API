import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import users, projects, tasks, habits, auth

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Moderner Lifespan-Handler für Startup & Shutdown."""
    # STARTUP
    logger.info("🚀 Application startup complete")
    yield
    # SHUTDOWN
    logger.info("👋 Application shutting down")


app = FastAPI(
    title="Habit Tracker API",
    description="Eine API zur Verwaltung von Aufgaben und Gewohnheiten.",
    version="0.8.1",
    lifespan=lifespan,  # ← Hier registriert
)


@app.get("/")
def read_root():
    return {"message": "Hallo! Die Habit Tracker API läuft. 🚀"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Router registrieren
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(habits.router)