"""
Integrity verification and hashing module for biometric data.
Core implementation with extensibility for multiple hash algorithms.
"""

import hashlib
import config


class IntegrityError(Exception):
    """Raised when integrity verification fails."""
    pass


def generate_hash(data: bytes, algorithm: str = None) -> str:
    """
    Generate cryptographic hash of data.
    
    Args:
        data: Input bytes to hash
        algorithm: Hash algorithm (default: config.HASH_ALGORITHM)
    
    Returns:
        Hex-encoded hash string
        
    Raises:
        IntegrityError: If hashing fails
    """
    if algorithm is None:
        algorithm = config.HASH_ALGORITHM
    
    if not isinstance(data, bytes):
        raise IntegrityError("Data must be bytes")
    
    try:
        if algorithm == 'sha256':
            return hashlib.sha256(data).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data).hexdigest()
        elif algorithm == 'sha3_256':
            return hashlib.sha3_256(data).hexdigest()
        else:
            raise IntegrityError(f"Unsupported hash algorithm: {algorithm}")
    except Exception as e:
        raise IntegrityError(f"Hashing failed: {str(e)}")


def verify_hash(data: bytes, expected_hash: str, algorithm: str = None) -> bool:
    """
    Verify data against a known hash.
    
    Args:
        data: Input bytes to verify
        expected_hash: Expected hash value (hex string)
        algorithm: Hash algorithm (default: config.HASH_ALGORITHM)
    
    Returns:
        True if hash matches, False otherwise
        
    Raises:
        IntegrityError: If verification fails due to invalid input
    """
    if not isinstance(data, bytes):
        raise IntegrityError("Data must be bytes")
    
    if not isinstance(expected_hash, str):
        raise IntegrityError("Hash must be hex string")
    
    computed_hash = generate_hash(data, algorithm)
    
    # Use constant-time comparison to prevent timing attacks
    return computed_hash == expected_hash.lower()


def compute_hash_metadata(embedding_bytes: bytes, encrypted_bytes: bytes, 
                         dna_payload: str) -> dict:
    """
    Compute hashes for all stages of the pipeline.
    Useful for research analysis and integrity tracking.
    
    Args:
        embedding_bytes: Original face embedding
        encrypted_bytes: Encrypted embedding
        dna_payload: DNA-encoded payload
    
    Returns:
        Dictionary with hashes of each stage
    """
    return {
        'embedding_hash': generate_hash(embedding_bytes),
        'encrypted_hash': generate_hash(encrypted_bytes),
        'dna_hash': generate_hash(dna_payload.encode('utf-8')),
        'algorithm': config.HASH_ALGORITHM,
    }


def verify_integrity_chain(original_hash: str, computed_hash: str, 
                          stage_name: str = "Data") -> bool:
    """
    Verify integrity across transformation stages.
    
    Args:
        original_hash: Original hash value
        computed_hash: Recomputed hash after transformation
        stage_name: Name of stage for error messages
    
    Returns:
        True if hashes match
        
    Raises:
        IntegrityError: If verification fails
    """
    if original_hash != computed_hash:
        raise IntegrityError(
            f"Integrity check failed at stage '{stage_name}': "
            f"expected {original_hash}, got {computed_hash}"
        )
    return True


class IntegrityValidator:
    """
    Extensible integrity validation system.
    Supports multiple hash algorithms and verification methods.
    """
    
    def __init__(self, algorithm: str = None):
        """
        Initialize validator with chosen algorithm.
        
        Args:
            algorithm: Hash algorithm (default: config.HASH_ALGORITHM)
        """
        self.algorithm = algorithm if algorithm is not None else config.HASH_ALGORITHM
        self.hashes = {}  # Store computed hashes for verification
    
    def register_stage(self, stage_name: str, data: bytes) -> str:
        """
        Register data hash for a pipeline stage.
        
        Args:
            stage_name: Name of the stage
            data: Data to hash
        
        Returns:
            Hex hash of data
        """
        if not isinstance(data, bytes):
            raise IntegrityError(f"Stage '{stage_name}' data must be bytes")
        
        hash_value = generate_hash(data, self.algorithm)
        self.hashes[stage_name] = hash_value
        
        if config.VERBOSE_LOGGING:
            print(f"[INTEGRITY] {stage_name}: {hash_value[:16]}...")
        
        return hash_value
    
    def verify_stage(self, stage_name: str, data: bytes) -> bool:
        """
        Verify data against previously registered stage hash.
        
        Args:
            stage_name: Name of stage to verify
            data: Data to verify
        
        Returns:
            True if verification passes
            
        Raises:
            IntegrityError: If stage not registered or verification fails
        """
        if stage_name not in self.hashes:
            raise IntegrityError(f"Stage '{stage_name}' not registered")
        
        computed_hash = generate_hash(data, self.algorithm)
        expected_hash = self.hashes[stage_name]
        
        if computed_hash != expected_hash:
            raise IntegrityError(
                f"Integrity verification failed for stage '{stage_name}'"
            )
        
        return True
    
    def get_report(self) -> dict:
        """Get full integrity report."""
        return {
            'algorithm': self.algorithm,
            'stages': self.hashes,
            'total_stages': len(self.hashes),
        }


# Future: HMAC-based integrity for message authentication
def compute_hmac(data: bytes, key: bytes, algorithm: str = 'sha256') -> str:
    """
    Compute HMAC for authenticated encryption.
    Extensibility hook for future authenticated encryption schemes.
    
    Args:
        data: Data to authenticate
        key: Secret key
        algorithm: HMAC algorithm
    
    Returns:
        HMAC hex string
    """
    import hmac
    
    if algorithm == 'sha256':
        return hmac.new(key, data, hashlib.sha256).hexdigest()
    else:
        raise IntegrityError(f"Unsupported HMAC algorithm: {algorithm}")
