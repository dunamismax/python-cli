# Python CLI Monorepo

A comprehensive monorepo for Python CLI applications and utilities built with modern Python tools and best practices.

## 🚀 Features

- **FastAPI Backend**: Modern, high-performance web framework with automatic API documentation
- **Typer CLI Apps**: Beautiful command-line interfaces with Rich integration
- **SQLAlchemy ORM**: Async database operations with SQLite/PostgreSQL support
- **Pydantic Models**: Data validation and serialization
- **Poetry Package Management**: Modern dependency management
- **Pytest Testing**: Comprehensive test suite with fixtures
- **Rich Console Output**: Beautiful terminal interfaces
- **Docker Support**: Containerized deployment
- **Type Safety**: Full typing support with mypy

## 📦 Applications

### 1. API Server (`apps/api_server`)
A FastAPI-based REST API server with user and task management.

**Features:**
- User CRUD operations
- Task management with filtering and pagination
- Async database operations
- API documentation with Swagger UI
- Error handling and validation

**Usage:**
```bash
# Start the API server
poetry run api-server

# Access API docs at http://localhost:8000/docs
```

### 2. Todo CLI (`apps/todo_cli`)
A powerful command-line todo application with rich terminal interface.

**Features:**
- Add, update, delete tasks
- Priority levels and status tracking
- Tag support
- Statistics and filtering
- JSON storage with backup/restore
- Beautiful terminal output

**Usage:**
```bash
# Add a new task
poetry run todo-cli add "Buy groceries" --priority high --tag shopping

# List all tasks
poetry run todo-cli list

# Complete a task
poetry run todo-cli complete 1

# Show statistics
poetry run todo-cli stats
```

### 3. File Organizer (`apps/file_organizer`)
A CLI tool for organizing files by type, date, or size.

**Features:**
- Organize files by type (images, documents, etc.)
- Organize files by date
- Organize files by size
- Find and remove duplicates
- Clean empty directories
- Directory statistics
- Dry-run mode

**Usage:**
```bash
# Organize files by type
poetry run file-organizer organize-by-type /path/to/messy/folder

# Find duplicates
poetry run file-organizer find-duplicates /path/to/folder --remove

# Get directory statistics
poetry run file-organizer stats /path/to/folder
```

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone https://github.com/dunamismax/python-cli.git
cd python-cli
```

2. **Install Poetry (if not already installed):**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. **Install dependencies:**
```bash
poetry install
```

4. **Activate the virtual environment:**
```bash
poetry shell
```

## 🏗️ Development

### Project Structure
```
python-cli/
├── apps/                    # Application modules
│   ├── api_server/         # FastAPI application
│   ├── todo_cli/           # Todo CLI application
│   └── file_organizer/     # File organizer CLI
├── shared/                 # Shared utilities
│   ├── config.py          # Configuration management
│   ├── database.py        # Database utilities
│   ├── logging.py         # Logging setup
│   └── utils.py           # Common utilities
├── tests/                  # Test suite
│   ├── test_shared/       # Shared module tests
│   └── test_apps/         # Application tests
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=apps --cov=shared

# Run specific test file
poetry run pytest tests/test_apps/test_todo_cli.py
```

### Code Quality
```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Lint code
poetry run flake8

# Type checking
poetry run mypy apps shared
```

### Adding New Applications

1. Create a new directory under `apps/`
2. Add your application code
3. Update `pyproject.toml` to include the new script entry point
4. Add tests under `tests/test_apps/`
5. Update this README

## 🔧 Configuration

Applications use environment variables and `.env` files for configuration:

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./data/app.db

# API Server
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true

# Logging
LOG_LEVEL=INFO

# Directories
DATA_DIR=./data
LOGS_DIR=./logs
```

## 🐳 Docker Support

```bash
# Build image
docker build -t python-cli .

# Run API server
docker run -p 8000:8000 python-cli api-server

# Run with docker-compose
docker-compose up
```

## 🧪 Testing

The project includes comprehensive tests with:
- Unit tests for all modules
- Integration tests for API endpoints
- Fixture-based test setup
- Coverage reporting
- Async test support

## 📚 Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using type hints
- **Uvicorn**: ASGI server implementation
- **Celery**: Distributed task queue
- **Redis**: In-memory data store

### CLI
- **Typer**: Modern CLI framework
- **Rich**: Rich text and beautiful formatting
- **Click**: Command line interface creation kit

### Development
- **Poetry**: Dependency management
- **Pytest**: Testing framework
- **Black**: Code formatter
- **isort**: Import sorter
- **Flake8**: Linting
- **mypy**: Static type checker

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Run the test suite
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 👤 Author

**dunamismax**
- Email: dunamismax@tutamail.com
- GitHub: [@dunamismax](https://github.com/dunamismax)

## 🔗 Links

- [Repository](https://github.com/dunamismax/python-cli)
- [Issues](https://github.com/dunamismax/python-cli/issues)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Poetry Documentation](https://python-poetry.org/docs/)