"""
Image I/O and validation module.
Handles loading, saving, and validating images with error handling.
"""

import os
from PIL import Image
import cv2
import numpy as np
import config


class ImageIOError(Exception):
    """Raised when image I/O operations fail."""
    pass


def load_image(image_path: str) -> Image.Image:
    """
    Load image from file with validation.
    
    Args:
        image_path: Path to image file
    
    Returns:
        PIL Image object
        
    Raises:
        ImageIOError: If file not found, invalid format, or corrupted
    """
    if not isinstance(image_path, str):
        raise ImageIOError("Image path must be string")
    
    # Validate file exists
    if not os.path.exists(image_path):
        raise ImageIOError(f"Image file not found: {image_path}")
    
    # Validate extension
    _, ext = os.path.splitext(image_path)
    ext = ext.lower().lstrip('.')
    
    if ext not in config.SUPPORTED_IMAGE_FORMATS:
        raise ImageIOError(
            f"Unsupported format: {ext}. "
            f"Supported: {', '.join(config.SUPPORTED_IMAGE_FORMATS)}"
        )
    
    try:
        # Try loading with PIL
        img = Image.open(image_path)
        
        # Verify image is readable by loading pixel data
        img.load()
        
        if config.VERBOSE_LOGGING:
            print(f"[IMAGE] Loaded {ext.upper()} image: {image_path}")
            print(f"  Size: {img.size}, Mode: {img.mode}")
        
        return img
        
    except Exception as e:
        raise ImageIOError(f"Failed to load image {image_path}: {str(e)}")


def load_image_cv2(image_path: str) -> np.ndarray:
    """
    Load image using OpenCV.
    
    Args:
        image_path: Path to image file
    
    Returns:
        NumPy array (BGR format)
        
    Raises:
        ImageIOError: If image cannot be loaded
    """
    try:
        img = cv2.imread(image_path)
        
        if img is None:
            raise ImageIOError(f"Failed to load image: {image_path}")
        
        return img
        
    except Exception as e:
        raise ImageIOError(f"OpenCV image loading failed: {str(e)}")


def save_image(image: Image.Image, output_path: str, quality: int = None) -> str:
    """
    Save PIL Image to file.
    
    Args:
        image: PIL Image object
        output_path: Path for output file
        quality: JPEG quality (0-100, default: config.JPEG_QUALITY)
    
    Returns:
        Path to saved image
        
    Raises:
        ImageIOError: If save operation fails
    """
    if not isinstance(image, Image.Image):
        raise ImageIOError("Image must be PIL Image object")
    
    if not isinstance(output_path, str):
        raise ImageIOError("Output path must be string")
    
    if quality is None:
        quality = config.JPEG_QUALITY
    
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Get file extension
        _, ext = os.path.splitext(output_path)
        ext = ext.lower().lstrip('.')
        
        # Save with appropriate parameters
        if ext in ['jpg', 'jpeg']:
            image.save(output_path, 'JPEG', quality=quality)
        elif ext == 'png':
            image.save(output_path, 'PNG', compress_level=config.PNG_COMPRESSION)
        elif ext == 'bmp':
            image.save(output_path, 'BMP')
        else:
            # Default: try with PIL's default format detection
            image.save(output_path, quality=quality)
        
        if config.VERBOSE_LOGGING:
            print(f"[IMAGE] Saved image to {output_path}")
        
        return output_path
        
    except Exception as e:
        raise ImageIOError(f"Failed to save image: {str(e)}")


def validate_image_format(image_path: str) -> bool:
    """
    Validate that image is readable and not corrupted.
    
    Args:
        image_path: Path to image file
    
    Returns:
        True if valid, False otherwise
    """
    try:
        img = Image.open(image_path)
        img.verify()
        return True
    except Exception:
        return False


def get_image_info(image_path: str) -> dict:
    """
    Get detailed image information.
    
    Args:
        image_path: Path to image file
    
    Returns:
        Dictionary with image metadata
    """
    try:
        img = load_image(image_path)
        file_size = os.path.getsize(image_path)
        
        return {
            'path': image_path,
            'filename': os.path.basename(image_path),
            'file_size_bytes': file_size,
            'format': img.format,
            'mode': img.mode,
            'size_pixels': img.size,
            'width': img.size[0],
            'height': img.size[1],
            'file_extension': os.path.splitext(image_path)[1].lower(),
        }
        
    except Exception as e:
        raise ImageIOError(f"Failed to get image info: {str(e)}")


def resize_image(image: Image.Image, size: tuple) -> Image.Image:
    """
    Resize PIL Image.
    
    Args:
        image: PIL Image object
        size: Target size (width, height)
    
    Returns:
        Resized image
    """
    if not isinstance(image, Image.Image):
        raise ImageIOError("Image must be PIL Image object")
    
    try:
        return image.resize(size, Image.Resampling.LANCZOS)
    except Exception as e:
        raise ImageIOError(f"Image resizing failed: {str(e)}")


def convert_image_format(input_path: str, output_path: str) -> str:
    """
    Convert image to different format.
    
    Args:
        input_path: Path to source image
        output_path: Path for converted image
    
    Returns:
        Path to converted image
    """
    try:
        img = load_image(input_path)
        
        # Convert RGBA to RGB if saving as JPEG
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        
        return save_image(img, output_path)
        
    except Exception as e:
        raise ImageIOError(f"Format conversion failed: {str(e)}")


def crop_image(image: Image.Image, box: tuple) -> Image.Image:
    """
    Crop image region.
    
    Args:
        image: PIL Image object
        box: Crop box (left, upper, right, lower)
    
    Returns:
        Cropped image
    """
    try:
        return image.crop(box)
    except Exception as e:
        raise ImageIOError(f"Image cropping failed: {str(e)}")
