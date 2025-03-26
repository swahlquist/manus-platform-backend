"""
Integration tests for multiple AI providers.
"""

import asyncio
import logging
from typing import Dict, Any, List

from services.provider_manager import ProviderManager
from config.settings import load_settings, Settings, ProviderConfig

logger = logging.getLogger("manus-backend.integration")

class ProviderIntegration:
    """Integration utilities for multiple AI providers."""
    
    def __init__(self, settings: Settings = None):
        """
        Initialize provider integration.
        
        Args:
            settings: Settings object. If None, loads from default config.
        """
        self.settings = settings or load_settings()
        self.provider_manager = ProviderManager(self.settings)
    
    async def test_provider(self, provider_name: str) -> Dict[str, Any]:
        """
        Test a specific provider.
        
        Args:
            provider_name: Name of the provider to test.
            
        Returns:
            Test result dictionary.
        """
        provider = self.provider_manager.get_provider(provider_name)
        if not provider:
            return {
                "provider": provider_name,
                "status": "error",
                "message": f"Provider {provider_name} not found"
            }
        
        if not provider.enabled:
            return {
                "provider": provider_name,
                "status": "disabled",
                "message": f"Provider {provider_name} is disabled"
            }
        
        try:
            # Simple test prompt
            prompt = "Respond with 'Hello, World!' and nothing else."
            
            # Test completion
            result = await provider.generate_completion(prompt)
            
            return {
                "provider": provider_name,
                "status": "success",
                "model": result.get("model", "unknown"),
                "response": result.get("text", ""),
                "tokens": result.get("tokens", 0)
            }
        except Exception as e:
            logger.error(f"Error testing provider {provider_name}: {e}")
            return {
                "provider": provider_name,
                "status": "error",
                "message": str(e)
            }
    
    async def test_all_providers(self) -> List[Dict[str, Any]]:
        """
        Test all enabled providers.
        
        Returns:
            List of test result dictionaries.
        """
        results = []
        for provider in self.provider_manager.get_all_providers():
            result = await self.test_provider(provider.name)
            results.append(result)
        
        return results
    
    async def test_fallback_strategy(self) -> Dict[str, Any]:
        """
        Test the fallback strategy.
        
        Returns:
            Test result dictionary.
        """
        try:
            # Simple test prompt
            prompt = "Respond with 'Testing fallback strategy' and nothing else."
            
            # Force fallback by using a non-existent provider
            result = await self.provider_manager.generate_completion(
                prompt=prompt,
                provider_name="non_existent_provider"
            )
            
            return {
                "status": "success",
                "provider_used": result.get("provider", "unknown"),
                "model": result.get("model", "unknown"),
                "response": result.get("text", ""),
                "tokens": result.get("tokens", 0)
            }
        except Exception as e:
            logger.error(f"Error testing fallback strategy: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def simulate_rate_limit(self, provider_name: str) -> Dict[str, Any]:
        """
        Simulate rate limiting for a provider.
        
        Args:
            provider_name: Name of the provider to simulate rate limiting for.
            
        Returns:
            Test result dictionary.
        """
        provider = self.provider_manager.get_provider(provider_name)
        if not provider:
            return {
                "provider": provider_name,
                "status": "error",
                "message": f"Provider {provider_name} not found"
            }
        
        # Temporarily set a very low rate limit
        original_rate_limit = provider.rate_limit
        provider.rate_limit = 1
        
        try:
            # Simple test prompt
            prompt = "Respond with a short greeting."
            
            # First request should succeed
            first_result = await provider.generate_completion(prompt)
            
            # Second request should trigger rate limit and fallback
            second_result = await self.provider_manager.generate_completion(
                prompt=prompt,
                provider_name=provider_name
            )
            
            return {
                "status": "success",
                "first_request": {
                    "provider": first_result.get("provider", "unknown"),
                    "status": "success"
                },
                "second_request": {
                    "provider": second_result.get("provider", "unknown"),
                    "status": "success" if second_result.get("provider") != provider_name else "error"
                },
                "fallback_worked": second_result.get("provider") != provider_name
            }
        except Exception as e:
            logger.error(f"Error simulating rate limit for provider {provider_name}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
        finally:
            # Restore original rate limit
            provider.rate_limit = original_rate_limit
