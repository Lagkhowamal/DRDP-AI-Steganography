"""
LSB steganography module for hiding encrypted payloads in images.
Core implementation with extensibility for DCT and AI-based steganography.
"""

import os
from stegano import lsb
from PIL import Image
import config


class SteganographyError(Exception):
    """Raised when steganography operations fail."""
    pass


def hide_payload(carrier_image_path: str, payload: str, output_image_path: str) -> dict:
    """
    Hide payload in carrier image using LSB steganography.
    
    Process:
    1. Load carrier image
    2. Embed payload in LSBs of pixel values
    3. Save stego image
    
    Args:
        carrier_image_path: Path to carrier image
        payload: String payload to hide
        output_image_path: Path for output stego image
    
    Returns:
        Dictionary with:
        - 'output_path': path to stego image
        - 'carrier_size': carrier image size in bytes
        - 'payload_size': payload size in bytes
        - 'capacity_used': percentage of image capacity used
    
    Raises:
        SteganographyError: If operation fails
    """
    if not isinstance(carrier_image_path, str):
        raise SteganographyError("Carrier image path must be string")
    
    if not isinstance(payload, str):
        raise SteganographyError("Payload must be string")
    
    if len(payload) == 0:
        raise SteganographyError("Payload cannot be empty")
    
    try:
        # Verify carrier image exists
        if not os.path.exists(carrier_image_path):
            raise SteganographyError(f"Carrier image not found: {carrier_image_path}")
        
        # Get carrier image size
        carrier_size = os.path.getsize(carrier_image_path)
        
        # Use stegano LSB to hide payload
        secret = lsb.hide(carrier_image_path, payload)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_image_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Save stego image
        secret.save(output_image_path)
        
        # Verify output was created
        if not os.path.exists(output_image_path):
            raise SteganographyError("Failed to create output stego image")
        
        stego_size = os.path.getsize(output_image_path)
        payload_size = len(payload.encode('utf-8'))
        
        # Calculate capacity
        # LSB in RGB: 1 bit per channel * 3 channels * pixels = 3 bits per pixel
        # For 8-bit depth, roughly can hide 0.375 bytes per pixel
        capacity_estimate = carrier_size * 0.375 / 8  # Very rough estimate
        capacity_used = (payload_size / capacity_estimate) * 100 if capacity_estimate > 0 else 0
        
        if config.VERBOSE_LOGGING:
            print(f"[STEGANOGRAPHY] Payload hidden in {output_image_path}")
            print(f"  Carrier size: {carrier_size} bytes")
            print(f"  Payload size: {payload_size} bytes")
            print(f"  Stego size: {stego_size} bytes")
        
        return {
            'output_path': output_image_path,
            'carrier_size': carrier_size,
            'payload_size': payload_size,
            'stego_size': stego_size,
            'capacity_used_percent': capacity_used,
        }
        
    except SteganographyError:
        raise
    except Exception as e:
        raise SteganographyError(f"Failed to hide payload: {str(e)}")


def extract_payload(stego_image_path: str) -> str:
    """
    Extract hidden payload from stego image.
    
    Args:
        stego_image_path: Path to stego image
    
    Returns:
        Extracted payload string
        
    Raises:
        SteganographyError: If operation fails
    """
    if not isinstance(stego_image_path, str):
        raise SteganographyError("Stego image path must be string")
    
    try:
        # Verify stego image exists
        if not os.path.exists(stego_image_path):
            raise SteganographyError(f"Stego image not found: {stego_image_path}")
        
        # Use stegano LSB to extract payload
        payload = lsb.reveal(stego_image_path)
        
        if payload is None:
            raise SteganographyError("No payload found in stego image")
        
        if not isinstance(payload, str):
            payload = payload.decode('utf-8')
        
        if len(payload) == 0:
            raise SteganographyError("Extracted payload is empty")
        
        if config.VERBOSE_LOGGING:
            print(f"[STEGANOGRAPHY] Payload extracted from {stego_image_path}")
            print(f"  Payload size: {len(payload)} characters")
        
        return payload
        
    except SteganographyError:
        raise
    except Exception as e:
        raise SteganographyError(f"Failed to extract payload: {str(e)}")


def get_image_capacity(image_path: str) -> int:
    """
    Estimate maximum payload size for given image.
    
    For LSB steganography:
    - Each pixel (RGB) can hide ~3 bits
    - Total capacity = (image_width * image_height * 3 * bit_depth) / 8 bytes
    
    Args:
        image_path: Path to image
    
    Returns:
        Estimated capacity in bytes
        
    Raises:
        SteganographyError: If image cannot be loaded
    """
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # RGB image: 3 channels, each can hide 1 bit per channel
        # Total: 3 bits per pixel per bit depth
        capacity_bits = width * height * 3
        capacity_bytes = capacity_bits // 8
        
        return capacity_bytes
        
    except Exception as e:
        raise SteganographyError(f"Failed to calculate capacity: {str(e)}")


def validate_payload_size(image_path: str, payload_size: int) -> bool:
    """
    Check if payload fits in image.
    
    Args:
        image_path: Path to carrier image
        payload_size: Size of payload in bytes
    
    Returns:
        True if payload fits, False otherwise
        
    Raises:
        SteganographyError: If validation fails
    """
    try:
        capacity = get_image_capacity(image_path)
        return payload_size <= capacity
    except Exception as e:
        raise SteganographyError(f"Failed to validate payload size: {str(e)}")


# Extensibility: Abstract steganography interface
class SteganographyProvider:
    """
    Abstract base for steganography methods.
    Allows swapping between LSB, DCT, and AI-based steganography.
    """
    
    def hide(self, carrier_image_path: str, payload: str, output_path: str) -> dict:
        """Hide payload in image."""
        raise NotImplementedError
    
    def extract(self, stego_image_path: str) -> str:
        """Extract payload from image."""
        raise NotImplementedError
    
    def get_capacity(self, image_path: str) -> int:
        """Get image capacity."""
        raise NotImplementedError


class LSBProvider(SteganographyProvider):
    """LSB steganography implementation."""
    
    def hide(self, carrier_image_path: str, payload: str, output_path: str) -> dict:
        return hide_payload(carrier_image_path, payload, output_path)
    
    def extract(self, stego_image_path: str) -> str:
        return extract_payload(stego_image_path)
    
    def get_capacity(self, image_path: str) -> int:
        return get_image_capacity(image_path)


# Future: DCT-based steganography for better imperceptibility
# class DCTProvider(SteganographyProvider):
#     """DCT steganography for JPEG images."""
#     pass
#
# class AIProvider(SteganographyProvider):
#     """AI-based generative steganography."""
#     pass
