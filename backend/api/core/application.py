from fastapi import FastAPI
from .state import GlobalState
from .config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Inicializa o estado global
app.state.api_v1_str = settings.API_V1_STR
app.state.global_state = GlobalState()

def get_state() -> GlobalState:
    """Retorna o estado global da aplicação"""
    return app.state.global_state