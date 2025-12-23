"""
Custom exceptions for Word Document Validator.
Provides structured error handling throughout the application.
"""


class WordValidatorError(Exception):
    """Base exception for Word Validator."""
    pass


class FileValidationError(WordValidatorError):
    """Raised when file validation fails."""
    pass


class FileSizeError(FileValidationError):
    """Raised when file size exceeds limit."""
    pass


class FileFormatError(FileValidationError):
    """Raised when file format is invalid."""
    pass


class ProcessingError(WordValidatorError):
    """Raised when document processing fails."""
    pass


class ChunkingError(ProcessingError):
    """Raised when text chunking fails."""
    pass


class AIServiceError(WordValidatorError):
    """Base exception for AI service errors."""
    pass


class OllamaError(AIServiceError):
    """Raised when Ollama service fails."""
    pass


class DeepSeekError(AIServiceError):
    """Raised when DeepSeek API fails."""
    pass


class DeepSeekFormatError(DeepSeekError):
    """Raised when DeepSeek response format is invalid."""
    pass


class DeepSeekTimeoutError(DeepSeekError):
    """Raised when DeepSeek API times out."""
    pass


class CacheError(WordValidatorError):
    """Raised when cache operations fail."""
    pass


class TemplateError(WordValidatorError):
    """Raised when GOST template is missing or invalid."""
    pass


class DocumentAssemblyError(WordValidatorError):
    """Raised when final document assembly fails."""
    pass


class PKMRequirementsError(WordValidatorError):
    """Raised when PKM 690 requirements cannot be loaded."""
    pass


class ValidationError(WordValidatorError):
    """Raised when data validation fails."""
    pass


class SecurityError(WordValidatorError):
    """Raised when security validation fails."""
    pass
