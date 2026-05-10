"""
Unit tests for cryptography module.
Tests AES encryption/decryption, key derivation, and error handling.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import crypto


class TestCrypto(unittest.TestCase):
    """Test cryptography module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.key = crypto.generate_random_key()
        self.plaintext = b"Hello, this is a test message for encryption!"
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test encryption and decryption round-trip."""
        encrypted = crypto.encrypt_data(self.plaintext, self.key)
        decrypted = crypto.decrypt_data(encrypted, self.key)
        self.assertEqual(self.plaintext, decrypted)
    
    def test_encrypt_adds_iv(self):
        """Test that IV is included in ciphertext."""
        encrypted = crypto.encrypt_data(self.plaintext, self.key)
        # IV is first 16 bytes
        self.assertGreaterEqual(len(encrypted), 16)
    
    def test_padding(self):
        """Test PKCS7 padding."""
        # Test various data sizes
        for size in [1, 15, 16, 17, 32, 100]:
            data = b'X' * size
            padded = crypto.pad(data)
            self.assertEqual(len(padded) % 16, 0)
            unpadded = crypto.unpad(padded)
            self.assertEqual(data, unpadded)
    
    def test_invalid_key_size(self):
        """Test error handling for invalid key size."""
        short_key = b"short"
        with self.assertRaises(crypto.CryptographyError):
            crypto.encrypt_data(self.plaintext, short_key)
    
    def test_decrypt_with_wrong_key(self):
        """Test decryption with wrong key fails."""
        encrypted = crypto.encrypt_data(self.plaintext, self.key)
        wrong_key = crypto.generate_random_key()
        
        # Decryption might not fail, but won't recover plaintext
        try:
            decrypted = crypto.decrypt_data(encrypted, wrong_key)
            self.assertNotEqual(self.plaintext, decrypted)
        except crypto.CryptographyError:
            pass  # Expected
    
    def test_generate_random_key(self):
        """Test random key generation."""
        key1 = crypto.generate_random_key()
        key2 = crypto.generate_random_key()
        
        self.assertEqual(len(key1), 32)
        self.assertEqual(len(key2), 32)
        self.assertNotEqual(key1, key2)  # Should be different
    
    def test_key_derivation(self):
        """Test key derivation from password."""
        password = "test_password_123"
        key1, salt1 = crypto.derive_key_from_password(password)
        key2, salt2 = crypto.derive_key_from_password(password, salt1)
        
        self.assertEqual(len(key1), 32)
        self.assertEqual(len(key2), 32)
        self.assertEqual(key1, key2)  # Same password and salt
        self.assertEqual(salt1, salt2)
    
    def test_invalid_data_type(self):
        """Test error handling for invalid data types."""
        with self.assertRaises(crypto.CryptographyError):
            crypto.encrypt_data("not bytes", self.key)


if __name__ == '__main__':
    unittest.main()
