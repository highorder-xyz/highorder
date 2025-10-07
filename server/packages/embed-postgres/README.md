# Embed PostgreSQL

A Python library for embedding PostgreSQL databases, similar to the Rust [postgresql-embedded](https://github.com/theseus-rs/postgresql-embedded) project. This library provides an embedded-like experience for PostgreSQL similar to what you would have with SQLite.

## Features

- **Automatic Installation**: Downloads and installs PostgreSQL binaries at runtime
- **Cross-Platform**: Supports Linux, macOS, and Windows
- **Ephemeral Ports**: Automatically finds available ports for PostgreSQL instances
- **Database Management**: Create, drop, and check database existence
- **Easy Configuration**: Flexible configuration options
- **Context Manager**: Clean resource management with Python context managers
- **Cleanup**: Automatic cleanup on exit

## Installation

### Using uv (recommended)

```bash
uv add embed-postgres
```

### Using pip

```bash
pip install embed-postgres
```

## Quick Start

```python
from embed_postgres import PostgreSQL

# Basic usage
with PostgreSQL() as postgres:
    # Create a database
    postgres.create_database("test_db")
    
    # Check if database exists
    exists = postgres.database_exists("test_db")
    print(f"Database exists: {exists}")
    
    # Get connection URL
    url = postgres.get_connection_url("test_db")
    print(f"Connection URL: {url}")
    
    # Drop database
    postgres.drop_database("test_db")
```

## Manual Management

```python
from embed_postgres import PostgreSQL, PostgreSQLConfig

# Custom configuration
config = PostgreSQLConfig(
    version="15.4",
    port=5432,
    username="myuser",
    password="mypassword"
)

postgres = PostgreSQL(config)

# Setup and start
postgres.setup()  # Download and install PostgreSQL
postgres.start()  # Start the server

# Use the database
postgres.create_database("my_app_db")

# Stop when done
postgres.stop()
```

## Configuration Options

```python
from embed_postgres import PostgreSQLConfig

config = PostgreSQLConfig(
    version="15.4",                    # PostgreSQL version
    port=5432,                         # Port (None for auto-assign)
    host="localhost",                  # Host address
    username="postgres",               # Username
    password="password",               # Password
    install_dir="/custom/install",     # Installation directory
    data_dir="/custom/data",           # Data directory
    timeout=30,                        # Startup timeout
    cleanup_on_exit=True,              # Auto cleanup
    postgres_config={                  # PostgreSQL settings
        "max_connections": "200",
        "shared_buffers": "256MB"
    }
)
```

## Database Operations

```python
with PostgreSQL() as postgres:
    # Create database
    postgres.create_database("app_db")
    
    # Check existence
    if postgres.database_exists("app_db"):
        print("Database ready!")
    
    # Get connection details
    url = postgres.get_connection_url("app_db")
    
    # Use with your favorite PostgreSQL client
    import psycopg2
    conn = psycopg2.connect(url)
    
    # Clean up
    postgres.drop_database("app_db")
```

## Advanced Examples

### Custom Data Directory and No Cleanup

```python
from embed_postgres import PostgreSQL, PostgreSQLConfig

# Custom data directory with persistence
config = PostgreSQLConfig(
    version="17.6",
    data_dir="/path/to/custom/data",
    cleanup_on_exit=False,  # Data persists after exit
    postgres_config={
        "shared_buffers": "256MB",
        "max_connections": "100"
    }
)

postgres = PostgreSQL(config)
postgres.setup()
postgres.start()

# Data will persist after postgres.stop()
```

### Multiple Instances

```python
# Run multiple PostgreSQL instances simultaneously
config1 = PostgreSQLConfig(port=5434, data_dir="/tmp/instance1")
config2 = PostgreSQLConfig(port=5435, data_dir="/tmp/instance2")

postgres1 = PostgreSQL(config1)
postgres2 = PostgreSQL(config2)

postgres1.setup()
postgres1.start()
postgres2.setup() 
postgres2.start()

# Both instances running on different ports
```

### Production-like Configuration

```python
config = PostgreSQLConfig(
    version="17.6",
    cleanup_on_exit=False,
    postgres_config={
        "shared_buffers": "512MB",
        "effective_cache_size": "2GB",
        "max_connections": "200",
        "log_statement": "mod",
        "log_min_duration_statement": "5000"
    }
)
```

## Error Handling

```python
from embed_postgres import PostgreSQL, PostgreSQLEmbeddedError

try:
    with PostgreSQL() as postgres:
        postgres.create_database("test")
except PostgreSQLEmbeddedError as e:
    print(f"PostgreSQL error: {e}")
```

## Requirements

- Python 3.8+
- Internet connection (for initial PostgreSQL download)
- Sufficient disk space for PostgreSQL installation

## Platform Support

- **Linux**: x86_64, ARM64
- **macOS**: x86_64, ARM64 (Apple Silicon)
- **Windows**: x86_64

## License

MIT License

## Development

### Using uv for development

```bash
# Clone the repository
git clone https://github.com/zeaphoo/embed-postgres.git
cd embed-postgres

# Install dependencies with uv
uv sync

# Run tests
uv run pytest

# Run examples
uv run python examples/basic_usage.py
uv run python examples/advanced_configuration.py
uv run python examples/production_like.py
uv run python examples/version_management.py

# Format code
uv run black .

# Type checking
uv run mypy embed_postgres/
```

### Project structure with uv

This project uses `uv` for modern Python dependency management:

- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Locked dependency versions (generated by uv)
- No `requirements.txt` or `setup.py` needed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
