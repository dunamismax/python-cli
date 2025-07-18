"""FastAPI application main module."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from shared.config import init_config, get_config
from shared.database import init_db_manager, get_db_manager
from shared.logging import setup_logging, get_logger
from .routers import users_router, tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    config = get_config()
    logger = get_logger(__name__)
    
    logger.info("Starting up FastAPI application...")
    
    # Initialize database
    db_manager = init_db_manager(config.db.database_url)
    await db_manager.create_tables()
    
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    await db_manager.close()
    logger.info("Database connection closed")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = get_config()
    
    app = FastAPI(
        title=config.app_name,
        description=config.description,
        version=config.version,
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this properly in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(tasks_router, prefix="/api/v1")
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Welcome to the Python CLI API Server",
            "version": config.version,
            "docs": "/docs",
        }
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler."""
        logger = get_logger(__name__)
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.detail}
            )
        
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
    
    return app


def start_server():
    """Start the FastAPI server."""
    # Initialize configuration and logging
    config = init_config()
    setup_logging(
        level=config.log_level,
        log_file=config.logs_dir / "api_server.log",
        use_rich=True,
    )
    
    logger = get_logger(__name__)
    logger.info(f"Starting server on {config.api.host}:{config.api.port}")
    
    # Create and run the app
    app = create_app()
    
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.port,
        reload=config.api.reload,
        log_level=config.log_level.lower(),
    )


if __name__ == "__main__":
    start_server()