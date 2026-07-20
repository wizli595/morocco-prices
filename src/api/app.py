"""FastAPI application factory."""

from fastapi import FastAPI

from src.api.routes import prices, products, sources, stats


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    app = FastAPI(
        title="MaPrix API",
        description="Morocco Price Observatory — query historical and current prices",
        version="0.1.0",
    )

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(stats.router)
    app.include_router(prices.router)
    app.include_router(products.router)
    app.include_router(sources.router)
    return app
