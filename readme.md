# EEG Attention Monitoring System

Sistema de monitoramento de atenção em tempo real usando EEG com dashboard interativo.

## Estrutura do Projeto

```
projeto/
├── backend/            # API FastAPI e processamento EEG
│   ├── api/
│   ├── src/
│   └── tests/
└── frontend/          # Interface React com TypeScript
    └── src/
```

## Requisitos do Sistema

### Backend
- Python 3.8+
- pip

### Frontend
- Node.js 16+
- npm ou yarn

## Instalação

### 1. Backend (Python/FastAPI)

1. Crie e ative um ambiente virtual:
```bash
# Windows
python -m venv bci
bci\Scripts\activate

# Linux/Mac
python3 -m venv bci
source bci/bin/activate
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Crie o arquivo .env com suas variáveis de ambiente:
```env
API_ENV=development
API_HOST=localhost
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000"]
```

### 2. Frontend (React/TypeScript)

1. Instale as dependências:
```bash
cd frontend
npm install
```

2.  Crie o arquivo .env.local com suas variáveis de ambiente::
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1/ws/stream
```

## Executando o Projeto

### 1. Backend

1. Inicie o servidor de desenvolvimento:
```bash
# No diretório backend/
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

2. Verificação:
- API estará disponível em: http://localhost:8000
- Documentação: http://localhost:8000/docs

### 2. Frontend

1. Inicie o servidor de desenvolvimento:
```bash
# No diretório frontend/
npm run dev
```

2. Acesse:
- Interface: http://localhost:3000

## Testes

### Backend
```bash
# No diretório backend/
pytest tests/
```

### Frontend
```bash
# No diretório frontend/
npm test
```

## Estrutura de Arquivos Detalhada

### Backend
```
backend/
├── api/
│   ├── core/
│   │   ├── config.py         # Configurações da API
│   │   └── state.py         # Estado global
│   ├── models/
│   │   └── schemas.py       # Schemas Pydantic
│   └── routes/
│       ├── eeg.py           # Rotas EEG
│       └── websocket.py     # Rotas WebSocket
├── src/
│   ├── attention_bci.py     # Processamento principal
│   ├── data_loader.py       # Carregamento de dados
│   ├── feature_extractor.py # Extração características
│   └── signal_processor.py  # Processamento sinais
└── tests/
    ├── test_api.py
    ├── test_processing.py
    ├── conftest.py
    └── test_websocket.py

```

### Frontend
```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   ├── charts/
│   │   ├── cards/
│   │   └── monitoring/
│   ├── contexts/
│   │   ├── WebSocketContext.tsx
│   │   └── MonitoringContext.tsx
│   ├── hooks/
│   │   ├── useWebSocket.ts
│   │   └── useEEGData.ts
│   ├── utils/
│   └── pages/
└── public/
```

## Uso da API

### WebSocket Endpoints

1. Conexão:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/stream');
```

2. Formato das mensagens:
```typescript
interface WebSocketMessage {
  type: 'initial_state' | 'processed_data' | 'error';
  data?: EEGData;
  timestamp: number;
}
```

### REST Endpoints

#### Processamento EEG
```bash
POST /api/v1/eeg/process
GET /api/v1/eeg/analysis
```

#### Sessões
```bash
POST /api/v1/session/start
POST /api/v1/session/stop
POST /api/v1/session/save
GET /api/v1/session/load
```

## Solução de Problemas

### Backend

1. Erro de conexão com WebSocket:
   - Verifique se o servidor está rodando
   - Confirme as configurações CORS
   - Verifique a URL do WebSocket

2. Erros de processamento:
   - Verifique o formato dos dados EEG
   - Confirme a frequência de amostragem
   - Verifique logs do servidor

### Frontend

1. Erro de build:
```bash
# Limpe cache e reinstale dependências
npm clean-install
```

2. Problemas de conexão:
   - Verifique variáveis de ambiente
   - Confirme URLs da API/WebSocket
   - Verifique Console do navegador

## Guia de Testes

Este guia fornece informações sobre como testar a API backend e os componentes de processamento.

### Configurando o Ambiente de Testes

1. Certifique-se de ter todas as dependências instaladas:
```bash
pip install -r requirements.txt
```

