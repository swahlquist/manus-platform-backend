"""
Unit tests for the provider manager.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch

from services.provider_manager import ProviderManager, Provider, ProviderError
from config.settings import Settings, ProviderConfig

# Mock provider implementation
class MockProvider(Provider):
    def _initialize_client(self):
        self.client = MagicMock()
    
    async def _generate_completion_impl(self, prompt, model, **kwargs):
        if self.name == "failing_provider":
            raise Exception("Simulated provider failure")
        
        return {
            "text": f"Response from {self.name}",
            "provider": self.name,
            "model": model or "mock-model",
            "tokens": 10,
            "request_id": "mock-request-id"
        }

@pytest.fixture
def mock_settings():
    """Create mock settings with multiple providers."""
    return Settings(
        providers=[
            ProviderConfig(
                name="provider1",
                api_key="mock-key-1",
                models=["model1"],
                priority=1,
                enabled=True
            ),
            ProviderConfig(
                name="provider2",
                api_key="mock-key-2",
                models=["model2"],
                priority=2,
                enabled=True
            ),
            ProviderConfig(
                name="failing_provider",
                api_key="mock-key-3",
                models=["model3"],
                priority=3,
                enabled=True
            ),
            ProviderConfig(
                name="disabled_provider",
                api_key="mock-key-4",
                models=["model4"],
                priority=4,
                enabled=False
            )
        ],
        default_provider="provider1",
        fallback_strategy="priority"
    )

@pytest.fixture
def provider_manager(mock_settings):
    """Create a provider manager with mock providers."""
    manager = ProviderManager(mock_settings)
    
    # Replace the providers with mock providers
    manager.providers = {
        "provider1": MockProvider(mock_settings.providers[0]),
        "provider2": MockProvider(mock_settings.providers[1]),
        "failing_provider": MockProvider(mock_settings.providers[2]),
        "disabled_provider": MockProvider(mock_settings.providers[3])
    }
    
    return manager

@pytest.mark.asyncio
async def test_get_provider(provider_manager):
    """Test getting a provider by name."""
    provider = provider_manager.get_provider("provider1")
    assert provider is not None
    assert provider.name == "provider1"
    
    provider = provider_manager.get_provider("non_existent")
    assert provider is None

@pytest.mark.asyncio
async def test_get_all_providers(provider_manager):
    """Test getting all enabled providers."""
    providers = provider_manager.get_all_providers()
    assert len(providers) == 3  # Excluding disabled_provider
    assert all(p.enabled for p in providers)
    assert "disabled_provider" not in [p.name for p in providers]

@pytest.mark.asyncio
async def test_generate_completion_default_provider(provider_manager):
    """Test generating a completion with the default provider."""
    result = await provider_manager.generate_completion("Test prompt")
    assert result["provider"] == "provider1"
    assert result["text"] == "Response from provider1"

@pytest.mark.asyncio
async def test_generate_completion_specific_provider(provider_manager):
    """Test generating a completion with a specific provider."""
    result = await provider_manager.generate_completion("Test prompt", provider_name="provider2")
    assert result["provider"] == "provider2"
    assert result["text"] == "Response from provider2"

@pytest.mark.asyncio
async def test_generate_completion_fallback(provider_manager):
    """Test fallback when the specified provider fails."""
    result = await provider_manager.generate_completion("Test prompt", provider_name="failing_provider")
    assert result["provider"] == "provider1"  # Fallback to highest priority
    assert result["text"] == "Response from provider1"

@pytest.mark.asyncio
async def test_generate_completion_all_fail(provider_manager):
    """Test behavior when all providers fail."""
    # Make all providers fail
    for provider in provider_manager.providers.values():
        provider.name = "failing_provider"
    
    with pytest.raises(ProviderError):
        await provider_manager.generate_completion("Test prompt")

@pytest.mark.asyncio
async def test_fallback_strategy_priority(provider_manager):
    """Test priority-based fallback strategy."""
    provider_manager.fallback_strategy = "priority"
    
    # Make the default provider fail
    provider_manager.providers["provider1"].name = "failing_provider"
    
    result = await provider_manager.generate_completion("Test prompt")
    assert result["provider"] == "provider2"  # Next in priority

@pytest.mark.asyncio
async def test_get_provider_status(provider_manager):
    """Test getting provider status information."""
    status = provider_manager.get_provider_status()
    assert len(status) == 4  # All providers, including disabled
    
    provider1_status = next(s for s in status if s["name"] == "provider1")
    assert provider1_status["enabled"] is True
    assert provider1_status["priority"] == 1
    
    disabled_status = next(s for s in status if s["name"] == "disabled_provider")
    assert disabled_status["enabled"] is False
