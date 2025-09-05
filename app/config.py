import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)


def canonicalize_base_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    url = url.rstrip("/")
    for suffix in ("/browse", "/rest/api/3", "/rest/api/latest", "/rest"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
    return url


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
    cache_ttl_seconds: int = Field(3600, alias="CACHE_TTL_SECONDS")
    threads: int = Field(4, alias="THREADS")
    faiss_enabled: bool = Field(False, alias="FAISS_ENABLED")

    default_bitbucket_repos: List[str] = Field(
        default_factory=list, alias="DEFAULT_BITBUCKET_REPOS"
    )
    default_branches: List[str] = Field(default_factory=list, alias="DEFAULT_BRANCHES")

    bitbucket: BitbucketSettings = BitbucketSettings()
    jira: JiraDefaults = JiraDefaults()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
        frozen=True,
    )

    @field_validator("jira_base_url", mode="before")
    @classmethod
    def _canon_jira(cls, v: str) -> str:
        canon = canonicalize_base_url(v or "")
        if v and v.rstrip("/") != canon:
            logger.warning("Canonicalizing JIRA_BASE_URL to %s", canon)
        return canon

    @field_validator("bitbucket_base_url", mode="before")
    @classmethod
    def _canon_bb(cls, v: str) -> str:
        return canonicalize_base_url(v or "")

    @field_validator("default_bitbucket_repos", "default_branches", mode="before")
    @classmethod
    def _split_csv(cls, v):
        if isinstance(v, str):
            return [p.strip() for p in v.split(",") if p.strip()]
        return v


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
    s = Settings(**yaml_defaults)
    if not s.default_bitbucket_repos:
        object.__setattr__(
            s,
            "default_bitbucket_repos",
            [f"{s.bitbucket.project_key}/{r}" for r in s.bitbucket.repos],
        )
    if not s.default_branches:
        object.__setattr__(s, "default_branches", s.bitbucket.branch_defaults)

    logger.info("Jira base URL: %s", s.jira_base_url)
    logger.info("Bitbucket base URL: %s", s.bitbucket_base_url)
    logger.info("Default repos: %s", s.default_bitbucket_repos)
    logger.info("Default branches: %s", s.default_branches)
    return s


settings = load_settings()


class ConfigError(Exception):
    pass


def validate_settings(s: Settings) -> List[str]:
    errors: List[str] = []
    if not s.jira_base_url:
        errors.append("JIRA_BASE_URL is missing")
    if not (s.jira_token_file or (s.jira_email and s.jira_api_token)):
        errors.append("Provide JIRA_TOKEN_FILE or JIRA_EMAIL+JIRA_API_TOKEN")
    if not s.bitbucket_base_url:
        errors.append("BITBUCKET_BASE_URL is missing")
    if not s.bitbucket_token:
        errors.append("BITBUCKET_TOKEN is missing")
    if not s.openai_api_key:
        errors.append("OPENAI_API_KEY is missing")
    if not s.default_bitbucket_repos:
        errors.append("DEFAULT_BITBUCKET_REPOS is missing")
    else:
        for r in s.default_bitbucket_repos:
            if "/" not in r:
                errors.append(f"Repo '{r}' must be project/repo")
                break
    if not s.default_branches:
        errors.append("DEFAULT_BRANCHES is missing")
    return errors
