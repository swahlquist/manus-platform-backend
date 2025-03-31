"""
Command-line utility for testing provider integration.
"""

import asyncio
import argparse
import logging
import json
import os
import sys
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from integration.provider_integration import ProviderIntegration
from config.settings import load_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("manus-backend.test_integration")

async def main():
    """Main entry point for the integration test utility."""
    parser = argparse.ArgumentParser(description="Manus Backend Provider Integration Test")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--test-provider", help="Test a specific provider")
    parser.add_argument("--test-all", action="store_true", help="Test all providers")
    parser.add_argument("--test-fallback", action="store_true", help="Test fallback strategy")
    parser.add_argument("--simulate-rate-limit", help="Simulate rate limiting for a provider")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Set config path if provided
    if args.config:
        os.environ["MANUS_CONFIG_PATH"] = args.config
    
    # Load settings and create integration tester
    settings = load_settings()
    integration = ProviderIntegration(settings)
    
    # Run tests based on arguments
    results = {}
    
    if args.test_provider:
        logger.info(f"Testing provider: {args.test_provider}")
        results["provider_test"] = await integration.test_provider(args.test_provider)
    
    if args.test_all:
        logger.info("Testing all providers")
        results["all_providers"] = await integration.test_all_providers()
    
    if args.test_fallback:
        logger.info("Testing fallback strategy")
        results["fallback_test"] = await integration.test_fallback_strategy()
    
    if args.simulate_rate_limit:
        logger.info(f"Simulating rate limit for provider: {args.simulate_rate_limit}")
        results["rate_limit_test"] = await integration.simulate_rate_limit(args.simulate_rate_limit)
    
    # If no specific tests were requested, run all tests
    if not any([args.test_provider, args.test_all, args.test_fallback, args.simulate_rate_limit]):
        logger.info("Running all integration tests")
        results["all_providers"] = await integration.test_all_providers()
        results["fallback_test"] = await integration.test_fallback_strategy()
        
        # Simulate rate limit for the first provider
        providers = integration.provider_manager.get_all_providers()
        if providers:
            first_provider = providers[0].name
            logger.info(f"Simulating rate limit for provider: {first_provider}")
            results["rate_limit_test"] = await integration.simulate_rate_limit(first_provider)
    
    # Print results
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
