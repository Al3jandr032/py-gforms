# Google Forms Integration POC

A proof of concept for integrating with Google Forms API using Python with support for multiple authentication methods.

## Features

- Google Forms API client with multiple authentication methods
- **Service Account Authentication** (recommended for production)
- **API Key Authentication** (legacy support)
- **OAuth2 Authentication** (for user-based access)
- Type-safe Python code with mypy
- Comprehensive testing with both pytest and unittest
- Code formatting with black and isort
- Linting with flake8
- Pre-commit hooks for code quality
- Environment-based configuration

## Setup

### Prerequisites

- Python 3.12+
- uv package manager

### Installation

1. Clone the repository and navigate to the project directory
2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
3. Configure authentication (see [Authentication](#authentication) section)
4. Install dependencies:
   ```bash
   make install-dev
   ```
5. Install pre-commit hooks:
   ```bash
   make pre-commit
   ```

## Authentication

This library supports three authentication methods:

### 1. Service Account Authentication (Recommended)

Service accounts are ideal for server-to-server applications and provide the most secure authentication method.

#### Setup Service Account:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable the Google Forms API
4. Create a service account
5. Download the service account JSON file
6. Share your Google Forms with the service account email

#### Configuration:
```bash
# Option 1: File path
GOOGLE_SERVICE_ACCOUNT_PATH=/path/to/service-account.json

# Option 2: JSON string (useful for containers)
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}

# Force service account usage
USE_SERVICE_ACCOUNT=true
```

### 2. API Key Authentication (Legacy)

Simple but limited authentication method.

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. OAuth2 Authentication

For applications that need to access forms on behalf of users.

```bash
GOOGLE_CLIENT_SECRETS_PATH=/path/to/client_secrets.json
GOOGLE_TOKEN_PATH=token.json
```

## Usage

### Basic Usage with Service Account

```python
from gforms import GFormsClient

# Method 1: Auto-detect from environment
client = GFormsClient()

# Method 2: Explicit service account file
client = GFormsClient.from_service_account_file("path/to/service-account.json")

# Method 3: Service account JSON string
client = GFormsClient(service_account_json='{"type":"service_account",...}')

# Get form metadata
form_data = client.get_form("your_form_id_here")
print(f"Form title: {form_data['info']['title']}")

# Get form responses (service account only)
responses = client.get_form_responses("your_form_id_here")
print(f"Number of responses: {len(responses.get('responses', []))}")
```

### API Key Authentication

```python
from gforms import GFormsClient

# Initialize with API key
client = GFormsClient(api_key="your_api_key_here")

# Or use environment variable GOOGLE_API_KEY
client = GFormsClient()

# Get form metadata
form_data = client.get_form("your_form_id_here")
print(f"Form title: {form_data['info']['title']}")
```

### OAuth2 Authentication

```python
from gforms import GoogleAuthenticator, GFormsClient

# Initialize authenticator
auth = GoogleAuthenticator()

# Authenticate with OAuth2
credentials = auth.authenticate_with_oauth("path/to/client_secrets.json")

# Use with client (manual setup)
# Note: Direct OAuth integration with GFormsClient coming soon
```

### Running the Example

```bash
uv run python main.py
```

## Development

### Available Commands

```bash
make help           # Show available commands
make install        # Install production dependencies
make install-dev    # Install development dependencies
make test           # Run tests with pytest
make test-unittest  # Run tests with unittest
make test-all       # Run both pytest and unittest tests
make lint           # Run linting
make format         # Format code
make type-check     # Run type checking
make clean          # Clean cache files
make check          # Run all checks (lint + test)
```

### Project Structure

```
gforms/
├── src/gforms/          # Main package
│   ├── __init__.py      # Package initialization
│   ├── core.py          # Core functionality
│   ├── auth.py          # Authentication module
│   └── config.py        # Configuration management
├── tests/               # Test files
│   ├── test_core.py     # Core functionality tests (pytest)
│   └── test_auth_unittest.py  # Authentication tests (unittest)
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── examples.py          # Usage examples
├── .env.example         # Environment template
├── pyproject.toml       # Project configuration
├── Makefile            # Development commands
└── README.md           # This file
```

## Configuration

The application uses environment variables for configuration:

### Authentication
- `GOOGLE_API_KEY`: Your Google API key (legacy method)
- `GOOGLE_SERVICE_ACCOUNT_PATH`: Path to service account JSON file
- `GOOGLE_SERVICE_ACCOUNT_JSON`: Service account JSON as string
- `USE_SERVICE_ACCOUNT`: Force service account authentication
- `GOOGLE_CLIENT_SECRETS_PATH`: Path to OAuth2 client secrets
- `GOOGLE_TOKEN_PATH`: Path to store OAuth2 tokens

### Application
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)

## Testing

This project supports both pytest and unittest frameworks:

### Run pytest tests (with coverage):
```bash
make test
```

### Run unittest tests:
```bash
make test-unittest
```

### Run both test suites:
```bash
make test-all
```

## Authentication Comparison

| Feature | API Key | Service Account | OAuth2 |
|---------|---------|-----------------|--------|
| Setup Complexity | Low | Medium | High |
| Security | Basic | High | High |
| Form Access | Public forms only | Shared forms | User's forms |
| Response Access | No | Yes | Yes |
| Rate Limits | Shared | Dedicated | User-based |
| Production Ready | No | Yes | Yes |

## Code Quality

This project uses several tools to maintain code quality:

- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing framework
- **unittest**: Alternative testing framework
- **pre-commit**: Git hooks

## License

This is a proof of concept project.
