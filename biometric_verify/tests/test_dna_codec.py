"""
Unit tests for DNA codec module.
Tests DNA encoding/decoding, statistics, and error handling.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import dna_codec


class TestDNACodec(unittest.TestCase):
    """Test DNA codec module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data = b"Test DNA encoding data for biometric system"
    
    def test_bytes_to_dna_roundtrip(self):
        """Test bytes to DNA and back."""
        dna = dna_codec.bytes_to_dna(self.test_data)
        recovered = dna_codec.dna_to_bytes(dna)
        self.assertEqual(self.test_data, recovered)
    
    def test_dna_contains_only_nucleotides(self):
        """Test DNA string contains only A, T, G, C."""
        dna = dna_codec.bytes_to_dna(self.test_data)
        self.assertTrue(all(c in 'ATGC' for c in dna))
    
    def test_dna_length_expansion(self):
        """Test DNA expansion ratio (4x)."""
        dna = dna_codec.bytes_to_dna(self.test_data)
        # 2 bits = 1 DNA nucleotide, so 8 bits (1 byte) = 4 nucleotides
        expected_length = len(self.test_data) * 4
        self.assertAlmostEqual(len(dna), expected_length, delta=1)
    
    def test_binary_to_dna(self):
        """Test binary to DNA conversion."""
        binary = "00011011"  # Even length
        dna = dna_codec.binary_to_dna(binary)
        self.assertEqual(len(dna), 4)  # 8 bits = 4 nucleotides
        
        # Verify mapping (00->A, 01->T, 10->G, 11->C)
        expected = "ATGC"
        self.assertEqual(dna, expected)

    def test_dna_to_binary(self):
        """Test DNA to binary conversion."""
        dna = "ATGC"
        binary = dna_codec.dna_to_binary(dna)
        self.assertEqual(binary, "00011011")

    def test_dna_statistics(self):
        """Test DNA statistics computation."""
        dna = "AAATTTGGGGCCCC"
        stats = dna_codec.get_dna_statistics(dna)
        
        self.assertEqual(stats['total_length'], 14)
        self.assertEqual(stats['nucleotide_counts']['A'], 3)
        self.assertEqual(stats['nucleotide_counts']['T'], 3)
        self.assertEqual(stats['nucleotide_counts']['G'], 4)
        self.assertEqual(stats['nucleotide_counts']['C'], 4)
        
        # GC-content = (G + C) / total
        expected_gc = 8 / 14
        self.assertAlmostEqual(stats['gc_content'], expected_gc)

    def test_invalid_binary_string(self):
        """Test error handling for invalid binary."""
        with self.assertRaises(dna_codec.DNACodecError):
            dna_codec.binary_to_dna("00102")  # Contains '2'

    def test_invalid_dna_string(self):
        """Test error handling for invalid DNA."""
        with self.assertRaises(dna_codec.DNACodecError):
            dna_codec.dna_to_binary("ATGX")  # Contains 'X'

    def test_odd_length_binary(self):
        """Test error handling for odd-length binary."""
        # This should NOT raise error (it's even)
        dna_codec.binary_to_dna("0001") 
        
        # This SHOULD raise error (odd length)
        with self.assertRaises(dna_codec.DNACodecError):
            dna_codec.binary_to_dna("000")
    
    def test_dna_codec_class(self):
        """Test DNACodec class."""
        codec = dna_codec.DNACodec()
        dna = codec.encode(self.test_data)
        recovered = codec.decode(dna)
        self.assertEqual(self.test_data, recovered)
    
    def test_validate_dna(self):
        """Test DNA validation."""
        codec = dna_codec.DNACodec()
        self.assertTrue(codec.validate_dna("ATGC"))
        self.assertFalse(codec.validate_dna("ATGX"))


if __name__ == '__main__':
    unittest.main()
