"""Google Forms integration proof of concept."""

__version__ = "0.1.0"
__author__ = "Al3x"
__email__ = "al3x@mail.com"

from .auth import AuthenticationError, GoogleAuthenticator
from .config import Config, config
from .core import GFormsClient

__all__ = [
    "GFormsClient",
    "GoogleAuthenticator",
    "AuthenticationError",
    "Config",
    "config",
]
