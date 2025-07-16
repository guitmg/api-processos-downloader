"""
Custom exceptions for PJe Automation package.
"""


class PJeAutomationError(Exception):
    """Base exception for PJe automation errors."""

    pass


class LoginError(PJeAutomationError):
    """Exception raised when login fails."""

    pass


class ProcessNotFoundError(PJeAutomationError):
    """Exception raised when a process is not found."""

    pass


class DownloadError(PJeAutomationError):
    """Exception raised when document download fails."""

    pass


class NavigationError(PJeAutomationError):
    """Exception raised when page navigation fails."""

    pass


class ElementNotFoundError(PJeAutomationError):
    """Exception raised when a required element is not found."""

    pass
