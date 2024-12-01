#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Iniciando ambiente de desenvolvimento...${NC}"

# Ativa ambiente virtual se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Instala dependências
echo -e "${GREEN}Instalando dependências...${NC}"
pip install -r requirements.txt

# Configura variáveis de ambiente
export PYTHONPATH=$PYTHONPATH:$(pwd)
export API_ENV=development

# Inicia servidor
echo -e "${GREEN}Iniciando servidor FastAPI...${NC}"
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000