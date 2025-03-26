# Manus Backend

A custom backend system for the Manus Platform that connects to multiple AI providers (OpenAI, Anthropic, etc.) to avoid capacity limits.

## Overview

This backend system is designed to work with the Manus Platform frontend prototype at https://julcalzk.manus.space. It provides a robust API for generating completions from multiple AI providers with automatic fallback mechanisms to ensure reliability and avoid capacity limits.

## Features

- Support for multiple AI providers (OpenAI, Anthropic, etc.)
- Fallback strategies (priority-based, round-robin, random)
- Rate limiting and error handling
- Task queue for background processing
- RESTful API with FastAPI
- Comprehensive testing suite
- Docker containerization for easy deployment

## Architecture

The backend is built with a modular architecture:

- **API Layer**: FastAPI routes for client communication
- **Provider Manager**: Handles multiple AI providers with fallback strategies
- **Provider Implementations**: Specific implementations for each AI provider
- **Task Queue**: Background processing for long-running tasks
- **Configuration**: YAML-based configuration with environment variable support

## Directory Structure

```
manus-backend/
├── src/
│   ├── api/              # API routes and models
│   ├── config/           # Configuration handling
│   ├── integration/      # Integration testing
│   ├── providers/        # AI provider implementations
│   ├── services/         # Core services (provider manager, task queue)
│   ├── utils/            # Utility functions and error handling
│   └── main.py           # Application entry point
├── tests/                # Unit tests
├── config/               # Configuration files
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker container definition
├── docker-compose.yml    # Docker Compose configuration
├── deploy.sh             # Deployment script
└── run_tests.py          # Test runner script
```

## Installation

### Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose (for containerized deployment)
- API keys for supported AI providers (OpenAI, Anthropic, etc.)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd manus-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create configuration file:
   ```bash
   cp config/config.yaml.example config/config.yaml
   ```

5. Edit `config/config.yaml` to add your API keys and customize settings.

6. Run the application:
   ```bash
   python src/main.py
   ```

### Docker Deployment

1. Make the deployment script executable:
   ```bash
   chmod +x deploy.sh
   ```

2. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

3. The backend will be available at http://localhost:8000

## Configuration

The backend is configured through a YAML file located at `config/config.yaml`. You can also use environment variables for sensitive information like API keys.

Example configuration:

```yaml
# Global settings
settings:
  default_provider: "openai"
  fallback_strategy: "priority"  # Options: priority, round-robin, random
  request_timeout: 60
  max_tokens: 4096
  temperature: 0.0
  debug: false
  cors_origins:
    - "*"

# Provider configurations
providers:
  - name: "openai"
    api_key: "${OPENAI_API_KEY}"  # Will be replaced with environment variable
    base_url: "https://api.openai.com/v1"
    models:
      - "gpt-4o"
      - "gpt-4-turbo"
      - "gpt-3.5-turbo"
    priority: 1
    timeout: 30
    max_retries: 3
    enabled: true
    rate_limit: 100  # Requests per minute

  - name: "anthropic"
    api_key: "${ANTHROPIC_API_KEY}"  # Will be replaced with environment variable
    base_url: "https://api.anthropic.com"
    models:
      - "claude-3-opus"
      - "claude-3-sonnet"
      - "claude-3-haiku"
    priority: 2
    timeout: 30
    max_retries: 3
    enabled: true
    rate_limit: 100  # Requests per minute
```

## API Endpoints

### Health Check

```
GET /api/v1/health
```

Returns the health status of the backend.

### Provider Status

```
GET /api/v1/providers
```

Returns the status of all configured AI providers.

### Generate Completion

```
POST /api/v1/completions
```

Generates a completion for the given prompt using the specified provider or fallback strategy.

Request body:
```json
{
  "prompt": "Your prompt text here",
  "provider": "openai",  // Optional, uses default if not specified
  "model": "gpt-4o",     // Optional, uses first model in config if not specified
  "max_tokens": 1000,    // Optional
  "temperature": 0.7     // Optional
}
```

### Task Management

```
POST /api/v1/tasks
```

Creates a new background task.

```
GET /api/v1/tasks/{task_id}
```

Gets the status of a task.

## Testing

Run the test suite:

```bash
python run_tests.py --all
```

Run specific tests:

```bash
python run_tests.py --unit     # Run unit tests only
python run_tests.py --integration  # Run integration tests only
```

## Integration Testing

Test the integration with AI providers:

```bash
python src/integration/test_integration.py
```

## Extending

### Adding a New Provider

1. Create a new provider implementation in `src/providers/`:
   ```python
   from services.provider_manager import Provider, ProviderConfig, ProviderError

   class NewProvider(Provider):
       def _initialize_client(self):
           # Initialize the provider client
           
       async def _generate_completion_impl(self, prompt, model, **kwargs):
           # Implement completion generation
   ```

2. Register the provider in `src/services/provider_manager.py`:
   ```python
   def _initialize_providers(self):
       from providers.openai_provider import OpenAIProvider
       from providers.anthropic_provider import AnthropicProvider
       from providers.new_provider import NewProvider
       
       provider_classes = {
           "openai": OpenAIProvider,
           "anthropic": AnthropicProvider,
           "new_provider": NewProvider,
       }
   ```

3. Add the provider configuration to `config/config.yaml`.

## Continuing Development Across Multiple Threads

This implementation is designed to be easily continued across multiple threads:

1. The modular architecture allows for incremental development
2. Docker containerization ensures consistent deployment
3. Comprehensive documentation facilitates onboarding
4. The codebase can be shared via GitHub or as a zip file

To continue development in a new thread:
1. Share the GitHub repository link or a zip file of the codebase
2. Reference the documentation to understand the current implementation
3. Continue from where you left off, focusing on specific components

## License

[MIT License](LICENSE)
