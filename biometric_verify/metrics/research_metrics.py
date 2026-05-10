"""
Metrics and benchmarking module for technical documentation.
Computes PSNR, SSIM, payload statistics, and timing benchmarks.
"""

import time
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
import config


class MetricsError(Exception):
    """Raised when metrics computation fails."""
    pass


def calculate_psnr(original_image_path: str, stego_image_path: str) -> float:
    """
    Calculate Peak Signal-to-Noise Ratio (PSNR) between original and stego image.
    
    PSNR = 20 * log10(MAX_PIXEL / sqrt(MSE))
    
    Where MAX_PIXEL = 255 for 8-bit images.
    
    Typical values:
    - PSNR > 40 dB: imperceptible difference
    - 30-40 dB: acceptable quality
    - < 30 dB: visible distortion
    
    Args:
        original_image_path: Path to original carrier image
        stego_image_path: Path to stego image
    
    Returns:
        PSNR in decibels (dB)
        
    Raises:
        MetricsError: If images cannot be loaded or have different dimensions
    """
    try:
        # Load images
        original = cv2.imread(original_image_path)
        stego = cv2.imread(stego_image_path)
        
        if original is None:
            raise MetricsError(f"Cannot load original image: {original_image_path}")
        
        if stego is None:
            raise MetricsError(f"Cannot load stego image: {stego_image_path}")
        
        # Ensure same dimensions
        if original.shape != stego.shape:
            raise MetricsError(
                f"Image dimensions mismatch: "
                f"original {original.shape}, stego {stego.shape}"
            )
        
        # Convert to float32 for calculations
        original_f = original.astype(np.float32)
        stego_f = stego.astype(np.float32)
        
        # Calculate MSE (Mean Squared Error)
        mse = np.mean((original_f - stego_f) ** 2)
        
        # Handle zero MSE (identical images)
        if mse == 0:
            return 100.0  # Infinite PSNR represented as 100 dB
        
        # Calculate PSNR
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        
        return float(psnr)
        
    except MetricsError:
        raise
    except Exception as e:
        raise MetricsError(f"PSNR calculation failed: {str(e)}")


def calculate_ssim(original_image_path: str, stego_image_path: str) -> float:
    """
    Calculate Structural Similarity Index (SSIM) between images.
    
    SSIM measures perceived image quality considering luminance, contrast, and structure.
    
    Range: -1 to 1
    - 1.0: identical images
    - 0.0: no structural similarity
    - < 0.0: negative correlation
    
    Typical values for good steganography: > 0.95
    
    Args:
        original_image_path: Path to original carrier image
        stego_image_path: Path to stego image
    
    Returns:
        SSIM score (0-1)
        
    Raises:
        MetricsError: If images cannot be loaded
    """
    try:
        # Load images
        original = cv2.imread(original_image_path)
        stego = cv2.imread(stego_image_path)
        
        if original is None or stego is None:
            raise MetricsError("Cannot load images")
        
        # Convert to grayscale for SSIM calculation
        original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        stego_gray = cv2.cvtColor(stego, cv2.COLOR_BGR2GRAY)
        
        # Calculate SSIM
        ssim_value = ssim(original_gray, stego_gray)
        
        return float(ssim_value)
        
    except MetricsError:
        raise
    except Exception as e:
        raise MetricsError(f"SSIM calculation failed: {str(e)}")


def compute_payload_statistics(embedding_bytes: bytes, encrypted_bytes: bytes, 
                               dna_payload: str) -> dict:
    """
    Compute payload transformation statistics for research.
    
    Tracks size changes across transformation pipeline:
    1. Original embedding (128 float32 values)
    2. Encrypted with AES (adds IV + padding)
    3. DNA encoded (2 bits → 1 nucleotide)
    
    Args:
        embedding_bytes: Original embedding bytes
        encrypted_bytes: AES-encrypted bytes
        dna_payload: DNA-encoded sequence
    
    Returns:
        Dictionary with statistics:
        - original_size: embedding size
        - encrypted_size: encrypted size
        - encryption_overhead: added bytes
        - dna_length: nucleotide count
        - compression_ratio: DNA expansion
        - entropy: Shannon entropy of encrypted data
    """
    try:
        original_size = len(embedding_bytes)
        encrypted_size = len(encrypted_bytes)
        dna_length = len(dna_payload)
        
        # Compute encryption overhead (IV + padding)
        encryption_overhead = encrypted_size - original_size
        
        # Compute DNA expansion ratio
        # Theoretically: 1 byte (8 bits) → 4 DNA nucleotides
        dna_expansion_ratio = dna_length / encrypted_size if encrypted_size > 0 else 0
        
        # Compute entropy of encrypted data
        # Shannon entropy H = -Σ(p_i * log2(p_i))
        unique, counts = np.unique(np.frombuffer(encrypted_bytes, dtype=np.uint8), 
                                   return_counts=True)
        probabilities = counts / len(encrypted_bytes)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        return {
            'original_size': original_size,
            'encrypted_size': encrypted_size,
            'dna_length': dna_length,
            'encryption_overhead': encryption_overhead,
            'encryption_overhead_percent': (encryption_overhead / original_size) * 100,
            'dna_expansion_ratio': dna_expansion_ratio,
            'entropy_bits': float(entropy),
            'entropy_percent': (entropy / 8.0) * 100,  # Percentage of theoretical maximum
        }
        
    except Exception as e:
        raise MetricsError(f"Payload statistics computation failed: {str(e)}")


