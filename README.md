# Manus Platform Backend

A custom backend system for the Manus Platform that connects to multiple AI providers (OpenAI, Anthropic, etc.) to avoid capacity limits.

## Overview

This backend system is built on top of the [OpenManus](https://github.com/mannaandpoem/OpenManus) framework, leveraging its existing capabilities for connecting to multiple AI providers while extending it to meet the specific requirements of the Manus Platform.

## Architecture

The backend architecture consists of the following core components:

1. **API Gateway** - Entry point for frontend requests
2. **Provider Manager** - Manages connections to multiple AI providers
3. **Request Router** - Routes requests with load balancing and failover
4. **Response Processor** - Standardizes responses from different providers
5. **Task Manager** - Handles long-running tasks
6. **Caching Layer** - Improves performance
7. **Analytics Engine** - Tracks usage and performance

For more details, see the [architecture document](architecture.md).

## Project Structure

```
manus-platform-backend/
├── src/
│   ├── api/           # API endpoints
│   ├── providers/     # AI provider integrations
│   ├── utils/         # Utility functions
│   ├── models/        # Data models
│   └── config/        # Configuration
├── tests/             # Test suite
├── architecture.md    # Architecture documentation
└── README.md          # This file
```

## Getting Started

### Prerequisites

- Python 3.12+
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/swahlquist/manus-platform-backend.git
cd manus-platform-backend
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

### Configuration

Create a `.env` file in the root directory with your API keys:

```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

## Development

This project is under active development. The current focus is on implementing the core backend components and integrating multiple AI providers.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