2. Para desenvolvimento, instale as dependências de desenvolvimento:
```bash
pip install -e ".[dev]"
```

3. Ative seu ambiente virtual:
```bash
source bci/bin/activate  # Linux/Mac
# ou
.\bci\Scripts\activate  # Windows
```

### Executando os Testes

#### Executando Todos os Testes
Para rodar todos os testes com relatório de cobertura:
```bash
pytest
```

#### Executando Arquivos de Teste Específicos
```bash
# Testa endpoints da API
pytest tests/test_api.py

# Testa processamento de sinais
pytest tests/test_processing.py

# Testa funcionalidade WebSocket
pytest tests/test_websocket.py
```

#### Opções de Teste
- Executar testes com saída detalhada:
```bash
pytest -v
```

- Executar testes mostrando prints:
```bash
pytest -s
```

- Gerar relatório de cobertura:
```bash
pytest --cov=src --cov=api --cov-report=term-missing
```

### Estrutura dos Testes

A suite de testes está organizada da seguinte forma:

- `tests/conftest.py`: Fixtures e configurações comuns
- `tests/test_api.py`: Testes dos endpoints da API
- `tests/test_processing.py`: Testes de processamento de sinais
- `tests/test_websocket.py`: Testes de comunicação WebSocket

### Teste Manual

Para testar manualmente a conexão WebSocket:

1. Inicie o servidor:
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

2. Execute o script de teste WebSocket:
```bash
python tests/test_websocket.py
```

### Testes Contínuos Durante o Desenvolvimento

Para testes contínuos durante o desenvolvimento:

1. Instale o pytest-watch (incluído nas dependências de dev):
```bash
pip install pytest-watch
```

2. Execute os testes automaticamente quando arquivos forem alterados:
```bash
ptw
```

### Cobertura de Testes

Para obter um relatório detalhado de cobertura:

```bash
pytest --cov=src --cov=api --cov-report=html
```

Isso irá gerar um relatório HTML no diretório `htmlcov`.

### Dicas para Testes WebSocket

Ao testar a funcionalidade WebSocket:

1. Use o script de teste fornecido:
```bash
python tests/test_websocket.py
```

2. Monitore os logs do servidor para problemas de conexão
3. Verifique se o formato da resposta WebSocket corresponde ao schema esperado
4. Verifique se o processamento de dados funciona com dados EEG simulados

### Solução de Problemas

Se encontrar problemas:

1. Certifique-se de que todas as dependências estão instaladas:
```bash
pip install -r requirements.txt
```

2. Verifique se o servidor está rodando (para testes de API/WebSocket)
3. Verifique se o banco de dados de teste está configurado corretamente
4. Procure mensagens de erro detalhadas na saída do teste
5. Use as flags -v e -s do pytest para mais informações

### Estrutura do Projeto de Testes

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Configurações e fixtures compartilhadas
│   ├── test_api.py          # Testes da API
│   ├── test_processing.py   # Testes de processamento
│   └── test_websocket.py    # Testes WebSocket
├── pyproject.toml           # Configurações do pytest
└── requirements.txt         # Dependências do projeto
```

### Executando Testes com Tags

Você pode usar tags para executar grupos específicos de testes:

```bash
# Executar apenas testes da API
pytest -v -m "api"

# Executar apenas testes de processamento
pytest -v -m "processing"

# Executar testes não marcados como lentos
pytest -v -m "not slow"
```

### Geração de Dados de Teste

O módulo de testes inclui geradores de dados EEG simulados para testes. Para usar:

```python
from tests.conftest import sample_eeg_data

# Gera dados EEG simulados
data = sample_eeg_data()
```

### Ambiente de Desenvolvimento

Para uma melhor experiência de desenvolvimento, recomenda-se:

1. Usar um editor com suporte a pytest (VSCode, PyCharm)
2. Configurar o autopep8 ou black para formatação automática
3. Habilitar linting com flake8
4. Usar mypy para verificação de tipos

### Executando Testes de Performance

Para testes de performance:

```bash
# Mede tempo de execução dos testes
pytest --durations=0

# Executa testes de performance específicos
pytest -v -m "performance"
```

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.