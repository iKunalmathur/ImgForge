"""
Main image processing pipeline that orchestrates background removal and replacement.
"""

import os
import time
import logging
from typing import Dict, List, Optional
from PIL import Image
from tqdm import tqdm
from colorama import Fore, Style, init as colorama_init

from .background_remover import BackgroundRemover
from .background_replacer import BackgroundReplacer
from .utils import (
    get_image_files,
    ensure_folder_exists,
    get_output_path,
    validate_image,
    format_time
)


class ImageProcessor:
    """
    Main processor that handles the complete pipeline of background removal and replacement.
    """

    def __init__(self, config: Dict):
        """
        Initialize the image processor with configuration.

        Args:
            config: Dictionary containing configuration options
        """
        self.config = config

        # Initialize colorama for colored output
        colorama_init(autoreset=True)

        # Initialize components
        self.remover = BackgroundRemover(
            model_name=config.get('model', 'u2net'))
        self.replacer = None

        # Load background if specified
        bg_path = config.get('default_background')
        if bg_path and os.path.exists(bg_path):
            self.replacer = BackgroundReplacer(bg_path)
            logging.info(f"Using background: {bg_path}")
        else:
            logging.warning(
                "No valid background image found. Will create default background.")
            self.replacer = BackgroundReplacer()

        # Processing statistics
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': 0,
            'end_time': 0
        }

    def _create_default_background(self, size: tuple) -> Image.Image:
        """
        Create a default gray background if no background image is provided.

        Args:
            size: (width, height) tuple

        Returns:
            PIL Image of default background
        """
        # Create a gradient gray background similar to the sample
        from PIL import ImageDraw

        background = Image.new('RGB', size, color=(200, 200, 200))
        draw = ImageDraw.Draw(background)

        # Add subtle gradient effect
        for y in range(size[1]):
            # Gradient from 180 to 220
            gray_val = int(180 + (y / size[1]) * 40)
            color = (gray_val, gray_val, gray_val)
            draw.line([(0, y), (size[0], y)], fill=color)

        return background

    def process_single_image(self, input_path: str, output_path: str) -> bool:
        """
        Process a single image through the pipeline.

        Args:
            input_path: Path to input image
            output_path: Path to save output image

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate input image
            if not validate_image(input_path):
                return False

            # Load original image to get dimensions
            original_image = Image.open(input_path)
            original_size = original_image.size
            original_format = original_image.format

            logging.info(
                f"Processing: {os.path.basename(input_path)} ({original_size[0]}x{original_size[1]})")

            # Step 1: Remove background
            subject_image = self.remover.remove_background(original_image)

            # Step 2: Prepare background
            if self.replacer.background_image is None:
                # Create default background if none provided
                default_bg = self._create_default_background(original_size)
                self.replacer.set_background(default_bg)

            # Step 3: Replace background
            output_image = self.replacer.replace_background(
                subject_image,
                target_size=original_size,
                center_subject=self.config.get('center_subject', True)
            )

            # Step 4: Add shadow if enabled
            if self.config.get('add_shadow', False):
                output_image = self.replacer.add_shadow(output_image)

            # Step 5: Convert to RGB for saving (if format doesn't support transparency)
            output_format = self.config.get('output_format', 'JPEG')
            if self.config.get('preserve_original_format', False):
                output_format = original_format or 'JPEG'

            if output_format.upper() in ['JPEG', 'JPG']:
                # JPEG doesn't support transparency, convert to RGB
                if output_image.mode == 'RGBA':
                    rgb_image = Image.new(
                        'RGB', output_image.size, (255, 255, 255))
                    rgb_image.paste(output_image, mask=output_image.split()[3])
                    output_image = rgb_image

            # Step 6: Save output image
            quality = self.config.get('output_quality', 95)
            if output_format.upper() in ['JPEG', 'JPG']:
                output_image.save(output_path, format='JPEG',
                                  quality=quality, optimize=True)
            elif output_format.upper() == 'PNG':
                output_image.save(output_path, format='PNG', optimize=True)
            elif output_format.upper() == 'WEBP':
                output_image.save(output_path, format='WEBP', quality=quality)
            else:
                output_image.save(output_path)

            logging.info(f"✓ Saved: {os.path.basename(output_path)}")
            return True

        except Exception as e:
            logging.error(
                f"✗ Failed to process {os.path.basename(input_path)}: {str(e)}")
            return False

    def process_batch(self, input_folder: str, output_folder: str) -> Dict:
        """
        Process all images in the input folder.

        Args:
            input_folder: Path to folder containing input images
            output_folder: Path to folder for output images

        Returns:
            Dictionary with processing statistics
        """
        # Ensure output folder exists
        ensure_folder_exists(output_folder)

        # Get list of image files
        image_files = get_image_files(input_folder)

        if not image_files:
            logging.warning(f"No images found in {input_folder}")
            return self.stats

        # Initialize stats
        self.stats['total'] = len(image_files)
        self.stats['start_time'] = time.time()

        # Print header
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}ImgForge")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
        print(f"Input folder:  {input_folder}")
        print(f"Output folder: {output_folder}")
        print(f"Found {len(image_files)} image(s) to process\n")

        # Process each image with progress bar
        for idx, input_path in enumerate(tqdm(image_files, desc="Processing", unit="image")):
            # Generate output path
            output_path = get_output_path(
                input_path,
                output_folder,
                self.config.get('output_format'),
                self.config.get('preserve_original_format', False),
                self.config.get('add_timestamp', False)
            )

            # Check if should skip existing
            if self.config.get('skip_existing', True) and os.path.exists(output_path):
                logging.info(
                    f"Skipping existing: {os.path.basename(output_path)}")
                self.stats['skipped'] += 1
                continue

            # Process image
            start_time = time.time()
            success = self.process_single_image(input_path, output_path)
            elapsed = time.time() - start_time

            if success:
                self.stats['successful'] += 1
                tqdm.write(
                    f"{Fore.GREEN}[{idx+1}/{len(image_files)}] ✓ {os.path.basename(input_path)} ({elapsed:.1f}s){Style.RESET_ALL}")
            else:
                self.stats['failed'] += 1
                tqdm.write(
                    f"{Fore.RED}[{idx+1}/{len(image_files)}] ✗ {os.path.basename(input_path)} (failed){Style.RESET_ALL}")

                # Stop if continue_on_error is False
                if not self.config.get('continue_on_error', True):
                    logging.error("Stopping batch processing due to error")
                    break

        # Finalize stats
        self.stats['end_time'] = time.time()
        total_time = self.stats['end_time'] - self.stats['start_time']

        # Print summary
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}Processing Complete!")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
        print(f"Total images:  {self.stats['total']}")
        print(
            f"{Fore.GREEN}Successful:    {self.stats['successful']}{Style.RESET_ALL}")

        if self.stats['failed'] > 0:
            print(
                f"{Fore.RED}Failed:        {self.stats['failed']}{Style.RESET_ALL}")

        if self.stats['skipped'] > 0:
            print(
                f"{Fore.YELLOW}Skipped:       {self.stats['skipped']}{Style.RESET_ALL}")

        print(f"Total time:    {format_time(total_time)}")

        if self.stats['successful'] > 0:
            avg_time = total_time / self.stats['successful']
            print(f"Average time:  {avg_time:.1f}s per image")

        print(
            f"\nOutput saved to: {Fore.CYAN}{output_folder}{Style.RESET_ALL}\n")

        return self.stats

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.remover:
            self.remover.cleanup()
        logging.debug("ImageProcessor cleanup complete")
