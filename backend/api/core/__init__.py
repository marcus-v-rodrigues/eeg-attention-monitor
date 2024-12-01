"""
Core da API
Configurações e estado global
"""

from .config import settings
from .state import GlobalState

__all__ = ['settings', 'GlobalState']