"""
Usage examples for biometric verification system.
Demonstrates library integration and API usage.
"""

import sys
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import crypto, embeddings, dna_codec, integrity, steganography
from pipeline.embedding_pipeline import EmbeddingPipeline
from pipeline.verification_pipeline import VerificationPipeline
from metrics import research_metrics
from bio_io import report_generator


def example_basic_encryption():
    """Example 1: Basic AES encryption and decryption."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic AES Encryption")
    print("="*70)
    
    # Generate key
    aes_key = crypto.generate_random_key()
    print(f"Generated AES-256 key: {aes_key.hex()[:32]}...")
    
    # Encrypt data
    plaintext = b"Sensitive biometric data"
    encrypted = crypto.encrypt_data(plaintext, aes_key)
    print(f"\nPlaintext: {plaintext}")
    print(f"Encrypted size: {len(encrypted)} bytes (original: {len(plaintext)} bytes)")
    
    # Decrypt data
    decrypted = crypto.decrypt_data(encrypted, aes_key)
    print(f"Decrypted: {decrypted}")
    
    assert plaintext == decrypted, "Encryption/decryption failed!"
    print("\n✓ Encryption/decryption successful")


def example_dna_encoding():
    """Example 2: DNA encoding and decoding."""
    print("\n" + "="*70)
    print("EXAMPLE 2: DNA Encoding")
    print("="*70)
    
    # Original data
    data = b"Bio"
    print(f"Original data: {data}")
    print(f"Original size: {len(data)} bytes")
    
    # Encode to DNA
    dna = dna_codec.bytes_to_dna(data)
    print(f"\nDNA sequence: {dna}")
    print(f"DNA length: {len(dna)} nucleotides")
    print(f"Expansion ratio: {len(dna) / len(data):.2f}x")
    
    # Get DNA statistics
    stats = dna_codec.get_dna_statistics(dna)
    print(f"\nDNA Statistics:")
    print(f"  A: {stats['nucleotide_counts']['A']}")
    print(f"  T: {stats['nucleotide_counts']['T']}")
    print(f"  G: {stats['nucleotide_counts']['G']}")
    print(f"  C: {stats['nucleotide_counts']['C']}")
    print(f"  GC-Content: {stats['gc_content']:.2%}")
    
    # Recover data
    recovered = dna_codec.dna_to_bytes(dna)
    print(f"\nRecovered data: {recovered}")
    
    assert data == recovered, "DNA encoding/decoding failed!"
    print("✓ DNA encoding/decoding successful")


def example_face_embedding():
    """Example 3: Face embedding extraction and processing."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Face Embedding")
    print("="*70)
    
    # Generate synthetic embedding (for demo without real face)
    embedding = embeddings.generate_synthetic_embedding(seed=42)
    print(f"Generated synthetic face embedding")
    print(f"Shape: {embedding.shape}")
    print(f"Values range: [{np.min(embedding):.4f}, {np.max(embedding):.4f}]")
    
    # Convert to bytes
    embedding_bytes = embeddings.embedding_to_bytes(embedding)
    print(f"\nEmbedding as bytes: {len(embedding_bytes)} bytes")
    
    # Hash embedding
    embedding_hash = integrity.generate_hash(embedding_bytes)
    print(f"SHA256 hash: {embedding_hash[:32]}...")
    
    # Recover embedding
    recovered_embedding = embeddings.bytes_to_embedding(embedding_bytes)
    
    # Compare
    distance = embeddings.compare_embeddings(embedding, recovered_embedding)
    print(f"\nDistance from original: {distance:.10f}")
    print("✓ Embedding recovery successful")


