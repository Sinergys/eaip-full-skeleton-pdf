"""
Pydantic models for EAIP ingest service API.

These models define the structure of request and response data
for API endpoints.
"""

from pydantic import BaseModel


class ValidateRequest(BaseModel):
    """
    Request model for validation endpoint.
    
    Attributes:
        batchId: Unique identifier for the batch to validate
    """
    batchId: str


class EnterpriseCreate(BaseModel):
    """
    Request model for creating a new enterprise.
    
    Attributes:
        name: Name of the enterprise
    """
    name: str


class EditablePayload(BaseModel):
    """
    Request model for editable text content.
    
    Attributes:
        text: Text content to be processed
    """
    text: str
