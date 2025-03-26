# Manus Backend API Documentation

This document provides detailed information about the API endpoints available in the Manus Backend system.

## Base URL

All API endpoints are prefixed with `/api/v1`.

## Authentication

Currently, the API does not implement authentication. In a production environment, you should implement an authentication mechanism such as API keys or OAuth.

## Endpoints

### Health Check

**Endpoint:** `GET /api/v1/health`

**Description:** Check if the backend service is running properly.

**Response:**
```json
{
  "status": "ok"
}
```

### Provider Status

**Endpoint:** `GET /api/v1/providers`

**Description:** Get status information for all configured AI providers.

**Response:**
```json
{
  "providers": [
    {
      "name": "openai",
      "enabled": true,
      "priority": 1,
      "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
      "error_count": 0,
      "request_count": 42
    },
    {
      "name": "anthropic",
      "enabled": true,
      "priority": 2,
      "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
      "error_count": 0,
      "request_count": 17
    }
  ]
}
```

### Generate Completion

**Endpoint:** `POST /api/v1/completions`

**Description:** Generate a completion for the given prompt using the specified provider or fallback strategy.

**Request:**
```json
{
  "prompt": "Explain quantum computing in simple terms",
  "provider": "openai",
  "model": "gpt-4o",
  "max_tokens": 1000,
  "temperature": 0.7,
  "stream": false
}
```

**Parameters:**
- `prompt` (required): The prompt to generate a completion for
- `provider` (optional): The name of the provider to use. If not specified, uses the default provider.
- `model` (optional): The model to use for generation. If not specified, uses the first model in the provider's configuration.
- `max_tokens` (optional): Maximum number of tokens to generate
- `temperature` (optional): Controls randomness in the response (0.0 to 1.0)
- `stream` (optional): Whether to stream the response (not currently implemented)

**Response:**
```json
{
  "text": "Quantum computing is like...",
  "provider": "openai",
  "model": "gpt-4o",
  "tokens": 156,
  "request_id": "req_abc123"
}
```

### Create Task

**Endpoint:** `POST /api/v1/tasks`

**Description:** Create a new background task.

**Request:**
```json
{
  "task_type": "completion",
  "content": "Generate a long essay about climate change",
  "parameters": {
    "max_tokens": 4000,
    "temperature": 0.5
  }
}
```

**Parameters:**
- `task_type` (required): Type of task to create
- `content` (required): Content for the task
- `parameters` (optional): Additional parameters for the task

**Response:**
```json
{
  "task_id": "task_123456",
  "status": "pending"
}
```

### Get Task Status

**Endpoint:** `GET /api/v1/tasks/{task_id}`

**Description:** Get the status of a task.

**Parameters:**
- `task_id` (path parameter): ID of the task to get status for

**Response:**
```json
{
  "task_id": "task_123456",
  "status": "in_progress",
  "progress": 0.5,
  "result": null
}
```

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `502 Bad Gateway`: Provider error

Error responses have the following format:

```json
{
  "error": {
    "status_code": 400,
    "message": "Invalid request parameters",
    "details": {
      "field": "prompt",
      "issue": "cannot be empty"
    }
  }
}
```

## Rate Limiting

The API does not currently implement rate limiting at the API level. Provider-level rate limiting is handled internally by the provider manager.

## Versioning

The API is versioned in the URL path (`/api/v1/`). Future versions will use `/api/v2/`, etc.
