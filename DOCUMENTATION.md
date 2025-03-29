# Manus Platform Backend Documentation

## Overview

The Manus Platform Backend is a custom backend system that connects to multiple AI providers (OpenAI, Anthropic, AWS Bedrock, Azure OpenAI) to avoid capacity limits. It's built on top of the [OpenManus](https://github.com/mannaandpoem/OpenManus) framework, leveraging its existing capabilities while extending it to meet the specific requirements of the Manus Platform.

## Architecture

The backend architecture consists of the following core components:

### 1. API Gateway
Serves as the entry point for all frontend requests, handling authentication, validation, and routing.

### 2. Provider Manager
Manages connections to multiple AI providers, handling provider configuration, health monitoring, and selection.

### 3. Request Router
Routes requests to appropriate providers based on availability and load, with failover capabilities.

### 4. Response Processor
Processes and standardizes responses from different providers.

### 5. Task Manager
Manages long-running tasks and asynchronous operations.

### 6. Caching Layer
Caches responses to reduce API calls and improve performance.

### 7. Analytics Engine
Collects and analyzes usage data across providers.

## API Endpoints

### Authentication
- `POST /auth/token` - Get authentication token
- `POST /auth/refresh` - Refresh authentication token

### Chat
- `POST /chat/completions` - Get chat completions
- `POST /chat/stream` - Stream chat completions

### Tasks
- `POST /tasks` - Create a new task
- `GET /tasks/{task_id}` - Get task status and results
- `DELETE /tasks/{task_id}` - Cancel a task

### Providers
- `GET /providers` - List available providers
- `GET /providers/{provider_id}/status` - Get provider status

### Analytics
- `GET /analytics/usage` - Get usage statistics
- `GET /analytics/performance` - Get performance metrics

## Provider Integrations

The backend currently supports the following AI providers:

### 1. OpenAI
- Models: GPT-4o, GPT-4o-mini, etc.
- Implementation: `src/providers/openai_provider.py`
- Configuration: Set `OPENAI_API_KEY` in `.env`

### 2. Anthropic
- Models: Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku
- Implementation: `src/providers/anthropic_provider.py`
- Configuration: Set `ANTHROPIC_API_KEY` in `.env`

### 3. AWS Bedrock
- Models: Claude models, Llama models, etc.
- Implementation: `src/providers/bedrock_provider.py`
- Configuration: Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `.env`

### 4. Azure OpenAI
- Models: GPT-4, GPT-3.5-Turbo, etc.
- Implementation: `src/providers/azure_provider.py`
- Configuration: Set Azure-related variables in `.env`

## Deployment

### Prerequisites
- Docker and Docker Compose
- API keys for at least one AI provider

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/swahlquist/manus-platform-backend.git
   cd manus-platform-backend
   ```

2. Create a `.env` file with your API keys (use `.env.example` as a template):
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

4. Access the API at `http://localhost:8000` and the documentation at `http://localhost:8000/docs`

## Development

### Project Structure
```
manus-platform-backend/
├── src/
│   ├── api/           # API endpoints
│   │   ├── chat.py    # Chat endpoints
│   │   ├── tasks.py   # Task endpoints
│   │   ├── analytics.py # Analytics endpoints
│   │   └── providers.py # Provider endpoints
│   ├── providers/     # AI provider integrations
│   │   ├── manager.py # Provider manager
│   │   ├── router.py  # Request router
│   │   ├── factory.py # Provider factory
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   ├── bedrock_provider.py
│   │   └── azure_provider.py
│   ├── utils/         # Utility functions
│   │   ├── caching.py # Caching layer
│   │   ├── task_manager.py # Task manager
│   │   └── analytics.py # Analytics engine
│   ├── models/        # Data models
│   ├── config/        # Configuration
│   ├── app.py         # Main application
│   └── main.py        # Entry point
├── tests/             # Test suite
│   └── test_api.py    # API tests
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── deploy.sh          # Deployment script
├── .env.example       # Example environment variables
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

### Adding a New Provider
1. Create a new provider class in `src/providers/` that extends `BaseProvider`
2. Implement the required methods: `generate_completion`, `generate_stream`, and `get_status`
3. Add the provider to the factory in `src/providers/factory.py`
4. Update the `.env.example` file with the required configuration variables

### Running Tests
```bash
python -m tests.test_api
```

## Future Development

### Short-term Improvements
1. **Authentication System**: Implement JWT-based authentication for API security
2. **Redis Integration**: Replace in-memory caching with Redis for distributed caching
3. **Database Integration**: Add PostgreSQL for persistent storage of tasks and analytics
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Logging**: Add comprehensive logging for debugging and monitoring

### Medium-term Roadmap
1. **Provider Metrics**: Collect and analyze performance metrics for each provider
2. **Smart Routing**: Implement ML-based routing to select the best provider for each request
3. **Cost Optimization**: Add features to optimize cost across providers
4. **Admin Dashboard**: Create an admin dashboard for monitoring and configuration
5. **Webhook Support**: Add webhook support for asynchronous notifications

### Long-term Vision
1. **Fine-tuning Integration**: Support for fine-tuning models across providers
2. **Multi-region Deployment**: Deploy to multiple regions for improved latency and reliability
3. **Hybrid Deployment**: Support for on-premises deployment alongside cloud providers
4. **Advanced Analytics**: Implement advanced analytics for usage patterns and optimization
5. **Custom Model Support**: Add support for custom models and local inference

## Contributing

We welcome contributions to the Manus Platform Backend! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
