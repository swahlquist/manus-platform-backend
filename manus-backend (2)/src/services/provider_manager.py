"""
Provider Manager for handling multiple AI providers.
"""

import logging
import random
import time
from typing import Dict, List, Any, Optional, Tuple

from config.settings import Settings, ProviderConfig

logger = logging.getLogger("manus-backend.provider_manager")

class ProviderError(Exception):
    """Exception raised for provider-related errors."""
    pass

class Provider:
    """Base class for AI providers."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.name = config.name
        self.api_key = config.api_key
        self.base_url = config.base_url
        self.models = config.models
        self.priority = config.priority
        self.enabled = config.enabled
        self.rate_limit = config.rate_limit
        self.last_request_time = 0
        self.request_count = 0
        self.error_count = 0
        self.client = None
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the provider client."""
        raise NotImplementedError("Subclasses must implement _initialize_client")
    
    def _check_rate_limit(self) -> bool:
        """
        Check if the provider is rate limited.
        
        Returns:
            bool: True if rate limited, False otherwise.
        """
        if not self.rate_limit:
            return False
        
        current_time = time.time()
        time_window = 60  # 1 minute in seconds
        
        # Reset counter if outside time window
        if current_time - self.last_request_time > time_window:
            self.request_count = 0
            self.last_request_time = current_time
            return False
        
        # Check if rate limit reached
        if self.request_count >= self.rate_limit:
            return True
        
        return False
    
    def _update_request_stats(self):
        """Update request statistics."""
        self.request_count += 1
        self.last_request_time = time.time()
    
    async def generate_completion(self, prompt: str, model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate a completion for the given prompt.
        
        Args:
            prompt: The prompt to generate a completion for.
            model: The model to use for generation. If None, uses the first model in the config.
            **kwargs: Additional parameters to pass to the provider.
            
        Returns:
            Dict containing the completion response.
            
        Raises:
            ProviderError: If the provider is rate limited or an error occurs.
        """
        if not self.enabled:
            raise ProviderError(f"Provider {self.name} is disabled")
        
        if self._check_rate_limit():
            raise ProviderError(f"Provider {self.name} is rate limited")
        
        # Use first model if not specified
        if not model and self.models:
            model = self.models[0]
        
        try:
            self._update_request_stats()
            return await self._generate_completion_impl(prompt, model, **kwargs)
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error generating completion with provider {self.name}: {e}")
            raise ProviderError(f"Provider {self.name} error: {str(e)}")
    
    async def _generate_completion_impl(self, prompt: str, model: Optional[str], **kwargs) -> Dict[str, Any]:
        """Implementation of completion generation."""
        raise NotImplementedError("Subclasses must implement _generate_completion_impl")

class ProviderManager:
    """Manager for multiple AI providers."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.providers: Dict[str, Provider] = {}
        self.default_provider = settings.default_provider
        self.fallback_strategy = settings.fallback_strategy
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured providers."""
        from providers.openai_provider import OpenAIProvider
        from providers.anthropic_provider import AnthropicProvider
        
        provider_classes = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            # Add more providers as needed
        }
        
        for provider_config in self.settings.providers:
            provider_class = provider_classes.get(provider_config.name)
            if not provider_class:
                logger.warning(f"Unknown provider: {provider_config.name}")
                continue
            
            try:
                provider = provider_class(provider_config)
                self.providers[provider_config.name] = provider
                logger.info(f"Initialized provider: {provider_config.name}")
            except Exception as e:
                logger.error(f"Failed to initialize provider {provider_config.name}: {e}")
    
    def get_provider(self, name: str) -> Optional[Provider]:
        """
        Get a provider by name.
        
        Args:
            name: The name of the provider.
            
        Returns:
            The provider instance or None if not found.
        """
        return self.providers.get(name)
    
    def get_all_providers(self) -> List[Provider]:
        """
        Get all enabled providers.
        
        Returns:
            List of enabled provider instances.
        """
        return [p for p in self.providers.values() if p.enabled]
    
    def _get_providers_by_priority(self) -> List[Provider]:
        """
        Get providers sorted by priority.
        
        Returns:
            List of providers sorted by priority (lowest first).
        """
        return sorted(self.get_all_providers(), key=lambda p: p.priority)
    
    def _get_next_provider(self, exclude: List[str] = None) -> Optional[Provider]:
        """
        Get the next provider based on fallback strategy.
        
        Args:
            exclude: List of provider names to exclude.
            
        Returns:
            The next provider to use or None if no providers available.
        """
        exclude = exclude or []
        available_providers = [p for p in self.get_all_providers() if p.name not in exclude]
        
        if not available_providers:
            return None
        
        if self.fallback_strategy == "priority":
            return sorted(available_providers, key=lambda p: p.priority)[0]
        elif self.fallback_strategy == "round-robin":
            # Simple round-robin implementation
            return available_providers[0]  # In a real implementation, we'd track the last used provider
        elif self.fallback_strategy == "random":
            return random.choice(available_providers)
        else:
            # Default to priority
            return sorted(available_providers, key=lambda p: p.priority)[0]
    
    async def generate_completion(self, prompt: str, provider_name: Optional[str] = None, 
                                 model: Optional[str] = None, max_retries: int = 3, **kwargs) -> Dict[str, Any]:
        """
        Generate a completion using the specified provider or fallback strategy.
        
        Args:
            prompt: The prompt to generate a completion for.
            provider_name: The name of the provider to use. If None, uses the default provider.
            model: The model to use for generation.
            max_retries: Maximum number of retries with different providers.
            **kwargs: Additional parameters to pass to the provider.
            
        Returns:
            Dict containing the completion response.
            
        Raises:
            ProviderError: If all providers fail.
        """
        tried_providers = []
        last_error = None
        
        # Use default provider if not specified
        if not provider_name:
            provider_name = self.default_provider
        
        # Try the specified provider first
        if provider_name and provider_name in self.providers:
            provider = self.providers[provider_name]
            if provider.enabled:
                try:
                    return await provider.generate_completion(prompt, model, **kwargs)
                except ProviderError as e:
                    last_error = e
                    tried_providers.append(provider_name)
                    logger.warning(f"Provider {provider_name} failed: {e}")
        
        # Fallback to other providers
        retries = 0
        while retries < max_retries:
            next_provider = self._get_next_provider(exclude=tried_providers)
            if not next_provider:
                break
            
            try:
                logger.info(f"Trying fallback provider: {next_provider.name}")
                return await next_provider.generate_completion(prompt, model, **kwargs)
            except ProviderError as e:
                last_error = e
                tried_providers.append(next_provider.name)
                logger.warning(f"Fallback provider {next_provider.name} failed: {e}")
            
            retries += 1
        
        # All providers failed
        error_msg = f"All providers failed after {len(tried_providers)} attempts"
        if last_error:
            error_msg += f": {str(last_error)}"
        
        logger.error(error_msg)
        raise ProviderError(error_msg)
    
    def get_provider_status(self) -> List[Dict[str, Any]]:
        """
        Get status information for all providers.
        
        Returns:
            List of provider status dictionaries.
        """
        return [
            {
                "name": provider.name,
                "enabled": provider.enabled,
                "priority": provider.priority,
                "models": provider.models,
                "error_count": provider.error_count,
                "request_count": provider.request_count
            }
            for provider in self.providers.values()
        ]
