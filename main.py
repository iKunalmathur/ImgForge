#!/usr/bin/env python3
"""
ImgForge
Main entry point for the CLI application.
"""

from src.utils import setup_logging, ensure_folder_exists
from src.image_processor import ImageProcessor
import os
import sys
import argparse
import yaml
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_config(config_path: str) -> dict:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        Dictionary with configuration
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='ImgForge - Remove and replace image backgrounds',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default config
  python main.py
  
  # Use custom config file
  python main.py --config my_config.yaml
  
  # Override input/output folders
  python main.py --input ./my_images --output ./processed
  
  # Use custom background
  python main.py --background ./backgrounds/studio.jpg
        """
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    parser.add_argument(
        '--input',
        type=str,
        help='Input folder path (overrides config)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output folder path (overrides config)'
    )

    parser.add_argument(
        '--background',
        type=str,
        help='Background image path (overrides config)'
    )

    parser.add_argument(
        '--model',
        type=str,
        choices=['u2net', 'u2netp', 'u2net_human_seg', 'u2net_cloth_seg'],
        help='AI model to use for background removal (overrides config)'
    )

    parser.add_argument(
        '--quality',
        type=int,
        choices=range(1, 101),
        metavar='[1-100]',
        help='Output quality for JPEG/WEBP (1-100, overrides config)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )

    return parser.parse_args()


def validate_folders(config: dict) -> bool:
    """
    Validate that required folders and files exist.

    Args:
        config: Configuration dictionary

    Returns:
        True if valid, False otherwise
    """
    input_folder = config.get('input_folder')

    # Check input folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Input folder does not exist: {input_folder}")
        print(f"Please create the folder and add images to process.")
        return False

    # Check if input folder has images
    from src.utils import get_image_files
    image_files = get_image_files(input_folder)
    if not image_files:
        print(f"Error: No images found in input folder: {input_folder}")
        print(f"Supported formats: JPEG, PNG, WEBP, BMP")
        return False

    # Check background file if specified
    bg_path = config.get('default_background')
    if bg_path and not os.path.exists(bg_path):
        print(f"Warning: Background image not found: {bg_path}")
        print(f"Will use default gray background instead.")

    return True


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()

    # Load configuration
    if not os.path.exists(args.config):
        print(f"Error: Configuration file not found: {args.config}")
        print(f"Please create a config.yaml file or specify --config")
        sys.exit(1)

    config = load_config(args.config)

    # Override config with command line arguments
    if args.input:
        config['input_folder'] = args.input
    if args.output:
        config['output_folder'] = args.output
    if args.background:
        config['default_background'] = args.background
    if args.model:
        config['model'] = args.model
    if args.quality:
        config['output_quality'] = args.quality
    if args.verbose:
        config['log_level'] = 'DEBUG'

    # Setup logging
    setup_logging(
        config.get('log_file', './logs/processing.log'),
        config.get('log_level', 'INFO')
    )

    logging.info("="*60)
    logging.info("ImgForge v1.0")
    logging.info("="*60)

    # Validate configuration
    if not validate_folders(config):
        sys.exit(1)

    # Ensure output folder exists
    ensure_folder_exists(config['output_folder'])

    try:
        # Initialize processor
        processor = ImageProcessor(config)

        # Process images
        stats = processor.process_batch(
            config['input_folder'],
            config['output_folder']
        )

        # Cleanup
        processor.cleanup()

        # Exit with appropriate code
        if stats['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user.")
        logging.info("Processing interrupted by user")
        sys.exit(130)

    except Exception as e:
        print(f"\nError: {str(e)}")
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
