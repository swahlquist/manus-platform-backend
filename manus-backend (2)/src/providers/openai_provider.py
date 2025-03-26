"""
OpenAI provider implementation.
"""

import logging
import json
import uuid
from typing import Dict, Any, Optional

import openai
from openai import OpenAI

from services.provider_manager import Provider, ProviderConfig, ProviderError

logger = logging.getLogger("manus-backend.providers.openai")

class OpenAIProvider(Provider):
    """Provider implementation for OpenAI."""
    
    def _initialize_client(self):
        """Initialize the OpenAI client."""
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.config.timeout
            )
            logger.info(f"Initialized OpenAI client with base URL: {self.base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ProviderError(f"Failed to initialize OpenAI client: {str(e)}")
    
    async def _generate_completion_impl(self, prompt: str, model: Optional[str], **kwargs) -> Dict[str, Any]:
        """
        Implementation of completion generation for OpenAI.
        
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
                model = self.models[0] if self.models else "gpt-4o"
            
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
            response = self.client.chat.completions.create(**params)
            
            # Extract and return response
            result = {
                "text": response.choices[0].message.content,
                "provider": self.name,
                "model": model,
                "tokens": response.usage.total_tokens,
                "request_id": str(uuid.uuid4())
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error generating completion with OpenAI: {e}")
            raise ProviderError(f"OpenAI error: {str(e)}")