def example_full_pipeline():
    """Example 4: Full embedding and verification pipeline."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Full Embedding & Verification Pipeline")
    print("="*70)
    
    # For real usage, you would provide face and carrier images:
    # face_image_path = "face.jpg"
    # carrier_image_path = "carrier.png"
    # output_image_path = "stego_output.png"
    
    # For demo, we'll show the pipeline structure
    
    print("\nEmbedding Pipeline Stages:")
    print("1. Extract face embedding from image")
    print("2. Convert embedding to bytes (512 bytes)")
    print("3. Encrypt with AES-256 (adds 32-byte IV)")
    print("4. Encode encrypted data to DNA (4x expansion)")
    print("5. Create JSON payload with metadata")
    print("6. Hide payload in carrier image (LSB steganography)")
    print("\nVerification Pipeline Stages:")
    print("1. Extract hidden payload from stego image")
    print("2. Parse JSON payload and extract DNA sequence")
    print("3. Decode DNA to encrypted bytes")
    print("4. Decrypt with AES-256")
    print("5. Recover face embedding")
    print("6. Verify integrity hashes")
    print("7. Compare with original (optional)")
    
    print("\n✓ Pipeline structure explained")


def example_metrics():
    """Example 5: Research metrics and benchmarking."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Research Metrics")
    print("="*70)
    
    # Generate synthetic data
    embedding = embeddings.generate_synthetic_embedding()
    embedding_bytes = embeddings.embedding_to_bytes(embedding)
    
    # Encrypt
    aes_key = crypto.generate_random_key()
    encrypted_bytes = crypto.encrypt_data(embedding_bytes, aes_key)
    
    # DNA encode
    dna = dna_codec.bytes_to_dna(encrypted_bytes)
    
    # Compute payload statistics
    stats = research_metrics.compute_payload_statistics(
        embedding_bytes, encrypted_bytes, dna
    )
    
    print("\nPayload Transformation Statistics:")
    print(f"  Original size: {stats['original_size']} bytes")
    print(f"  Encrypted size: {stats['encrypted_size']} bytes")
    print(f"  Encryption overhead: {stats['encryption_overhead']} bytes "
          f"({stats['encryption_overhead_percent']:.1f}%)")
    print(f"  DNA length: {stats['dna_length']} nucleotides")
    print(f"  DNA expansion ratio: {stats['dna_expansion_ratio']:.2f}x")
    print(f"  Data entropy: {stats['entropy_bits']:.2f} bits/byte "
          f"({stats['entropy_percent']:.1f}% of theoretical max)")
    
    print("\n✓ Metrics computed successfully")


def example_key_derivation():
    """Example 6: Password-based key derivation."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Password-Based Key Derivation")
    print("="*70)
    
    password = "SecurePassword123!"
    
    # Derive key from password
    key, salt = crypto.derive_key_from_password(password)
    
    print(f"Password: {password}")
    print(f"Salt (hex): {salt.hex()}")
    print(f"Derived key (hex): {key.hex()}")
    
    # Same password and salt = same key
    key2, _ = crypto.derive_key_from_password(password, salt)
    
    assert key == key2, "Key derivation not reproducible!"
    print("\n✓ Key derivation successful and reproducible")


def example_integrity_validation():
    """Example 7: Integrity validation."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Integrity Validation")
    print("="*70)
    
    # Create validator
    validator = integrity.IntegrityValidator()
    
    # Register stage data
    data1 = b"stage1_data"
    data2 = b"stage2_data"
    
    hash1 = validator.register_stage('stage1', data1)
    hash2 = validator.register_stage('stage2', data2)
    
    print(f"Stage 1 hash: {hash1[:32]}...")
    print(f"Stage 2 hash: {hash2[:32]}...")
    
    # Verify stage
    validator.verify_stage('stage1', data1)
    print("\n✓ Stage 1 verified")
    
    validator.verify_stage('stage2', data2)
    print("✓ Stage 2 verified")
    
    # Try to verify wrong data
    try:
        validator.verify_stage('stage1', b"wrong_data")
        print("✗ Verification should have failed!")
    except integrity.IntegrityError:
        print("\n✓ Integrity check correctly detected tampering")


def main():
    """Run all examples."""
    print("\n" + "█"*70)
    print("█ Secure Biometric Identity Verification System - Usage Examples")
    print("█"*70)
    
    try:
        example_basic_encryption()
        example_dna_encoding()
        example_face_embedding()
        example_full_pipeline()
        example_metrics()
        example_key_derivation()
        example_integrity_validation()
        
        print("\n" + "█"*70)
        print("█ All examples completed successfully!")
        print("█"*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
