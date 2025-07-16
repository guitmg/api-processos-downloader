"""
PJe Automation Package

This package provides automation tools for the PJe (Processo Judicial Eletrônico)
system of TJMG (Tribunal de Justiça de Minas Gerais).
"""

__version__ = "1.0.0"
__author__ = "PJe Automation Team"
__email__ = "contact@example.com"

from .exceptions import LoginError, PJeAutomationError, ProcessNotFoundError
from .pje_client import PJeClient

__all__ = ["PJeClient", "PJeAutomationError", "LoginError", "ProcessNotFoundError"]