class BenchmarkSuite:
    """
    Comprehensive benchmarking suite for research performance analysis.
    Measures timing of each pipeline stage across multiple iterations.
    """
    
    def __init__(self, iterations: int = None):
        """
        Initialize benchmark suite.
        
        Args:
            iterations: Number of iterations (default: config.BENCHMARK_ITERATIONS)
        """
        self.iterations = iterations if iterations is not None else config.BENCHMARK_ITERATIONS
        self.results = {}  # stage_name -> list of times
        self.metadata = {}  # metadata for runs
    
    def benchmark_function(self, func, func_name: str, *args, **kwargs) -> dict:
        """
        Benchmark a function over multiple iterations.
        
        Args:
            func: Function to benchmark
            func_name: Name for benchmark results
            *args, **kwargs: Arguments for function
        
        Returns:
            Dictionary with timing statistics
        """
        times = []
        
        for _ in range(self.iterations):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                raise MetricsError(f"Benchmark of {func_name} failed: {str(e)}")
            end = time.perf_counter()
            
            elapsed = (end - start) * 1000  # Convert to milliseconds
            times.append(elapsed)
        
        # Compute statistics
        times_array = np.array(times)
        stats = {
            'function': func_name,
            'iterations': self.iterations,
            'mean_time_ms': float(np.mean(times_array)),
            'std_time_ms': float(np.std(times_array)),
            'min_time_ms': float(np.min(times_array)),
            'max_time_ms': float(np.max(times_array)),
            'median_time_ms': float(np.median(times_array)),
            'times_ms': times,  # Raw timings for detailed analysis
        }
        
        self.results[func_name] = stats
        
        return stats
    
    def get_summary(self) -> dict:
        """Get benchmark summary for all tested functions."""
        summary = {}
        
        for func_name, stats in self.results.items():
            summary[func_name] = {
                'mean_time_ms': stats['mean_time_ms'],
                'std_time_ms': stats['std_time_ms'],
                'min_time_ms': stats['min_time_ms'],
                'max_time_ms': stats['max_time_ms'],
            }
        
        return summary
    
    def get_full_report(self) -> dict:
        """Get complete benchmark report with all details."""
        return {
            'iterations': self.iterations,
            'results': self.results,
            'summary': self.get_summary(),
        }


def compute_image_statistics(image_path: str) -> dict:
    """
    Compute image statistics (entropy, histogram, etc.).
    Useful for steganography quality assessment.
    
    Args:
        image_path: Path to image
    
    Returns:
        Dictionary with image statistics
    """
    try:
        import os
        
        # File size statistics
        file_size = os.path.getsize(image_path)
        
        # Load image
        image = cv2.imread(image_path)
        
        if image is None:
            raise MetricsError(f"Cannot load image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Compute entropy
        unique, counts = np.unique(gray.flatten(), return_counts=True)
        probabilities = counts / gray.size
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        # Compute histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        
        return {
            'file_size_bytes': file_size,
            'image_shape': image.shape,
            'image_size_pixels': image.shape[0] * image.shape[1],
            'entropy': float(entropy),
            'mean_pixel_value': float(np.mean(gray)),
            'std_pixel_value': float(np.std(gray)),
            'min_pixel_value': float(np.min(gray)),
            'max_pixel_value': float(np.max(gray)),
        }
        
    except Exception as e:
        raise MetricsError(f"Image statistics computation failed: {str(e)}")


# Extensibility: Custom metric providers
class MetricProvider:
    """Abstract base for custom metrics implementations."""
    
    def compute_metric(self, *args, **kwargs) -> float:
        """Compute metric value."""
        raise NotImplementedError
