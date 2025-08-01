#!/usr/bin/env python3
"""
Cleanup Script
Removes temporary files and test outputs
"""

import os
import shutil
from pathlib import Path

def cleanup_temp_files():
    """Remove temporary and test files."""
    
    # Files to remove
    temp_files = [
        "test_*.py",
        "test_*.json",
        "*.log",
        "__pycache__",
        ".pytest_cache"
    ]
    
    # Directories to clean
    temp_dirs = [
        "logs",
        "cache",
        "excel"
    ]
    
    root_dir = Path(".")
    
    print("Cleaning up temporary files...")
    
    # Remove temp files
    for pattern in temp_files:
        for file_path in root_dir.glob(pattern):
            if file_path.is_file():
                try:
                    file_path.unlink()
                    print(f"Removed: {file_path}")
                except Exception as e:
                    print(f"Could not remove {file_path}: {e}")
            elif file_path.is_dir():
                try:
                    shutil.rmtree(file_path)
                    print(f"Removed directory: {file_path}")
                except Exception as e:
                    print(f"Could not remove {file_path}: {e}")
    
    # Clean temp directories
    for dir_name in temp_dirs:
        dir_path = root_dir / dir_name
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"Removed directory: {dir_name}")
            except Exception as e:
                print(f"Could not remove {dir_name}: {e}")

if __name__ == "__main__":
    cleanup_temp_files()
    print("Cleanup completed!")
