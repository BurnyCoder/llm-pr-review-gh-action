import os
import subprocess
import logging
import json
import tempfile
from typing import Dict, List, Optional, Union, Any

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_code2prompt_installed() -> bool:
    """
    Check if code2prompt is installed.
    
    Returns:
        bool: True if code2prompt is installed, False otherwise
    """
    try:
        result = subprocess.run(
            ["code2prompt", "--version"], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_code2prompt() -> bool:
    """
    Install code2prompt using cargo.
    
    Returns:
        bool: True if installation was successful, False otherwise
    """
    logger.info("Installing code2prompt...")
    try:
        # Check if cargo is installed
        cargo_check = subprocess.run(
            ["cargo", "--version"], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        
        if cargo_check.returncode != 0:
            logger.error("Cargo is not installed. Please install Rust and Cargo first: https://www.rust-lang.org/tools/install")
            return False
        
        # Install code2prompt
        install_process = subprocess.run(
            ["cargo", "install", "code2prompt"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        
        if install_process.returncode == 0:
            logger.info("code2prompt installed successfully")
            return True
        else:
            logger.error(f"Failed to install code2prompt: {install_process.stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"Error installing code2prompt: {str(e)}")
        return False


def get_codebase_with_code2prompt(
    codebase_path: str = None,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    include_hidden: bool = False,
    respect_gitignore: bool = True,
    add_line_numbers: bool = True,
    output_format: str = "text"
) -> Union[str, Dict[str, Any]]:
    """
    Generate a prompt containing the entire codebase using code2prompt.
    
    Args:
        codebase_path: Path to the codebase. If None, uses current directory.
        include_patterns: List of glob patterns to include (e.g. ["*.py", "*.js"])
        exclude_patterns: List of glob patterns to exclude (e.g. ["*.md", "*.txt"])
        include_hidden: Whether to include hidden files and directories
        respect_gitignore: Whether to respect .gitignore rules
        add_line_numbers: Whether to add line numbers to source code
        output_format: Format of the output ("text" or "json")
    
    Returns:
        Union[str, Dict[str, Any]]: The codebase as a formatted string or JSON object
    """
    # If no path is provided, use current directory
    if codebase_path is None:
        codebase_path = os.getcwd()
    
    # Ensure code2prompt is installed
    if not check_code2prompt_installed():
        if not install_code2prompt():
            logger.error("Failed to install code2prompt, cannot continue")
            return "" if output_format == "text" else {"prompt": "", "files": []}
    
    # Build command
    cmd = ["code2prompt", codebase_path]
    
    # Add optional flags
    if include_patterns:
        cmd.extend(["--include", ",".join(include_patterns)])
    
    if exclude_patterns:
        cmd.extend(["--exclude", ",".join(exclude_patterns)])
    
    if include_hidden:
        cmd.append("--hidden")
    
    if not respect_gitignore:
        cmd.append("--no-ignore")
    
    if add_line_numbers:
        cmd.append("--line-number")
    
    # Add output format
    if output_format == "json":
        cmd.append("--json")
    
    # Create a temporary file to store the output
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_path = temp_file.name
    
    cmd.extend(["--output", temp_path])
    
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        # Run code2prompt
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        
        if process.returncode != 0:
            logger.error(f"Error running code2prompt: {process.stderr.decode()}")
            os.unlink(temp_path)
            return "" if output_format == "text" else {"prompt": "", "files": []}
        
        # Read the result from the temporary file
        with open(temp_path, 'r') as f:
            content = f.read()
        
        # Delete the temporary file
        os.unlink(temp_path)
        
        # Parse JSON if needed
        if output_format == "json":
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON output from code2prompt")
                return {"prompt": content, "files": []}
        
        return content
    
    except Exception as e:
        logger.error(f"Error using code2prompt: {str(e)}")
        
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            
        return "" if output_format == "text" else {"prompt": "", "files": []}


def get_codebase(codebase_path: str = None) -> str:
    """
    Generates a prompt containing the entire codebase using code2prompt.
    
    This is a drop-in replacement for the original get_codebase function, 
    using code2prompt under the hood for better code extraction.
    
    Args:
        codebase_path: Optional custom path to the codebase. If None, uses current directory.
    
    Returns:
        str: A formatted string containing all code with file paths as headers
    """
    # Default include patterns - match the original function's extensions
    code_extensions = [
        "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.css", "*.scss", "*.html",
        "*.vue", "*.go", "*.java", "*.cpp", "*.c", "*.h", "*.rs", "*.sql", 
        "*.md", "*.txt", "*.json", "*.yaml", "*.yml", "*.toml", "*.ini", 
        "*.conf", "*.cfg", "*.properties", "*.env", "*.lock"
    ]
    
    # Exclude package-lock.json files to match original function
    exclude_patterns = ["package-lock.json"]
    
    return get_codebase_with_code2prompt(
        codebase_path=codebase_path,
        include_patterns=code_extensions,
        exclude_patterns=exclude_patterns,
        include_hidden=False,
        respect_gitignore=True,
        add_line_numbers=True,
        output_format="text"
    )


if __name__ == "__main__":
    # Example usage
    print("Checking if code2prompt is installed...")
    if not check_code2prompt_installed():
        print("Installing code2prompt...")
        success = install_code2prompt()
        if success:
            print("Installation successful!")
        else:
            print("Installation failed. Please install manually using: cargo install code2prompt")
    else:
        print("code2prompt is already installed")
    
    # Test get_codebase function
    print("\nTesting get_codebase function...")
    codebase = get_codebase()
    print(f"Successfully generated codebase prompt with {len(codebase)} characters") 