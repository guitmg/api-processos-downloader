"""
Configuration settings for the API.
"""

import os
from typing import Optional


class Settings:
    """Application settings."""

    # API Configuration
    API_TITLE: str = "PJe Automation API"
    API_DESCRIPTION: str = "API para automação de download de processos do PJe TJMG"
    API_VERSION: str = "1.0.0"

    # Webhook Configuration
    WEBHOOK_URL: str = "https://web.furycloud.io/workspace/genai/verdi-flows/webhook-test/9bcb8b28-65b7-48c4-819e-89b05de0bf98"

    # Server Configuration
    SERVER_BASE_URL: str = os.getenv("SERVER_BASE_URL", "https://meuservidor.com")

    # File paths
    DOWNLOAD_DIR: str = "data"
    SCRIPT_PATH: str = "main.py"

    # Timeout settings
    WEBHOOK_TIMEOUT: int = 30
    SCRIPT_TIMEOUT: int = 300  # 5 minutes

    @classmethod
    def get_file_url(cls, filename: str) -> str:
        """Generate public URL for downloaded file."""
        return f"{cls.SERVER_BASE_URL}/static/{filename}"


# Global settings instance
settings = Settings()
