"""
Configuration settings for Word Document Validator.
Loads settings from environment variables with fallback defaults.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file from current directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings for Word Document Validator."""
    
    # ============ Paths ============
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "/tmp"))
    GOST_TEMPLATE_PATH: Path = Path(
        os.getenv(
            "GOST_TEMPLATE_PATH",
            str(Path(__file__).parent.parent.parent.parent.parent / "templates" / "pcm690" / "energy_audit_template.docx")
        )
    )
    
    # ============ Database ============
    DATABASE_URL: str = os.getenv(
        "VALIDATOR_DATABASE_URL",
        "sqlite:///./word_validator_cache.db"
    )
    
    # ============ AI Configuration ============
    # Ollama (Local AI)
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral:7b")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "300"))  # 5 minutes
    USE_OLLAMA: bool = os.getenv("USE_OLLAMA", "true").lower() == "true"  # Feature flag
    
    # DeepSeek API (Cloud AI)
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_URL: str = os.getenv(
        "DEEPSEEK_API_URL",
        "https://api.deepseek.com/v1/chat/completions"
    )
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_MAX_TOKENS: int = int(os.getenv("DEEPSEEK_MAX_TOKENS", "4000"))
    DEEPSEEK_TIMEOUT: int = int(os.getenv("DEEPSEEK_TIMEOUT", "300"))  # 5 minutes
    
    # ============ Processing Configuration ============
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    CHUNK_SIZE_TOKENS: int = int(os.getenv("CHUNK_SIZE_TOKENS", "20000"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "2"))
    RETRY_DELAY_SECONDS: int = int(os.getenv("RETRY_DELAY_SECONDS", "5"))
    
    # ============ Cache Configuration ============
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL_DAYS: int = int(os.getenv("CACHE_TTL_DAYS", "30"))
    
    @classmethod
    def validate(cls) -> None:
        """Validate critical settings."""
        if not cls.DEEPSEEK_API_KEY:
            raise ValueError(
                "DEEPSEEK_API_KEY is required. Set it in environment variables."
            )
        
        if not cls.GOST_TEMPLATE_PATH.exists():
            raise FileNotFoundError(
                f"GOST template not found at: {cls.GOST_TEMPLATE_PATH}"
            )
        
        if not cls.TEMP_DIR.exists():
            cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
