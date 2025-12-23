"""
Constants for Word Document Validator.
Defines markers, formats, and fixed values.
"""

# ============ Object Markers ============
OBJECT_MARKER_PREFIX = "[[OBJ_"
OBJECT_MARKER_SUFFIX = "]]"
OBJECT_MARKER_PATTERN = r"\[\[OBJ_\d+\]\]"

# ============ Section Break Markers ============
SECTION_INTERRUPTED_PREFIX = "[[SECTION_INTERRUPTED_AT_CHAPTER_"
SECTION_INTERRUPTED_SUFFIX = "]]"
CONTINUATION_PREFIX = "[[CONTINUATION_OF_CHAPTER_"
CONTINUATION_SUFFIX = "]]"

# ============ DeepSeek Response Markers ============
START_CORRECTED_TEXT = "[START_OF_CORRECTED_TEXT]"
END_CORRECTED_TEXT = "[END_OF_CORRECTED_TEXT]"
START_RECOMMENDATIONS = "[CHUNK_RECOMMENDATIONS]"
END_RECOMMENDATIONS = "[END_OF_RECOMMENDATIONS]"

# ============ Special Markers ============
FICTIONAL_DATA_MARKER = "[ВНИМАНИЕ: ПРИМЕР С ВЫМЫШЛЕННЫМИ ДАННЫМИ]"

# ============ File Validation ============
ALLOWED_EXTENSIONS = {".docx"}
MAX_FILENAME_LENGTH = 255

# ============ Processing Limits ============
MIN_CHUNK_SIZE_TOKENS = 5000
MAX_CHUNK_SIZE_TOKENS = 25000
DEFAULT_CHUNK_SIZE_TOKENS = 20000

# ============ Status Values ============
class ProcessingStatus:
    """Processing status constants."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


class ErrorType:
    """Error type constants for better categorization."""
    VALIDATION_ERROR = "validation_error"
    FILE_ERROR = "file_error"
    AI_ERROR = "ai_error"
    NETWORK_ERROR = "network_error"
    PROCESSING_ERROR = "processing_error"
    TIMEOUT_ERROR = "timeout_error"


# ============ PKM 690 Constants ============
PKM690_SECTIONS_COUNT = 8
PKM690_SECTION_TITLES = [
    "ВВЕДЕНИЕ",
    "ОБЩИЕ СВЕДЕНИЯ О ПРЕДПРИЯТИИ",
    "АНАЛИЗ ЭНЕРГОПОТРЕБЛЕНИЯ",
    "АНАЛИЗ ОБОРУДОВАНИЯ",
    "МЕРОПРИЯТИЯ ПО ЭНЕРГОСБЕРЕЖЕНИЮ",
    "ЭКОНОМИЧЕСКИЙ АНАЛИЗ",
    "ЗАКЛЮЧЕНИЕ",
    "ПРИЛОЖЕНИЯ",
]
