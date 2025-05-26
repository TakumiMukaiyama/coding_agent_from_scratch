# Coding Agent From Scratch

A sophisticated AI-powered coding assistant system built from scratch using LangChain and OpenAI. This project implements a collaborative development workflow where a Programmer Agent and Reviewer Agent work together to generate, review, and improve code automatically.

## Purpose

This project aims to create an intelligent coding assistant that can:

- **Automated Code Generation**: Generate high-quality code based on natural language instructions
- **Intelligent Code Review**: Automatically review generated code for quality, best practices, and potential issues
- **Iterative Development**: Implement a feedback loop between programmer and reviewer agents for continuous improvement
- **Git Integration**: Automatically manage Git branches and create pull requests for generated code
- **Multi-language Support**: Support various programming languages and frameworks

The system follows a development cycle where:
1. The Programmer Agent generates code based on user instructions
2. The Reviewer Agent analyzes the generated code and provides feedback
3. The cycle repeats until the code meets quality standards (LGTM - Looks Good To Me)
4. The system can automatically create Git branches and manage version control

## Features

- **Agent Coordination**: Seamless collaboration between programmer and reviewer agents
- **Automated Branch Management**: Intelligent Git branch naming and creation
- **Code Quality Assurance**: Built-in code review and quality checks
- **Flexible Configuration**: Customizable coding rules and standards
- **CLI Interface**: Easy-to-use command-line interface for agent execution
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## Environment Setup with uv

This project uses [uv](https://github.com/astral-sh/uv) for fast and reliable Python package management.

### Prerequisites

- Python 3.12 or higher
- uv package manager

### Installing uv

If you don't have uv installed, you can install it using:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip
pip install uv
```

### Project Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd coding_agent_from_scratch
   ```

2. **Create and activate virtual environment**:
   ```bash
   # uv will automatically create a virtual environment and install dependencies
   uv sync
   ```

3. **Activate the virtual environment**:
   ```bash
   # On macOS/Linux
   source .venv/bin/activate
   
   # On Windows
   .venv\Scripts\activate
   ```

4. **Environment Configuration**:
   Create a `.env` file in the project root and configure your API keys:
   ```bash
   cp .env.example .env  # If example file exists
   # Edit .env file with your configuration
   ```

   Required environment variables:
   - OpenAI API credentials
   - Azure OpenAI configuration (if using Azure)
   - Other service-specific configurations

### Development Setup

For development, you can install additional development dependencies:

```bash
# Install development dependencies
uv add --dev pytest ruff black mypy

# Run tests
uv run pytest

# Run linting
uv run ruff check

# Format code
uv run black .
```

## Usage

### Basic Usage

Run the coding agent with a simple instruction:

```bash
uv run python src/main.py coordinator "Create a simple web API using FastAPI"
```

### Advanced Usage

The system supports various parameters for customization:

- **Max Iterations**: Control the number of review cycles
- **Auto Branch Creation**: Automatically create Git branches
- **Custom Instructions**: Provide detailed coding requirements

### Example Commands

```bash
# Generate a REST API
uv run python src/main.py coordinator "Create a REST API for user management with CRUD operations"

# Create a data processing script
uv run python src/main.py coordinator "Build a data processing pipeline for CSV files"

# Generate frontend components
uv run python src/main.py coordinator "Create React components for a todo application"
```

## Project Structure

```
src/
├── agent/                 # Agent-related modules
│   ├── function/         # Agent functions and tools
│   ├── rules/           # Coding rules and standards
│   └── schema/          # Data schemas
├── application/         # Application layer
├── infrastructure/      # Infrastructure and utilities
├── usecase/            # Business logic and use cases
│   ├── programmer/     # Programmer agent implementation
│   └── reviewer/       # Reviewer agent implementation
└── main.py             # CLI entry point

generated_code/         # Output directory for generated code
tests/                 # Test files
```

## Configuration

The system can be configured through:

- **Coding Rules**: Modify `src/agent/rules/coding_rule.md` to customize coding standards
- **Agent Behavior**: Configure agent parameters in the respective modules
- **Environment Variables**: Set API keys and service configurations in `.env`

## Contributing

1. Fork the repository
2. Create a feature branch using the automated branch naming system
3. Make your changes following the project's coding standards
4. Run tests and ensure code quality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or contributions, please [create an issue](link-to-issues) or contact the development team.
