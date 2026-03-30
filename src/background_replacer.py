"""
Background replacement module for compositing subjects onto new backgrounds.
"""

import logging
from typing import Tuple, Optional
from PIL import Image
import numpy as np
import cv2


class BackgroundReplacer:
    """
    Handles replacing backgrounds in images while maintaining quality.
    """
    
    def __init__(self, background_image_path: Optional[str] = None):
        """
        Initialize the background replacer.
        
        Args:
            background_image_path: Path to the background image
        """
        self.background_image_path = background_image_path
        self.background_image = None
        
        if background_image_path:
            self._load_background(background_image_path)
    
    def _load_background(self, background_path: str) -> None:
        """
        Load background image from file.
        
        Args:
            background_path: Path to background image
        """
        try:
            self.background_image = Image.open(background_path)
            logging.info(f"Loaded background image: {background_path} (size: {self.background_image.size})")
        except Exception as e:
            logging.error(f"Failed to load background image: {str(e)}")
            raise
    
    def set_background(self, background_image: Image.Image) -> None:
        """
        Set background image directly.
        
        Args:
            background_image: PIL Image to use as background
        """
        self.background_image = background_image
        logging.debug(f"Background set (size: {background_image.size})")
    
    def _resize_background(self, target_size: Tuple[int, int]) -> Image.Image:
        """
        Resize background to match target dimensions.
        
        Args:
            target_size: (width, height) tuple
        
        Returns:
            Resized background image
        """
        if self.background_image is None:
            raise ValueError("No background image loaded")
        
        # Get current and target dimensions
        bg_width, bg_height = self.background_image.size
        target_width, target_height = target_size
        
        # Calculate scaling to cover the entire target area
        scale = max(target_width / bg_width, target_height / bg_height)
        
        # Resize background
        new_width = int(bg_width * scale)
        new_height = int(bg_height * scale)
        resized_bg = self.background_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Crop to exact target size (center crop)
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        cropped_bg = resized_bg.crop((left, top, right, bottom))
        
        return cropped_bg
    
    def replace_background(self, subject_image: Image.Image, 
                          target_size: Optional[Tuple[int, int]] = None,
                          center_subject: bool = True) -> Image.Image:
        """
        Replace background of subject image with the loaded background.
        
        Args:
            subject_image: PIL Image with transparent background (RGBA)
            target_size: Target output size (width, height). If None, uses subject size
            center_subject: If True, centers the subject on the background
        
        Returns:
            PIL Image with new background
        """
        try:
            # Ensure subject has alpha channel
            if subject_image.mode != 'RGBA':
                subject_image = subject_image.convert('RGBA')
            
            # Determine target size
            if target_size is None:
                target_size = subject_image.size
            
            # Resize background to match target size
            background = self._resize_background(target_size)
            
            # Convert background to RGBA
            if background.mode != 'RGBA':
                background = background.convert('RGBA')
            
            # Resize subject if needed while maintaining aspect ratio
            if subject_image.size != target_size:
                subject_image = subject_image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Create output image
            output = Image.new('RGBA', target_size)
            output.paste(background, (0, 0))
            
            # Composite subject onto background using alpha channel
            output = Image.alpha_composite(output, subject_image)
            
            logging.debug(f"Background replaced successfully, output size: {output.size}")
            
            return output
            
        except Exception as e:
            logging.error(f"Error replacing background: {str(e)}")
            raise
    
    def add_shadow(self, image: Image.Image, shadow_opacity: float = 0.3) -> Image.Image:
        """
        Add a simple shadow effect under the subject (experimental).
        
        Args:
            image: PIL Image with subject on background
            shadow_opacity: Opacity of the shadow (0.0 to 1.0)
        
        Returns:
            PIL Image with shadow added
        """
        try:
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Create shadow layer (simplified version)
            shadow = np.zeros_like(img_array)
            shadow[:, :, 3] = (img_array[:, :, 3] * shadow_opacity).astype(np.uint8)
            
            # Offset shadow slightly down
            shadow_offset = 10
            shadow = np.roll(shadow, shadow_offset, axis=0)
            
            # Composite shadow with original
            shadow_img = Image.fromarray(shadow)
            output = Image.alpha_composite(shadow_img.convert('RGBA'), image.convert('RGBA'))
            
            logging.debug("Shadow effect applied")
            return output
            
        except Exception as e:
            logging.warning(f"Could not add shadow: {str(e)}")
            return image  # Return original if shadow fails
