"""
Pydantic models for Word Document Validator.
Defines request/response schemas and internal data structures.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


# ============ API Request/Response Models ============

class CheckReportRequest(BaseModel):
    """Request model for report validation endpoint."""
    # File will be uploaded as multipart/form-data
    # This model is for additional metadata if needed


class CheckReportResponse(BaseModel):
    """Response model for report validation endpoint."""
    message: str = Field(..., description="Status message")
    file_path: str = Field(..., description="Path to validated report")
    from_cache: bool = Field(default=False, description="Whether result was from cache")
    processing_time_seconds: Optional[float] = Field(None, description="Processing duration")
    file_hash: Optional[str] = Field(None, description="SHA-256 hash of input file")


# ============ Internal Processing Models ============

class ExtractedObject(BaseModel):
    """Model for extracted non-text objects (images, tables, etc)."""
    id: str = Field(..., description="Unique object ID (e.g., OBJ_001)")
    object_type: str = Field(..., description="Type: image, table, chart, formula")
    binary_data: Optional[bytes] = Field(None, description="Binary content")
    caption: Optional[str] = Field(None, description="Object caption text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TextChunk(BaseModel):
    """Model for text chunk during processing."""
    index: int = Field(..., description="Chunk sequence number (0-based)")
    text: str = Field(..., description="Chunk text content with markers")
    token_count: int = Field(..., description="Approximate token count")
    is_section_interrupted: bool = Field(default=False, description="If chunk ends mid-section")
    chapter_name: Optional[str] = Field(None, description="Chapter name if interrupted")


class OllamaAnalysisResult(BaseModel):
    """Model for Ollama analysis response."""
    issues: List[str] = Field(default_factory=list, description="List of detected issues")
    fixes: List[str] = Field(default_factory=list, description="List of suggested fixes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional analysis data")


class DeepSeekCorrectionResult(BaseModel):
    """Model for DeepSeek correction response."""
    corrected_text: str = Field(..., description="Corrected chunk text with markers preserved")
    recommendations: List[str] = Field(default_factory=list, description="List of recommendations")
    chunk_index: int = Field(..., description="Which chunk this result belongs to")


class ProcessingSummary(BaseModel):
    """Model for final processing summary."""
    total_chunks: int = Field(..., description="Total number of chunks processed")
    total_recommendations: int = Field(..., description="Total recommendations count")
    total_issues_found: int = Field(..., description="Total issues detected by Ollama")
    processing_time_seconds: float = Field(..., description="Total processing time")
    recommendations_by_category: Dict[str, int] = Field(
        default_factory=dict, 
        description="Recommendations grouped by PKM section"
    )


class CachedResult(BaseModel):
    """Model for cached validation result."""
    file_hash: str = Field(..., description="SHA-256 hash of input file")
    result_file_path: str = Field(..., description="Path to cached result file")
    created_at: datetime = Field(..., description="When cache entry was created")
    file_size: int = Field(..., description="Original file size in bytes")
    original_filename: str = Field(..., description="Original file name")


# ============ Error Models ============

class ValidationError(BaseModel):
    """Model for validation errors."""
    error_type: str = Field(..., description="Error type from ErrorType constants")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ProcessingError(BaseModel):
    """Model for processing errors with retry information."""
    error_type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    chunk_index: Optional[int] = Field(None, description="Chunk that failed")
    retry_count: int = Field(default=0, description="Number of retries attempted")
    is_fatal: bool = Field(default=False, description="If error is unrecoverable")
