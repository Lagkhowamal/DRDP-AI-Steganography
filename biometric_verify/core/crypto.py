"""
AES-256 encryption and decryption module for biometric data.
Core implementation with extensibility for post-quantum cryptography.
"""

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import config


class CryptographyError(Exception):
    """Raised when encryption/decryption operations fail."""
    pass


def pad(data: bytes, block_size: int = 16) -> bytes:
    """
    Apply PKCS7 padding to data.
    
    Args:
        data: Input bytes to pad
        block_size: Block size for padding (default 16 for AES)
    
    Returns:
        Padded bytes
        
    Raises:
        CryptographyError: If data is None or invalid type
    """
    if not isinstance(data, bytes):
        raise CryptographyError("Data must be bytes")
    
    padding_length = block_size - (len(data) % block_size)
    padding = bytes([padding_length]) * padding_length
    return data + padding


def unpad(data: bytes) -> bytes:
    """
    Remove PKCS7 padding from data.
    
    Args:
        data: Padded bytes
    
    Returns:
        Unpadded bytes
        
    Raises:
        CryptographyError: If padding is invalid
    """
    if not isinstance(data, bytes) or len(data) == 0:
        raise CryptographyError("Data must be non-empty bytes")
    
    padding_length = data[-1]
    
    # Validate padding
    if padding_length == 0 or padding_length > 16:
        raise CryptographyError(f"Invalid padding length: {padding_length}")
    
    for i in range(padding_length):
        if data[-(i + 1)] != padding_length:
            raise CryptographyError("Invalid padding bytes detected")
    
    return data[:-padding_length]


def encrypt_data(data: bytes, key: bytes) -> bytes:
    """
    Encrypt data using AES-256-CBC.
    
    Args:
        data: Input plaintext bytes
        key: AES key (must be 32 bytes for AES-256)
    
    Returns:
        IV (16 bytes) + Ciphertext (bytes)
        
    Raises:
        CryptographyError: If key size is incorrect or encryption fails
    """
    if not isinstance(data, bytes):
        raise CryptographyError("Data must be bytes")
    
    if not isinstance(key, bytes):
        raise CryptographyError("Key must be bytes")
    
    if len(key) != config.AES_KEY_SIZE:
        raise CryptographyError(
            f"AES key must be {config.AES_KEY_SIZE} bytes, "
            f"got {len(key)} bytes"
        )
    
    try:
        # Pad data to block size
        padded_data = pad(data)
        
        # Create AES cipher in CBC mode
        cipher = AES.new(key, AES.MODE_CBC)
        
        # Encrypt
        ciphertext = cipher.encrypt(padded_data)
        
        # Return IV + ciphertext
        return cipher.iv + ciphertext
        
    except Exception as e:
        raise CryptographyError(f"Encryption failed: {str(e)}")


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """
    Decrypt data encrypted with AES-256-CBC.
    
    Args:
        encrypted_data: IV (16 bytes) + Ciphertext (bytes)
        key: AES key (must be 32 bytes for AES-256)
    
    Returns:
        Plaintext bytes
        
    Raises:
        CryptographyError: If decryption fails or data format is invalid
    """
    if not isinstance(encrypted_data, bytes):
        raise CryptographyError("Encrypted data must be bytes")
    
    if len(encrypted_data) < 16:
        raise CryptographyError("Encrypted data too short (must contain IV + ciphertext)")
    
    if not isinstance(key, bytes):
        raise CryptographyError("Key must be bytes")
    
    if len(key) != config.AES_KEY_SIZE:
        raise CryptographyError(
            f"AES key must be {config.AES_KEY_SIZE} bytes, "
            f"got {len(key)} bytes"
        )
    
    try:
        # Extract IV and ciphertext
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        if len(ciphertext) == 0:
            raise CryptographyError("No ciphertext provided")
        
        # Create AES cipher for decryption
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Decrypt
        padded_plaintext = cipher.decrypt(ciphertext)
        
        # Remove padding
        plaintext = unpad(padded_plaintext)
        
        return plaintext
        
    except CryptographyError:
        raise
    except Exception as e:
        raise CryptographyError(f"Decryption failed: {str(e)}")


def generate_random_key(key_size: int = None) -> bytes:
    """
    Generate a cryptographically secure random key.
    
    Args:
        key_size: Key size in bytes (default: config.AES_KEY_SIZE)
    
    Returns:
        Random key bytes
    """
    if key_size is None:
        key_size = config.AES_KEY_SIZE
    
    if key_size <= 0:
        raise CryptographyError("Key size must be positive")
    
    return get_random_bytes(key_size)


def derive_key_from_password(password: str, salt: bytes = None, 
                             key_size: int = None, iterations: int = 100000) -> tuple:
    """
    Derive an AES key from a password using PBKDF2.
    
    Useful for password-based encryption.
    Extensibility hook for future key derivation methods (e.g., quantum-safe).
    
    Args:
        password: Password string
        salt: Random salt (if None, generates new one)
        key_size: Output key size in bytes (default: config.AES_KEY_SIZE)
        iterations: PBKDF2 iterations for security
    
    Returns:
        Tuple of (key_bytes, salt_bytes)
        
    Raises:
        CryptographyError: If derivation fails
    """
    if key_size is None:
        key_size = config.AES_KEY_SIZE
    
    try:
        if salt is None:
            salt = get_random_bytes(16)
        
        if isinstance(password, str):
            password = password.encode('utf-8')
        
        # PBKDF2 with SHA256
        key = PBKDF2(password, salt, key_size, count=iterations, hmac_hash_module=None)
        
        return key, salt
        
    except Exception as e:
        raise CryptographyError(f"Key derivation failed: {str(e)}")


# Extensibility class for future crypto algorithms
class CryptoProvider:
    """
    Abstract base for encryption providers.
    Allows swapping between AES, PQC (Kyber), and other algorithms.
    """
    
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        """Encrypt data."""
        raise NotImplementedError
    
    def decrypt(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt data."""
        raise NotImplementedError


class AESProvider(CryptoProvider):
    """AES-256-CBC implementation."""
    
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        return encrypt_data(data, key)
    
    def decrypt(self, encrypted_data: bytes, key: bytes) -> bytes:
        return decrypt_data(encrypted_data, key)


# Future: KyberProvider for post-quantum cryptography
# class KyberProvider(CryptoProvider):
#     """Kyber-1024 implementation for post-quantum security."""
#     def __init__(self):
#         # Initialize Kyber library
#         pass
