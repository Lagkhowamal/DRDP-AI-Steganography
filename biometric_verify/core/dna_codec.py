"""
DNA encoding and decoding module for steganographic payload.
Converts binary data to DNA nucleotide sequences and vice versa.
Core implementation with extensibility for variable encodings.
"""

import config


class DNACodecError(Exception):
    """Raised when DNA codec operations fail."""
    pass


def binary_to_dna(binary_string: str, mapping: dict = None) -> str:
    """
    Convert binary string to DNA sequence using configurable mapping.
    
    Args:
        binary_string: Binary string (e.g., '0011010101')
        mapping: DNA mapping dict (default: config.DNA_MAPPING)
    
    Returns:
        DNA string (e.g., 'ATGC')
        
    Raises:
        DNACodecError: If binary string is invalid or incomplete
    """
    if mapping is None:
        mapping = config.DNA_MAPPING
    
    if not isinstance(binary_string, str):
        raise DNACodecError("Binary string must be str")
    
    # Validate binary string
    if not all(c in '01' for c in binary_string):
        raise DNACodecError("Binary string must contain only 0 and 1")
    
    if len(binary_string) % 2 != 0:
        raise DNACodecError("Binary string length must be even (pairs of bits)")
    
    dna = ''
    try:
        for i in range(0, len(binary_string), 2):
            bits = binary_string[i:i+2]
            dna += mapping[bits]
    except KeyError as e:
        raise DNACodecError(f"Invalid mapping for bits {bits}")
    
    return dna


def dna_to_binary(dna_string: str, reverse_mapping: dict = None) -> str:
    """
    Convert DNA sequence back to binary string.
    
    Args:
        dna_string: DNA sequence (e.g., 'ATGC')
        reverse_mapping: Reverse DNA mapping (default: config.REVERSE_DNA_MAPPING)
    
    Returns:
        Binary string (e.g., '0011010101')
        
    Raises:
        DNACodecError: If DNA string is invalid
    """
    if reverse_mapping is None:
        reverse_mapping = config.REVERSE_DNA_MAPPING
    
    if not isinstance(dna_string, str):
        raise DNACodecError("DNA string must be str")
    
    # Validate DNA string
    valid_nucleotides = set('ATGC')
    if not all(c in valid_nucleotides for c in dna_string):
        raise DNACodecError("DNA string must contain only A, T, G, C")
    
    binary = ''
    try:
        for char in dna_string:
            binary += reverse_mapping[char]
    except KeyError as e:
        raise DNACodecError(f"Invalid nucleotide: {char}")
    
    return binary


def bytes_to_dna(data_bytes: bytes, mapping: dict = None) -> str:
    """
    Convert bytes to DNA sequence.
    
    Process:
    1. Convert each byte to 8-bit binary
    2. Group bits into pairs
    3. Map pairs to DNA nucleotides
    
    Args:
        data_bytes: Input bytes
        mapping: DNA mapping (default: config.DNA_MAPPING)
    
    Returns:
        DNA string
        
    Raises:
        DNACodecError: If data is invalid
    """
    if not isinstance(data_bytes, bytes):
        raise DNACodecError("Input must be bytes")
    
    if len(data_bytes) == 0:
        raise DNACodecError("Input bytes cannot be empty")
    
    # Convert bytes to binary string
    binary = ''.join(format(byte, '08b') for byte in data_bytes)
    
    # Pad to even length if necessary
    if len(binary) % 2 != 0:
        binary += '0'
    
    # Convert binary to DNA
    return binary_to_dna(binary, mapping)


def dna_to_bytes(dna_string: str, reverse_mapping: dict = None) -> bytes:
    """
    Convert DNA sequence back to bytes.
    
    Process:
    1. Map DNA nucleotides to bit pairs
    2. Group bits into 8-bit chunks
    3. Convert to bytes
    
    Args:
        dna_string: DNA sequence
        reverse_mapping: Reverse DNA mapping
    
    Returns:
        Reconstructed bytes
        
    Raises:
        DNACodecError: If DNA string is invalid
    """
    if not isinstance(dna_string, str):
        raise DNACodecError("DNA string must be str")
    
    if len(dna_string) == 0:
        raise DNACodecError("DNA string cannot be empty")
    
    # Convert DNA to binary
    binary = dna_to_binary(dna_string, reverse_mapping)
    
    # Convert binary to bytes
    byte_array = bytearray()
    
    for i in range(0, len(binary), 8):
        byte_bits = binary[i:i+8]
        
        # Only process complete bytes
        if len(byte_bits) == 8:
            byte_array.append(int(byte_bits, 2))
    
    return bytes(byte_array)


def get_dna_statistics(dna_string: str) -> dict:
    """
    Compute statistics about DNA sequence.
    Useful for research metrics and analysis.
    
    Args:
        dna_string: DNA sequence
    
    Returns:
        Dictionary with nucleotide counts and ratios
    """
    if not isinstance(dna_string, str):
        raise DNACodecError("DNA string must be str")
    
    total = len(dna_string)
    
    if total == 0:
        raise DNACodecError("DNA string cannot be empty")
    
    counts = {
        'A': dna_string.count('A'),
        'T': dna_string.count('T'),
        'G': dna_string.count('G'),
        'C': dna_string.count('C')
    }
    
    ratios = {nt: counts[nt] / total for nt in 'ATGC'}
    
    return {
        'total_length': total,
        'nucleotide_counts': counts,
        'nucleotide_ratios': ratios,
        'gc_content': (counts['G'] + counts['C']) / total,  # GC-content is important in genomics
    }


# Extensibility: Support alternative DNA encodings for research
class DNACodec:
    """
    Configurable DNA codec with support for different encoding schemes.
    Allows research into optimal DNA encodings for steganography.
    """
    
    def __init__(self, mapping: dict = None):
        """
        Initialize codec with custom mapping.
        
        Args:
            mapping: Custom DNA bit-to-nucleotide mapping
        """
        self.mapping = mapping if mapping is not None else config.DNA_MAPPING
        self.reverse_mapping = {v: k for k, v in self.mapping.items()}
    
    def encode(self, data_bytes: bytes) -> str:
        """Encode bytes to DNA."""
        return bytes_to_dna(data_bytes, self.mapping)
    
    def decode(self, dna_string: str) -> bytes:
        """Decode DNA to bytes."""
        return dna_to_bytes(dna_string, self.reverse_mapping)
    
    def validate_dna(self, dna_string: str) -> bool:
        """Check if DNA string is valid."""
        try:
            dna_to_binary(dna_string, self.reverse_mapping)
            return True
        except DNACodecError:
            return False
