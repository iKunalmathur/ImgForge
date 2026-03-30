"""
Background removal module using AI-based segmentation.
"""

import logging
from typing import Optional
from PIL import Image
import numpy as np
from rembg import remove, new_session


class BackgroundRemover:
    """
    Handles background removal from images using AI models.
    """
    
    def __init__(self, model_name: str = "u2net"):
        """
        Initialize the background remover with specified model.
        
        Args:
            model_name: Name of the model to use
                       Options: u2net, u2netp, u2net_human_seg, u2net_cloth_seg
        """
        self.model_name = model_name
        self.session = None
        logging.info(f"Initializing BackgroundRemover with model: {model_name}")
        
    def _load_model(self) -> None:
        """Load the AI model (lazy loading)."""
        if self.session is None:
            logging.info(f"Loading model '{self.model_name}'... This may take a moment on first run.")
            try:
                self.session = new_session(self.model_name)
                logging.info("Model loaded successfully")
            except Exception as e:
                logging.error(f"Failed to load model: {str(e)}")
                raise
    
    def remove_background(self, input_image: Image.Image) -> Image.Image:
        """
        Remove background from an image.
        
        Args:
            input_image: PIL Image object
        
        Returns:
            PIL Image with transparent background (RGBA mode)
        """
        try:
            # Lazy load the model
            self._load_model()
            
            # Convert to RGB if necessary
            if input_image.mode != 'RGB':
                input_image = input_image.convert('RGB')
            
            # Remove background
            logging.debug(f"Removing background from image of size {input_image.size}")
            output_image = remove(input_image, session=self.session)
            
            # Ensure output is in RGBA mode
            if output_image.mode != 'RGBA':
                output_image = output_image.convert('RGBA')
            
            return output_image
            
        except Exception as e:
            logging.error(f"Error removing background: {str(e)}")
            raise
    
    def remove_background_from_file(self, input_path: str, output_path: Optional[str] = None) -> Image.Image:
        """
        Remove background from an image file.
        
        Args:
            input_path: Path to input image
            output_path: Optional path to save output (if None, doesn't save)
        
        Returns:
            PIL Image with transparent background
        """
        try:
            # Load image
            logging.debug(f"Loading image: {input_path}")
            input_image = Image.open(input_path)
            
            # Remove background
            output_image = self.remove_background(input_image)
            
            # Save if output path provided
            if output_path:
                output_image.save(output_path, format='PNG')
                logging.debug(f"Saved output to: {output_path}")
            
            return output_image
            
        except Exception as e:
            logging.error(f"Error processing file {input_path}: {str(e)}")
            raise
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.session = None
        logging.debug("BackgroundRemover resources cleaned up")
