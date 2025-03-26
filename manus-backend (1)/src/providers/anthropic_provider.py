"""
Anthropic provider implementation.
"""

import logging
import json
import uuid
from typing import Dict, Any, Optional

import anthropic
from anthropic import Anthropic

from services.provider_manager import Provider, ProviderConfig, ProviderError

logger = logging.getLogger("manus-backend.providers.anthropic")

class AnthropicProvider(Provider):
    """Provider implementation for Anthropic."""
    
    def _initialize_client(self):
        """Initialize the Anthropic client."""
        try:
            self.client = Anthropic(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.config.timeout
            )
            logger.info(f"Initialized Anthropic client with base URL: {self.base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise ProviderError(f"Failed to initialize Anthropic client: {str(e)}")
    
    async def _generate_completion_impl(self, prompt: str, model: Optional[str], **kwargs) -> Dict[str, Any]:
        """
        Implementation of completion generation for Anthropic.
        
        Args:
            prompt: The prompt to generate a completion for.
            model: The model to use for generation.
            **kwargs: Additional parameters to pass to the provider.
            
        Returns:
            Dict containing the completion response.
        """
        try:
            # Use default model if not specified
            if not model:
                model = self.models[0] if self.models else "claude-3-opus-20240229"
            
            # Prepare parameters
            params = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.0),
                "max_tokens": kwargs.get("max_tokens", 4096)
            }
            
            # Add additional parameters
            for key, value in kwargs.items():
                if key not in params and key not in ["temperature", "max_tokens"]:
                    params[key] = value
            
            # Generate completion
            response = self.client.messages.create(**params)
            
            # Extract and return response
            result = {
                "text": response.content[0].text,
                "provider": self.name,
                "model": model,
                "tokens": response.usage.output_tokens + response.usage.input_tokens,
                "request_id": str(uuid.uuid4())
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error generating completion with Anthropic: {e}")
            raise ProviderError(f"Anthropic error: {str(e)}")
