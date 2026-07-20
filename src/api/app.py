"""FastAPI application factory."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    app = FastAPI(
        title="MaPrix API",
        description="Morocco Price Observatory",
        version="0.1.0",
    )

    @app.get("/health")  # type: ignore[untyped-decorator]
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
