#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Iniciando testes...${NC}"

# Ativa ambiente virtual se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Instala dependências de teste
echo -e "${GREEN}Instalando dependências de teste...${NC}"
pip install -r requirements.txt

# Executa linting
echo -e "${GREEN}Executando linting...${NC}"
flake8 src api tests

# Executa testes
echo -e "${GREEN}Executando testes...${NC}"
python -m pytest tests/ -v --cov=src --cov=api --cov-report=term-missing