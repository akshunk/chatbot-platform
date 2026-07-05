from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import conversations, messages, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    from core.llm.router import LLMRouter
    from core.prompts import PromptBuilder
    from core.chat import ConversationHistory, ContextBuilder, ResponseGenerator

    providers_config = {}
    providers_path = Path(settings.config_dir) / "providers.yaml"
    if providers_path.exists():
        import yaml
        with open(providers_path) as f:
            providers_config = yaml.safe_load(f) or {}

    models_config = {}
    models_path = Path(settings.config_dir) / "models.yaml"
    if models_path.exists():
        import yaml
        with open(models_path) as f:
            models_config = yaml.safe_load(f) or {}

    llm_router = LLMRouter(providers_config)
    prompt_builder = PromptBuilder(
        prompts_dir=Path(settings.core_dir) / "prompts",
        personality_dir=Path(settings.core_dir) / "personality",
    )
    history = ConversationHistory(data_dir=settings.data_dir)
    context_builder = ContextBuilder(prompt_builder)
    response_generator = ResponseGenerator(
        llm_router=llm_router,
        context_builder=context_builder,
        provider_name=settings.default_provider,
    )

    app.state.llm_router = llm_router
    app.state.prompt_builder = prompt_builder
    app.state.history = history
    app.state.context_builder = context_builder
    app.state.response_generator = response_generator
    app.state.providers_config = providers_config
    app.state.models_config = models_config
    app.state.default_provider = settings.default_provider
    app.state.default_model = settings.default_model
    yield


app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(conversations.router, prefix="/api", tags=["conversations"])
app.include_router(messages.router, prefix="/api", tags=["messages"])
