from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BitbucketSettings(BaseModel):
    project_key: str = "STARSYSONE"
    repos: List[str] = [
        "policycenter",
        "claimcenter",
        "billingcenter",
        "contactmanager",
    ]
    branch_defaults: List[str] = ["develop"]
    branch_pattern: str = "release/r-*"


class JiraDefaults(BaseModel):
    jql_default: str = ""


class Settings(BaseSettings):
    """Application configuration with optional ``config.yaml`` defaults.

    Environment variables take precedence over values defined in the YAML file
    or ``.env``. Unknown keys from the YAML are ignored so that extending the
    configuration does not break settings parsing."""

    jira_base_url: str = Field("", alias="JIRA_BASE_URL")
    jira_email: str = Field("", alias="JIRA_EMAIL")
    jira_api_token: str = Field("", alias="JIRA_API_TOKEN")
    jira_token_file: Optional[str] = Field(None, alias="JIRA_TOKEN_FILE")

    bitbucket_base_url: str = Field("", alias="BITBUCKET_BASE_URL")
    bitbucket_token: str = Field("", alias="BITBUCKET_TOKEN")

    rapid_token_url: str = Field("", alias="RAPID_TOKEN_URL")
    rapid_client_id: str = Field("", alias="RAPID_CLIENT_ID")
    rapid_client_secret: str = Field("", alias="RAPID_CLIENT_SECRET")

    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", alias="OPENAI_MODEL")

    pem_path: str = Field("/app/certs/corp.pem", alias="PEM_PATH")

    cache_ttl_seconds: int = Field(3600, alias="CACHE_TTL_SECONDS")
    threads: int = Field(4, alias="THREADS")
    faiss_enabled: bool = Field(False, alias="FAISS_ENABLED")

    bitbucket: BitbucketSettings = BitbucketSettings()
    jira: JiraDefaults = JiraDefaults()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
        frozen=True,
    )


def _load_yaml_defaults() -> Dict[str, Any]:
    cfg_path = Path("config.yaml")
    if cfg_path.exists():
        with cfg_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return data
    return {}


def load_settings() -> Settings:
    """Load application settings with precedence: env vars > .env > YAML."""
    load_dotenv(override=False)
    yaml_defaults = _load_yaml_defaults()
    return Settings(**yaml_defaults)


settings = load_settings()
