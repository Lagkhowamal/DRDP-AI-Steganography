"""
Face embedding extraction module using face_recognition library.
Core implementation with extensibility for multiple embedding models.
"""

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False

import numpy as np
import config


class EmbeddingError(Exception):
    """Raised when face detection or embedding extraction fails."""
    pass


def extract_face_embedding(image_path: str) -> np.ndarray:
    """
    Extract face embedding from image file.
    
    Uses face_recognition library to:
    1. Load image
    2. Detect faces
    3. Extract 128-dimensional embedding for first face
    
    Args:
        image_path: Path to image file (jpg, png, etc.)
    
    Returns:
        128-dimensional numpy array (face embedding)
        
    Raises:
        EmbeddingError: If file not found, image invalid, or no face detected
    """
    if not FACE_RECOGNITION_AVAILABLE:
        if config.USE_SYNTHETIC_EMBEDDINGS_FOR_TESTING:
            if config.VERBOSE_LOGGING:
                print("[WARNING] face_recognition not available. "
                      "Generating synthetic embedding for testing.")
            return generate_synthetic_embedding()
        
        raise EmbeddingError(
            "face_recognition library not installed. "
            "To install: pip install face-recognition dlib\n"
            "Windows users: See requirements.txt for dlib installation help.\n"
            "Alternatively: Set USE_SYNTHETIC_EMBEDDINGS_FOR_TESTING = True in config.py"
        )
    
    if not isinstance(image_path, str):
        raise EmbeddingError("Image path must be string")
    
    try:
        # Load image
        image = face_recognition.load_image_file(image_path)
    except FileNotFoundError:
        raise EmbeddingError(f"Image file not found: {image_path}")
    except Exception as e:
        raise EmbeddingError(f"Failed to load image: {str(e)}")
    
    try:
        # Detect faces and extract encodings
        encodings = face_recognition.face_encodings(
            image,
            num_jitters=1,  # Single pass for speed (research demo)
            model='small'   # Faster model for research
        )
    except Exception as e:
        raise EmbeddingError(f"Face detection failed: {str(e)}")
    
    # Validate detection results
    if len(encodings) == 0:
        raise EmbeddingError(
            "No face detected in image. Ensure image contains a clear, "
            "frontal face."
        )
    
    if len(encodings) > 1:
        if config.VERBOSE_LOGGING:
            print(f"[WARNING] Multiple faces detected ({len(encodings)}). "
                  "Using first face.")
    
    # Return first embedding as numpy array
    embedding = encodings[0]
    
    if not isinstance(embedding, np.ndarray):
        embedding = np.array(embedding)
    
    if embedding.shape != (128,):
        raise EmbeddingError(
            f"Unexpected embedding shape: {embedding.shape} "
            "(expected (128,))"
        )
    
    return embedding


def extract_face_embedding_with_metadata(image_path: str) -> dict:
    """
    Extract face embedding with additional metadata.
    
    Args:
        image_path: Path to image file
    
    Returns:
        Dictionary with:
        - 'embedding': numpy array
        - 'embedding_bytes': bytes representation
        - 'shape': embedding shape
        - 'dtype': data type
        - 'min_value', 'max_value': range statistics
    """
    embedding = extract_face_embedding(image_path)
    
    return {
        'embedding': embedding,
        'embedding_bytes': embedding.astype(np.float32).tobytes(),
        'shape': embedding.shape,
        'dtype': str(embedding.dtype),
        'min_value': float(np.min(embedding)),
        'max_value': float(np.max(embedding)),
        'mean_value': float(np.mean(embedding)),
        'std_value': float(np.std(embedding)),
    }


def embedding_to_bytes(embedding: np.ndarray) -> bytes:
    """
    Convert embedding numpy array to bytes.
    
    Args:
        embedding: Face embedding array
    
    Returns:
        Bytes representation (float32)
    """
    if not isinstance(embedding, np.ndarray):
        raise EmbeddingError("Embedding must be numpy array")
    
    if embedding.shape != (128,):
        raise EmbeddingError(f"Expected shape (128,), got {embedding.shape}")
    
    return embedding.astype(np.float32).tobytes()


def bytes_to_embedding(data: bytes) -> np.ndarray:
    """
    Reconstruct embedding from bytes.
    
    Args:
        data: Bytes representation of embedding
    
    Returns:
        Reconstructed numpy array
        
    Raises:
        EmbeddingError: If data size is incorrect
    """
    if not isinstance(data, bytes):
        raise EmbeddingError("Data must be bytes")
    
    expected_size = 128 * 4  # 128 float32 values
    
    if len(data) != expected_size:
        raise EmbeddingError(
            f"Expected {expected_size} bytes, got {len(data)}"
        )
    
    try:
        embedding = np.frombuffer(data, dtype=np.float32)
        return embedding
    except Exception as e:
        raise EmbeddingError(f"Failed to reconstruct embedding: {str(e)}")


def generate_synthetic_embedding(seed: int = None) -> np.ndarray:
    """
    Generate synthetic face embedding for testing.
    
    Useful for unit tests and demos without real face images.
    Values are drawn from normal distribution (typical face embedding distribution).
    
    Args:
        seed: Random seed for reproducibility
    
    Returns:
        128-dimensional synthetic embedding
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Face embeddings typically follow standard normal distribution
    # with mean ~0.1 and std ~1.0
    synthetic = np.random.normal(0.1, 0.1, 128)
    
    return synthetic.astype(np.float32)


def compare_embeddings(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Compare two embeddings using Euclidean distance.
    
    Args:
        embedding1: First embedding
        embedding2: Second embedding
    
    Returns:
        Euclidean distance (0 = identical, ~0.6 = different person)
    """
    if not isinstance(embedding1, np.ndarray) or not isinstance(embedding2, np.ndarray):
        raise EmbeddingError("Both inputs must be numpy arrays")
    
    if embedding1.shape != (128,) or embedding2.shape != (128,):
        raise EmbeddingError("Both embeddings must have shape (128,)")
    
    distance = np.linalg.norm(embedding1 - embedding2)
    return float(distance)


# Extensibility: Support multiple embedding models
class EmbeddingExtractor:
    """
    Configurable embedding extractor supporting multiple face recognition models.
    Allows research into different embedding techniques.
    """
    
    def __init__(self, model: str = 'small'):
        """
        Initialize extractor with chosen model.
        
        Args:
            model: 'small' (fast, research) or 'cnn' (slower, more accurate)
        """
        self.model = model
        if model not in ['small', 'cnn']:
            raise EmbeddingError(f"Unsupported model: {model}")
    
    def extract(self, image_path: str) -> np.ndarray:
        """Extract embedding using configured model."""
        image = face_recognition.load_image_file(image_path)
        
        encodings = face_recognition.face_encodings(
            image,
            num_jitters=1,
            model=self.model
        )
        
        if len(encodings) == 0:
            raise EmbeddingError("No face detected")
        
        return encodings[0]


# Future: Support for other embedding models
# class DeepFaceExtractor:
#     """DeepFace embedding extractor for research comparison."""
#     pass
#
# class VGGFaceExtractor:
#     """VGGFace embedding extractor."""
#     pass
