"""
Configuration settings for PJe Automation.
"""

import os
from typing import Any, Dict


class PJeConfig:
    """Configuration class for PJe automation settings."""

    # URLs
    BASE_URL = "https://pje.tjmg.jus.br"
    LOGIN_URL = f"{BASE_URL}/pje/login.seam"
    CONSULTATION_URL = f"{BASE_URL}/pje/Processo/ConsultaProcesso/listView.seam"

    # Timeouts (in seconds)
    DEFAULT_TIMEOUT = 30
    LOGIN_TIMEOUT = 45
    DOWNLOAD_TIMEOUT = 60
    IFRAME_TIMEOUT = 30

    # Directories
    DATA_DIR = "data"
    LOGS_DIR = "logs"
    SCREENSHOTS_DIR = "screenshots"
    DEBUG_DIR = "debug"
    TEMP_DIR = "temp"

    # Browser settings
    BROWSER_OPTIONS = {
        "headless": False,
        "window_size": (1920, 1080),
        "disable_extensions": True,
        "no_sandbox": True,
        "disable_dev_shm_usage": True,
    }

    # Selectors
    SELECTORS = {
        "sso_iframe": "#ssoFrame",
        "username_field": "#username",
        "password_field": "#password",
        "submit_button": "input[type='submit']",
        "process_fields": {
            "sequential": "fPP:numeroProcesso:numeroSequencial",
            "digit": "fPP:numeroProcesso:numeroDigitoVerificador",
            "year": "fPP:numeroProcesso:Ano",
            "court": "fPP:numeroProcesso:NumeroOrgaoJustica",
        },
        "search_button": "input[value='Pesquisar']",
        "download_dropdown": "a.btn-menu-abas.dropdown-toggle[title*='Download']",
        "download_button": "navbar:j_id220",
    }

    # File patterns
    FILE_PATTERNS = {"pdf_url": "s3-pjedocumentos.tjmg.jus.br", "pdf_extension": ".pdf"}

    @classmethod
    def get_credentials(cls) -> Dict[str, str]:
        """Get credentials from environment variables."""
        username = os.getenv("PJE_USERNAME")
        password = os.getenv("PJE_PASSWORD")

        if not username or not password:
            raise ValueError(
                "PJE_USERNAME and PJE_PASSWORD must be set in environment variables"
            )

        return {"username": username, "password": password}

    @classmethod
    def validate_credentials(cls) -> bool:
        """Validate that required credentials are present."""
        credentials = cls.get_credentials()
        return all(credentials.values())

    @classmethod
    def get_directories(cls) -> Dict[str, str]:
        """Get all configured directories."""
        return {
            "data": cls.DATA_DIR,
            "logs": cls.LOGS_DIR,
            "screenshots": cls.SCREENSHOTS_DIR,
            "debug": cls.DEBUG_DIR,
            "temp": cls.TEMP_DIR,
        }
