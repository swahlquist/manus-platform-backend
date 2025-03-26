"""
Configuration settings for the Manus Backend.
"""

import os
import yaml
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("manus-backend.config")

class ProviderConfig(BaseModel):
    """Configuration for an AI provider."""
    name: str
    api_key: str
    base_url: Optional[str] = None
    models: List[str] = Field(default_factory=list)
    priority: int = 1  # Lower number means higher priority
    timeout: int = 30  # Timeout in seconds
    max_retries: int = 3
    enabled: bool = True
    rate_limit: Optional[int] = None  # Requests per minute, None means no limit

class Settings(BaseModel):
    """Main configuration settings."""
    providers: List[ProviderConfig] = Field(default_factory=list)
    default_provider: str = "openai"
    fallback_strategy: str = "priority"  # Options: priority, round-robin, random
    request_timeout: int = 60
    max_tokens: int = 4096
    temperature: float = 0.0
    debug: bool = False
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])

def load_settings(config_path: Optional[str] = None) -> Settings:
    """
    Load settings from configuration file.
    
    Args:
        config_path: Path to configuration file. If None, uses environment variable or default path.
        
    Returns:
        Settings object with configuration values.
    """
    if not config_path:
        config_path = os.environ.get("MANUS_CONFIG_PATH", "config/config.yaml")
    
    try:
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        
        # Create provider configs
        providers = []
        for provider_data in config_data.get("providers", []):
            providers.append(ProviderConfig(**provider_data))
        
        # Create settings with providers
        settings_data = config_data.get("settings", {})
        settings_data["providers"] = providers
        
        settings = Settings(**settings_data)
        logger.info(f"Loaded configuration from {config_path}")
        return settings
    
    except Exception as e:
        logger.error(f"Failed to load configuration from {config_path}: {e}")
        logger.info("Using default configuration")
        
        # Create default configuration with OpenAI and Anthropic
        openai_provider = ProviderConfig(
            name="openai",
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url="https://api.openai.com/v1",
            models=["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            priority=1
        )
        
        anthropic_provider = ProviderConfig(
            name="anthropic",
            api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            base_url="https://api.anthropic.com",
            models=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            priority=2
        )
        
        return Settings(
            providers=[openai_provider, anthropic_provider],
            default_provider="openai",
            fallback_strategy="priority"
        )
