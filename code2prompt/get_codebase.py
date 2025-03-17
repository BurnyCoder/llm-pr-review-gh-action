import os
import logging
from .code2prompt_utils import get_codebase as code2prompt_get_codebase

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to WARNING to disable most logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_codebase(codebase_path: str = None) -> str:
    """
    Generates a prompt containing the entire codebase by recursively reading all code files.
    
    This function now uses code2prompt under the hood for better code extraction.
    If code2prompt is not available or fails, it will fall back to the original implementation.
    
    Args:
        codebase_path: Optional custom path to the codebase. If None, uses current directory.
    
    Returns:
        str: A formatted string containing all code with file paths as headers
    """
    try:
        # Try to use code2prompt
        return code2prompt_get_codebase(codebase_path)
    except Exception as e:
        logger.warning(f"Failed to use code2prompt: {str(e)}. Falling back to legacy implementation.")
        return get_codebase_legacy(codebase_path)


def get_codebase_legacy(codebase_path: str = None) -> str:
    """
    Original implementation of get_codebase.
    Recursively reads all code files (.py, .js, .css, .html, .ts, etc.) except those in .gitignore.
    
    Args:
        codebase_path: Optional custom path to the codebase. If None, uses AI_PLAYGROUND_PATH.
    
    Returns:
        str: A formatted string containing all code with file paths as headers
    """
    logger.debug("Getting codebase using legacy method")
    codebase_prompt = []
        
    # Code file extensions to include
    CODE_EXTENSIONS = {'.py', '.js', '.jsx', '.ts', '.tsx', '.css', '.scss', '.html', '.vue', '.go', '.java', '.cpp', '.c', '.h', '.rs', '.sql', '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.cfg', '.properties', '.env', '.lock', '.lockb', '.lock.json', '.lock.yaml', '.lock.yml', '.lock.toml', '.lock.ini', '.lock.conf', '.lock.cfg', '.lock.properties', '.lock.env'}
    
    # Store gitignore patterns from all .gitignore files
    gitignore_patterns = {}
    
    def load_gitignore_patterns(directory):
        """Load gitignore patterns from a directory's .gitignore file if it exists"""
        gitignore_path = os.path.join(directory, '.gitignore')
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, 'r') as f:
                    return [line.strip() for line in f if line.strip() and not line.startswith('#')]
            except Exception as e:
                logger.error(f"Error reading {gitignore_path}: {str(e)}")
        return []

    def is_ignored(path):
        """Check if path matches any gitignore pattern from parent directories"""
        rel_path = os.path.relpath(path, codebase_path)
        current_dir = os.path.dirname(path)
        
        # Check patterns from current and all parent directories
        while current_dir >= codebase_path:
            if current_dir in gitignore_patterns:
                for pattern in gitignore_patterns[current_dir]:
                    if pattern.endswith('/'):
                        if rel_path.startswith(pattern):
                            return True
                    elif pattern.startswith('*'):
                        if rel_path.endswith(pattern[1:]):
                            return True
                    elif pattern in rel_path:
                        return True
            current_dir = os.path.dirname(current_dir)
        return False

    # First pass: collect all gitignore patterns
    logger.debug("Collecting gitignore patterns")
    for root, _, _ in os.walk(codebase_path):
        patterns = load_gitignore_patterns(root)
        if patterns:
            gitignore_patterns[root] = patterns

    # Second pass: read files
    logger.debug("Reading files for codebase")
    for root, _, files in os.walk(codebase_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1]
            
            if file_ext not in CODE_EXTENSIONS:
                continue
                
            # Skip package-lock.json files
            if file == "package-lock.json":
                continue
                
            if not is_ignored(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        relative_path = os.path.relpath(file_path, codebase_path)
                        # Detect file type for syntax highlighting
                        ext = file_ext[1:]  # Remove the dot
                        codebase_prompt.append(f"\n### {relative_path}\n```{ext}\n{content}\n```\n")
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {str(e)}")
                    
    logger.debug("Successfully generated codebase")
    return "\n".join(codebase_prompt) 