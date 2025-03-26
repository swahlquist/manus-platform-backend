#!/usr/bin/env python3
"""
Main entry point for the Manus Backend service.
"""

import argparse
import logging
import os
import sys
from fastapi import FastAPI
import uvicorn

from config.settings import load_settings
from api.router import setup_routes
from services.provider_manager import ProviderManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("manus-backend")

app = FastAPI(
    title="Manus Backend",
    description="Backend service for Manus Platform connecting to multiple AI providers",
    version="0.1.0"
)

def initialize_app():
    """Initialize the FastAPI application with routes and middleware."""
    # Load configuration
    settings = load_settings()
    
    # Initialize provider manager
    provider_manager = ProviderManager(settings)
    
    # Setup API routes
    setup_routes(app, provider_manager)
    
    # Add middleware if needed
    # app.add_middleware(...)
    
    logger.info("Manus Backend initialized successfully")
    return app

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Manus Backend Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Set config path if provided
    if args.config:
        os.environ["MANUS_CONFIG_PATH"] = args.config
    
    # Initialize the application
    initialize_app()
    
    # Run the server
    logger.info(f"Starting Manus Backend server on {args.host}:{args.port}")
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()
