# Code2Prompt Utilities

This package provides utilities to convert your codebase into a single LLM prompt using the powerful [code2prompt](https://github.com/mufeedvh/code2prompt) tool.

## Features

- Automatic installation of code2prompt via Cargo
- Python API for interacting with code2prompt
- Drop-in replacement for the existing `get_codebase` function
- Respects .gitignore files
- Ability to filter files using glob patterns
- Support for different output formats (text or JSON)

## Installation

There are two ways to use these utilities:

### 1. Standalone Installer Script

Use the standalone installer script to install and test code2prompt:

```bash
# Make the script executable
chmod +x code2prompt_installer.py

# Run the installer
./code2prompt_installer.py
```

Options:
- `--install-only`: Only install code2prompt without running tests
- `--path PATH`: Path to the codebase to analyze (default: current directory)

### 2. Python Module

The utilities can also be used as a Python module:

```python
from src.backend.agents.implementations.utils.code2prompt_utils import (
    get_codebase,
    get_codebase_with_code2prompt,
    check_code2prompt_installed,
    install_code2prompt
)

# Check if code2prompt is installed
if not check_code2prompt_installed():
    install_code2prompt()

# Get the codebase prompt
codebase_prompt = get_codebase("path/to/your/code")
print(f"Generated a prompt with {len(codebase_prompt)} characters")

# More advanced usage with custom parameters
codebase_prompt = get_codebase_with_code2prompt(
    codebase_path="path/to/your/code",
    include_patterns=["*.py", "*.js"],  # These are passed to --filter
    exclude_patterns=["*.md", "node_modules/**"],
    include_hidden=False,
    respect_gitignore=True,
    add_line_numbers=True,
    output_format="text"  # or "json"
)
```

## Requirements

- Python 3.6+
- Rust and Cargo (for installing code2prompt)

## How It Works

The utility functions use code2prompt under the hood, which:

1. Traverses the directory structure
2. Builds a tree representation of files
3. Collects information about each file
4. Formats this information into a well-structured prompt
5. Outputs the prompt as text or JSON

## Command Line Options

The main command line options for code2prompt are:

- `--filter`: Glob patterns for files to include (e.g., `*.py,*.js`)
- `--exclude`: Glob patterns for files to exclude (e.g., `*.md,test_*`)
- `--exclude-files`: Specific files to exclude
- `--exclude-folders`: Specific folders to exclude
- `--tokens`: Display token count in the generated prompt
- `--encoding`: Specify tokenizer for token count (e.g., `cl100k`, `p50k`)
- `--line-number`: Add line numbers to source code blocks
- `--hidden`: Include hidden files and directories
- `--no-ignore`: Skip .gitignore rules

## About code2prompt

[code2prompt](https://github.com/mufeedvh/code2prompt) is a tool written in Rust that converts a codebase into a single LLM prompt. It offers various features like:

- Customizable prompt generation with Handlebars templates
- Support for .gitignore and glob pattern filtering
- Token counting for various LLM tokenizers
- Git diff output inclusion
- Line number inclusion
- And much more

For more information, visit the [code2prompt GitHub repository](https://github.com/mufeedvh/code2prompt). 