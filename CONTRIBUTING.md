# Contributing to SwordFish

Thank you for your interest in contributing to SwordFish! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

Before submitting a bug report:
- Check if the issue has already been reported
- Ensure you're using the latest version
- Check the documentation for potential solutions

When submitting a bug report, include:
- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs. actual behavior
- Screenshots or error logs if applicable
- Environment details (OS, browser, etc.)

### Suggesting Features

Feature suggestions are welcome! Please provide:
- A clear and descriptive title
- Detailed explanation of the proposed feature
- Any relevant examples or mockups
- Explanation of why this feature would be useful

### Pull Requests

1. Fork the repository
2. Create a new branch from `main`
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality
5. Submit a pull request

#### Pull Request Guidelines

- Follow the coding style of the project
- Include tests for new features or bug fixes
- Update documentation as needed
- Keep pull requests focused on a single change
- Write clear commit messages

## Development Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git

### Local Development

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/SwordFish.git
   cd SwordFish
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r Fish/requirements.txt
   ```

4. Create a `.env` file in the `Fish` directory (see `.env.example`)

5. Start the development environment
   ```bash
   ./run-dev.bat
   ```

### Running Tests

```bash
python -m pytest
```

## Project Structure

Please familiarize yourself with the project structure before contributing:

```
SwordFish/
├── Fish/                  # Main application code
│   ├── alembic/           # Database migrations
│   ├── app/               # Application code
│   │   ├── api/           # API routes
│   │   ├── core/          # Core functionality
│   │   ├── db/            # Database configuration
│   │   ├── models/        # SQLAlchemy models
│   │   ├── repositories/  # Data access layer
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── tasks/         # Celery tasks
│   │   └── utility/       # Utility functions
│   ├── tests/             # Test code
│   └── requirements.txt   # Python dependencies
├── docker/                # Docker configuration
```

## Coding Standards

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all functions, classes, and modules
- Keep functions small and focused on a single responsibility
- Use meaningful variable and function names

## License

By contributing to SwordFish, you agree that your contributions will be licensed under the project's license.

## Questions?

If you have any questions about contributing, please open an issue or contact the project maintainers.