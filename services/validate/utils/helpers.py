"""
Helper utilities for Word Document Validator.
Provides common functionality like hashing, token counting, etc.
"""
import hashlib
import re
from pathlib import Path
from typing import Optional

import tiktoken


def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of a file.
    
    Args:
        file_path: Path to file
    
    Returns:
        Hex digest of SHA-256 hash
    """
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Count tokens in text using tiktoken.
    
    Args:
        text: Text to count tokens for
        model: Model name for tokenizer (default: gpt-3.5-turbo)
    
    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base encoding (used by GPT-3.5/4)
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(text))


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename by removing invalid characters and limiting length.
    
    Args:
        filename: Original filename
        max_length: Maximum allowed length
    
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(sanitized) > max_length:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        max_name_length = max_length - len(ext) - 1
        sanitized = f"{name[:max_name_length]}.{ext}" if ext else name[:max_length]
    
    return sanitized


def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """
    Validate if file has allowed extension.
    
    Args:
        filename: Filename to validate
        allowed_extensions: Set of allowed extensions (e.g., {'.docx'})
    
    Returns:
        True if extension is allowed
    """
    ext = Path(filename).suffix.lower()
    return ext in allowed_extensions


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def extract_markers(text: str, pattern: str) -> list[str]:
    """
    Extract all markers matching pattern from text.
    
    Args:
        text: Text to search
        pattern: Regex pattern for markers
    
    Returns:
        List of matched markers
    """
    return re.findall(pattern, text)


def preserve_markers(original_text: str, corrected_text: str, pattern: str) -> str:
    """
    Ensure all markers from original text are preserved in corrected text.
    If markers are missing, re-insert them.
    
    Args:
        original_text: Original text with markers
        corrected_text: Corrected text (may have lost markers)
        pattern: Regex pattern for markers
    
    Returns:
        Corrected text with all markers preserved
    """
    original_markers = extract_markers(original_text, pattern)
    corrected_markers = extract_markers(corrected_text, pattern)
    
    missing_markers = set(original_markers) - set(corrected_markers)
    
    if not missing_markers:
        return corrected_text
    
    # Simple strategy: append missing markers at the end with warning
    # Better strategy would be context-based reinsertion
    result = corrected_text
    if missing_markers:
        result += "\n\n<!-- WARNING: Missing markers restored: " + ", ".join(missing_markers) + " -->"
    
    return result
