# tests/conftest.py
# -*- coding: utf-8 -*-
"""
Configuração do pytest para o projeto de análise de carbono.

Este arquivo configura o ambiente de teste e define fixtures
compartilhadas entre todos os testes.
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz do projeto ao Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Configurar logging para testes
import logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Suprimir warnings específicos durante os testes
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="statsmodels")
warnings.filterwarnings("ignore", category=UserWarning)