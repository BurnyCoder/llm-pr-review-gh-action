#!/usr/bin/env python3
"""
Code2Prompt Installer and Tester

This script installs and tests the code2prompt tool, which converts a codebase into 
a single LLM prompt. It handles the installation via cargo and provides example usage.

Usage:
    python code2prompt_installer.py [--install-only] [--path PATH]

Options:
    --install-only  Only install code2prompt without running tests
    --path PATH     Path to the codebase to analyze (default: current directory)
"""

import os
import sys
import argparse
import subprocess
import tempfile
import json


def print_header(text):
    """Print a formatted header text"""
    print("\n" + "=" * 60)
    print(f" {text} ".center(60))
    print("=" * 60)


def check_code2prompt_installed():
    """Check if code2prompt is installed"""
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


def install_code2prompt():
    """Install code2prompt using cargo"""
    print_header("INSTALLING CODE2PROMPT")
    
    # Check if cargo is installed
    try:
        cargo_check = subprocess.run(
            ["cargo", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        
        if cargo_check.returncode != 0:
            print("❌ Cargo is not installed.")
            print("Please install Rust and Cargo first: https://www.rust-lang.org/tools/install")
            return False
        
        print("✅ Cargo is installed. Installing code2prompt...")
        
        # Install code2prompt
        install_process = subprocess.run(
            ["cargo", "install", "code2prompt"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        
        if install_process.returncode == 0:
            print("✅ code2prompt installed successfully!")
            return True
        else:
            print(f"❌ Failed to install code2prompt: {install_process.stderr.decode()}")
            return False
    except Exception as e:
        print(f"❌ Error during installation: {str(e)}")
        return False


def get_codebase(codebase_path=None):
    """
    Generate a prompt containing the entire codebase using code2prompt
    
    Args:
        codebase_path: Path to the codebase. If None, uses current directory.
    
    Returns:
        str: The formatted codebase prompt
    """
    if codebase_path is None:
        codebase_path = os.getcwd()
    
    print(f"Processing codebase at: {codebase_path}")
    
    # Create a temporary file to store the output
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_path = temp_file.name
    
    # Default extensions to include
    code_extensions = [
        "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.css", "*.scss", "*.html",
        "*.vue", "*.go", "*.java", "*.cpp", "*.c", "*.h", "*.rs", "*.sql", 
        "*.md", "*.txt", "*.json", "*.yaml", "*.yml", "*.toml", "*.ini", 
        "*.conf", "*.cfg", "*.properties", "*.env", "*.lock"
    ]
    
    # Build command
    cmd = [
        "code2prompt", 
        codebase_path,
        "--filter", ",".join(code_extensions),
        "--exclude", "package-lock.json",
        "--line-number",
        "--tokens",
        "--output", temp_path
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        # Run code2prompt
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        
        if process.returncode != 0:
            print(f"❌ Error running code2prompt: {process.stderr.decode()}")
            os.unlink(temp_path)
            return ""
        
        # Read the result from the temporary file
        with open(temp_path, 'r') as f:
            content = f.read()
        
        # Delete the temporary file
        os.unlink(temp_path)
        
        return content
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            
        return ""


def test_code2prompt(codebase_path=None):
    """Run a test to analyze a codebase with code2prompt"""
    print_header("TESTING CODE2PROMPT")
    
    # Get the codebase prompt
    prompt = get_codebase(codebase_path)
    
    if prompt:
        preview_length = min(500, len(prompt))
        print("\n✅ Successfully generated codebase prompt!")
        print(f"Generated {len(prompt)} characters")
        print("\nPreview of the first few lines:")
        print("-" * 60)
        print(prompt[:preview_length] + "..." if len(prompt) > preview_length else prompt)
        print("-" * 60)
        
        # Ask if the user wants to save the output
        save_output = input("\nDo you want to save the output to a file? (y/N): ").lower()
        if save_output == 'y':
            output_file = input("Enter the output file path (default: codebase_prompt.md): ") or "codebase_prompt.md"
            try:
                with open(output_file, 'w') as f:
                    f.write(prompt)
                print(f"✅ Output saved to {output_file}")
            except Exception as e:
                print(f"❌ Failed to save output: {str(e)}")
    else:
        print("❌ Failed to generate codebase prompt.")


def main():
    """Install and test the code2prompt tool.

    This function sets up an argument parser to handle command-line arguments for
    installing and testing the code2prompt tool. It checks if code2prompt is
    already installed, installs it if not, and optionally runs tests on a specified
    codebase.

    Dependencies:
        - argparse: Used for parsing command-line arguments.
        - subprocess: Used for running shell commands to check and install code2prompt.
        - check_code2prompt_installed: Function to check if code2prompt is installed.
        - install_code2prompt: Function to install code2prompt using cargo.
        - test_code2prompt: Function to test code2prompt on a specified codebase.
        - print_header: Function to print formatted headers.

    Usages:
        - This function is the main entry point for the script and is called to
          execute the installation and testing process.

    Returns:
        int: Returns 0 on successful completion, 1 if installation fails.
    """
    parser = argparse.ArgumentParser(description="Install and test code2prompt")
    parser.add_argument("--install-only", action="store_true", help="Only install code2prompt without running tests")
    parser.add_argument("--path", help="Path to the codebase to analyze (default: current directory)")
    args = parser.parse_args()
    
    print_header("CODE2PROMPT INSTALLER & TESTER")
    print("This script will install and test code2prompt, a tool to convert")
    print("your codebase into a single LLM prompt.")
    print("\nFor more information, visit: https://github.com/mufeedvh/code2prompt")
    
    # Check if code2prompt is already installed
    if check_code2prompt_installed():
        print("✅ code2prompt is already installed")
        code2prompt_version = subprocess.run(
            ["code2prompt", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        print(f"Version: {code2prompt_version.stdout.decode().strip()}")
    else:
        # Install code2prompt
        if not install_code2prompt():
            print("❌ Installation failed. Please install manually.")
            return 1
    
    # Run tests if not install-only
    if not args.install_only:
        test_code2prompt(args.path)
    
    print_header("COMPLETED")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 