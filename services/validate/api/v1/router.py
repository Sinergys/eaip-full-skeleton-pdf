"""
Main API router for v1 endpoints.
Combines all v1 endpoints into a single router.
"""
from fastapi import APIRouter

from .endpoints import word_document

# Create main v1 router
api_router = APIRouter()

# Include word document validation endpoints
api_router.include_router(
    word_document.router,
    prefix="/v1",
    tags=["Word Document Validation"]
)
