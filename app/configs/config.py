"""
Configuration management for the agent, using Pydantic models and YAML loading.
"""

import os
from functools import lru_cache

import yaml
from pydantic import BaseModel, Field, SecretStr, StrictFloat, StrictInt, StrictStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    host: StrictStr
    name: StrictStr
    description: StrictStr
    version: StrictStr
    port: StrictInt
    log_level: StrictStr


class LLMConfig(BaseModel):
    stock_analyzer_prompt_path: StrictStr
    temperature: StrictFloat
    max_tokens: StrictInt
    retry: StrictInt


class ShioajiConfig(BaseSettings):
    api_key: str = Field(alias="SHIOAJI_API_KEY")
    api_secret: str = Field(alias="SHIOAJI_API_SECRET")
    
    model_config = SettingsConfigDict(env_prefix="")


class GeminiConfig(BaseSettings):
    endpoint: StrictStr = Field(alias="GEMINI_ENDPOINT")
    api_key: SecretStr = Field(alias="GEMINI_API_KEY")
    model: StrictStr = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")
    
    model_config = SettingsConfigDict(env_prefix="")


class Config(BaseSettings):
    app: AppConfig
    llm: LLMConfig
    shioaji: ShioajiConfig
    gemini: GeminiConfig


@lru_cache()
def get_config() -> Config:
    config_path = os.getenv("CONFIG_PATH", "app/configs/config.yaml")

    with open(config_path, "r") as f:
        yaml_config = yaml.safe_load(f)

    # Create sub-configs that automatically read from environment
    shioaji_config = ShioajiConfig()
    gemini_config = GeminiConfig()
    
    return Config(
        app=AppConfig(**yaml_config["app"]),
        llm=LLMConfig(**yaml_config["llm"]),
        shioaji=shioaji_config,
        gemini=gemini_config
    )
