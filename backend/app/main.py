"""
FinSpeak Trader - FastAPI Backend
Multi-signal financial analysis engine.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    logger.info("FinSpeak Trader starting up...")

    # Pre-warm Ollama model
    from .services.sentiment_service import prewarm_model
    await prewarm_model()

    # Check InfluxDB health
    from .services.influx_service import check_health
    if await check_health():
        logger.info("InfluxDB connected")
    else:
        logger.warning("InfluxDB not reachable - market data will be unavailable")

    yield

    logger.info("FinSpeak Trader shutting down")


app = FastAPI(
    title="FinSpeak Trader API",
    description="Multi-signal financial analysis engine",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from .routers.market_data import router as market_router
from .routers.corporate_data import router as corporate_router
from .routers.sentiment import router as sentiment_router
from .routers.technical import router as technical_router

app.include_router(market_router)
app.include_router(corporate_router)
app.include_router(sentiment_router)
app.include_router(technical_router)


@app.get("/api/health")
async def health_check():
    """Basic health check endpoint."""
    from .services.influx_service import check_health
    influx_ok = await check_health()
    return {
        "status": "ok",
        "influxdb": "connected" if influx_ok else "unavailable",
    }
