from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the application."""

    UV_LINK_MODE: str = Field(default="copy")

    MIRO_CLIENT_ID: str = Field(default="")
    MIRO_CLIENT_SECRET: str = Field(default="")
    MIRO_REDIRECT_URI: str = Field(default="http://localhost:8000/miro/callback")

    ## OPTIONAL:
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILEPATH: str = Field(default="./log/app.log")
    FASTAPI_HOST: str = Field(default="127.0.0.1")
    FASTAPI_PORT: int = Field(default=8000)
    OLLAMA_API_URL: str = Field(default="")
    AZURE_OPENAI_API_KEY: str = Field(default="")
    AZURE_OPENAI_ENDPOINT: str = Field(default="")
    AZURE_OPENAI_DEPLOYMENT: str = Field(default="")
    GOOGLE_API_KEY: str = Field(default="")
    FRONTEND_URL: str = Field(default="http://localhost:3000")
    BACKEND_URL: str = Field(default="http://localhost:8000")

    class Config:
        """Configuration for the settings."""

        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    """Get the settings for the application."""
    return Settings()


if __name__ == "__main__":
    import json

    from package.util.logger import get_logger

    settings = get_settings()
    logger = get_logger()
    logger.debug(json.dumps(settings.model_dump(), indent=2))
