"""
Utility functions for image processing and file operations.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from PIL import Image


def setup_logging(log_file: str, log_level: str = "INFO") -> None:
    """
    Configure logging for the application.
    
    Args:
        log_file: Path to the log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def get_image_files(folder: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    Get all image files from a folder.
    
    Args:
        folder: Path to the folder
        extensions: List of file extensions to include (e.g., ['.jpg', '.png'])
                   If None, uses default image extensions
    
    Returns:
        List of full paths to image files
    """
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
    
    if not os.path.exists(folder):
        logging.warning(f"Folder does not exist: {folder}")
        return []
    
    image_files = []
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions:
                image_files.append(file_path)
    
    return sorted(image_files)


def ensure_folder_exists(folder: str) -> None:
    """
    Create folder if it doesn't exist.
    
    Args:
        folder: Path to the folder
    """
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        logging.info(f"Created folder: {folder}")


def get_output_path(input_path: str, output_folder: str, 
                   output_format: Optional[str] = None,
                   preserve_original_format: bool = False,
                   add_timestamp: bool = False) -> str:
    """
    Generate output file path based on input path.
    
    Args:
        input_path: Path to input file
        output_folder: Output folder path
        output_format: Desired output format (e.g., 'JPEG', 'PNG')
        preserve_original_format: If True, keep original format
        add_timestamp: If True, add timestamp to filename
    
    Returns:
        Full path to output file
    """
    from datetime import datetime
    
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    
    # Add timestamp if requested
    if add_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"{name}_{timestamp}"
    
    if preserve_original_format or output_format is None:
        output_ext = ext
    else:
        # Map format to extension
        format_map = {
            'JPEG': '.jpg',
            'JPG': '.jpg',
            'PNG': '.png',
            'WEBP': '.webp',
            'BMP': '.bmp'
        }
        output_ext = format_map.get(output_format.upper(), '.jpg')
    
    return os.path.join(output_folder, f"{name}{output_ext}")


def validate_image(image_path: str) -> bool:
    """
    Validate if a file is a valid image.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        True if valid, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception as e:
        logging.error(f"Invalid image {image_path}: {str(e)}")
        return False


def format_time(seconds: float) -> str:
    """
    Format time in seconds to a readable string.
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
