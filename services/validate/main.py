"""
Main FastAPI application for Word Document Validation service.
Integrates word document validation with existing validation endpoints.
"""
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.v1.router import api_router
from core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="EAIP Validation Service",
    version="0.2.0",
    description="Word document validation and general data validation service"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Legacy Validation Endpoints ============
# Сохраняем существующие endpoints для обратной совместимости

class ValidateReq(BaseModel):
    batchId: str


@app.get("/health")
def health():
    """Legacy health check endpoint."""
    return {"service": "validate", "status": "ok"}


@app.post("/validate/run")
def validate_run(req: ValidateReq):
    """
    Legacy validation endpoint.
    Сохранён для обратной совместимости.
    """
    try:
        if not req.batchId or not req.batchId.strip():
            raise HTTPException(
                status_code=400, detail="batchId is required and cannot be empty"
            )

        # Заглушка: всегда «passed»
        return {"batchId": req.batchId, "passed": True, "issues": []}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


# ============ Include Word Validation API ============
app.include_router(api_router, prefix="/api")


# ============ Startup Events ============

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting EAIP Validation Service...")
    
    # Validate critical settings
    try:
        settings.validate()
        logger.info("✅ Configuration validated successfully")
        
        # Log configuration (without sensitive data)
        logger.info(f"TEMP_DIR: {settings.TEMP_DIR}")
        logger.info(f"GOST_TEMPLATE: {settings.GOST_TEMPLATE_PATH.name}")
        logger.info(f"Cache enabled: {settings.CACHE_ENABLED}")
        logger.info(f"Ollama URL: {settings.OLLAMA_URL}")
        logger.info(f"DeepSeek configured: {bool(settings.DEEPSEEK_API_KEY)}")
        
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.warning("Word validation endpoints will not work properly!")
    except FileNotFoundError as e:
        logger.error(f"❌ Template not found: {e}")
        logger.warning("Document assembly will fail!")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}", exc_info=True)
    
    logger.info("Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down EAIP Validation Service...")


# ============ Root Endpoint ============

@app.get("/")
def root():
    """Root endpoint with service information."""
    return {
        "service": "EAIP Validation Service",
        "version": "0.2.0",
        "endpoints": {
            "legacy_health": "/health",
            "legacy_validate": "/validate/run",
            "word_validation": "/api/v1/check-report/",
            "word_health": "/api/v1/health",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "features": [
            "Legacy batch validation",
            "Word document PKM-690 validation",
            "AI-powered text correction",
            "GOST document formatting"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
