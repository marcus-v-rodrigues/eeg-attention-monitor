"""
Testes do sistema BCI e API
"""

# Configuração de logging para testes
import logging
logging.getLogger('test').setLevel(logging.INFO)

from .test_processing import *
from .test_api import *
from .test_websocket import *