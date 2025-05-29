"""
Generic prompt template configuration

This module provides prompt templates that support arbitrary programming languages
and project types.

Usage examples:
    # For Python projects
    from src.agent.schema.programmer_input import ProgrammerInput

    input_data = ProgrammerInput(
        instruction="Please create a new API endpoint",
        language="Python",
        project_type="Web application",
        project_root="src/"
    )

    # For TypeScript projects
    input_data = ProgrammerInput(
        instruction="Please create a new component",
        language="TypeScript",
        project_type="React application",
        project_root="frontend/"
    )

    # For Terraform projects
    input_data = ProgrammerInput(
        instruction="Please define a new resource",
        language="Terraform",
        project_type="Infrastructure management",
        project_root="terraform/"
    )

    # Get language-specific configuration
    config = get_language_config("python")
    print(config["test_command"])  # "pytest"
"""

# Prompt template definition
PROGRAMMER_PROMPT_TEMPLATE = """
You are a programmer agent for a {language} project with '{project_root}' directory as root.
Please edit files according to the following user instructions.

## Project Information
- Programming Language: {language}
- Project Type: {project_type}
- Root Directory: {project_root}

Please use the following tools as needed to execute tasks:
- GetFilesList: Get list of files in the project
- ReadFile: Read file contents
- MakeNewFile: Create new files
- OverwriteFile: Overwrite existing files
- ExecTest: Execute tests (using test framework appropriate for the language)
- GeneratePullRequestParams: Generate information needed for PR creation
- RecordLgtm: Record LGTM (review approval)

## Language-specific Considerations
{language_specific_notes}

User instruction: 
{instruction}
"""

# Agent system message
PROGRAMMER_AGENT_SYSTEM_MESSAGE = """You are a professional programming assistant.
Based on user instructions, please perform coding, file operations, test execution, information gathering, etc.
by combining appropriate tools within the project (root is {project_root}) to help achieve the objectives.

- Before execution, first understand the necessary information and perform tool selection and step-by-step execution.
- When a directory is specified, always check where that directory is located.
- Write code following the conventions of the project's language and framework.
Please aim for consistent, reproducible, and accurate code operations.

You can use the following tools:
- GetFilesList: Get list of files in the project
- ReadFile: Read file contents
- MakeNewFile: Create new files
- OverwriteFile: Overwrite existing files
- ExecTest: Execute tests (using test framework appropriate for the language)
- GeneratePullRequestParams: Generate information needed for PR creation
"""

REVIEWER_AGENT_SYSTEM_MESSAGE = """You are a professional reviewer.
Please carefully examine the code diff and point out any issues or improvements.
Please review from the following perspectives:
- Code quality (readability, maintainability, performance)
- Security issues
- Best practice compliance
- Potential bugs
- Design issues

Important: Available tools
- ReviewCode: Review code diff and summarize issues and improvements, determine LGTM (Looks Good To Me)
- RecordLgtm: Record LGTM (review approval)

If the review result shows no issues and the code can be approved, you must call the record_lgtm_function tool to record LGTM (Looks Good To Me).
If there are issues, please point out specific improvements.
"""

# Language-specific configuration templates
LANGUAGE_SPECIFIC_CONFIGS = {
    "python": {
        "test_command": "pytest",
        "package_manager": "pip",
        "config_files": ["requirements.txt", "pyproject.toml", "setup.py"],
        "notes": """
- Maintain coding style following PEP 8
- Use type hints appropriately
- Write proper docstrings
- Virtual environment usage is recommended
        """,
    },
    "javascript": {
        "test_command": "npm test",
        "package_manager": "npm",
        "config_files": ["package.json", "package-lock.json"],
        "notes": """
- Follow ESLint and Prettier configurations
- Use module system (ES6 modules) appropriately
- Use async/await for asynchronous processing
        """,
    },
    "typescript": {
        "test_command": "npm test",
        "package_manager": "npm",
        "config_files": ["package.json", "tsconfig.json"],
        "notes": """
- Make full use of TypeScript's type system
- Enable strict mode
- Use interfaces and type definitions appropriately
        """,
    },
    "java": {
        "test_command": "mvn test",
        "package_manager": "maven",
        "config_files": ["pom.xml", "build.gradle"],
        "notes": """
- Follow Java naming conventions
- Implement proper exception handling
- Write JavaDoc comments
        """,
    },
    "go": {
        "test_command": "go test",
        "package_manager": "go mod",
        "config_files": ["go.mod", "go.sum"],
        "notes": """
- Format with gofmt
- Handle errors appropriately
- Design package structure properly
        """,
    },
    "rust": {
        "test_command": "cargo test",
        "package_manager": "cargo",
        "config_files": ["Cargo.toml", "Cargo.lock"],
        "notes": """
- Understand and use Rust's ownership system
- Format with cargo fmt
- Use Result type for error handling
        """,
    },
    "terraform": {
        "test_command": "terraform plan",
        "package_manager": "terraform",
        "config_files": ["main.tf", "variables.tf", "outputs.tf"],
        "notes": """
- Follow Terraform best practices
- Define variables and outputs appropriately
- Unify resource naming conventions
        """,
    },
}


def get_language_config(language: str) -> dict:
    """
    Get configuration for the specified language

    Args:
        language: Programming language

    Returns:
        Language-specific configuration dictionary
    """
    return LANGUAGE_SPECIFIC_CONFIGS.get(language.lower(), {})
