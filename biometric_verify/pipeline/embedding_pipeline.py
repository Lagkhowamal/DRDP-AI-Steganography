"""
Embedding pipeline: orchestrates face extraction → encryption → DNA encoding → steganography.
Core implementation for secure biometric verification.
"""

import time
import json
from datetime import datetime
import numpy as np
import config
from core import embeddings, crypto, dna_codec, integrity, steganography
from bio_io import image_handler


class EmbeddingPipelineError(Exception):
    """Raised when pipeline operations fail."""
    pass


class EmbeddingPipeline:
    """
    Complete encoding pipeline for biometric security.
    
    Process:
    1. Extract face embedding from image
    2. Convert embedding to bytes
    3. Encrypt bytes using AES-256
    4. Encode encrypted data to DNA sequence
    5. Create JSON payload with DNA and metadata
    6. Hide JSON payload in carrier image using LSB steganography
    """
    
    def __init__(self, aes_key: bytes = None, verbose: bool = True):
        """
        Initialize embedding pipeline.
        
        Args:
            aes_key: AES encryption key (32 bytes). If None, generates random key.
            verbose: Enable verbose logging
        """
        self.verbose = verbose or config.VERBOSE_LOGGING
        
        if aes_key is None:
            aes_key = crypto.generate_random_key()
            if self.verbose:
                print("[PIPELINE] Generated random AES key")
        
        if not isinstance(aes_key, bytes) or len(aes_key) != config.AES_KEY_SIZE:
            raise EmbeddingPipelineError(
                f"AES key must be {config.AES_KEY_SIZE} bytes"
            )
        
        self.aes_key = aes_key
        self.integrity_validator = integrity.IntegrityValidator()
        self.metadata = {}
    
    def run(self, face_image_path: str, carrier_image_path: str, 
            output_stego_path: str) -> dict:
        """
        Execute full embedding pipeline.
        
        Args:
            face_image_path: Path to face image
            carrier_image_path: Path to carrier image
            output_stego_path: Path for output stego image
        
        Returns:
            Dictionary with:
            - 'success': True if pipeline completed
            - 'embedding_bytes': original embedding bytes
            - 'encrypted_bytes': encrypted embedding
            - 'dna_payload': DNA-encoded payload
            - 'json_payload': full JSON payload
            - 'stego_image_path': output stego image path
            - 'metrics': timing and size metrics
            - 'hashes': integrity hashes
        
        Raises:
            EmbeddingPipelineError: If any stage fails
        """
        try:
            start_time = time.time()
            
            # Stage 1: Extract embedding
            if self.verbose:
                print("\n[STAGE 1] Extracting face embedding...")
            
            stage_start = time.time()
            embedding_array = embeddings.extract_face_embedding(face_image_path)
            embedding_bytes = embeddings.embedding_to_bytes(embedding_array)
            
            stage_time = time.time() - stage_start
            
            if self.verbose:
                print(f"  ✓ Extracted 128-D embedding ({len(embedding_bytes)} bytes)")
                print(f"    Time: {stage_time:.4f}s")
            
            # Register for integrity tracking
            embedding_hash = self.integrity_validator.register_stage(
                'embedding', embedding_bytes
            )
            
            # Stage 2: Encrypt embedding
            if self.verbose:
                print("\n[STAGE 2] Encrypting embedding with AES-256...")
            
            stage_start = time.time()
            encrypted_bytes = crypto.encrypt_data(embedding_bytes, self.aes_key)
            stage_time = time.time() - stage_start
            
            if self.verbose:
                print(f"  ✓ Encrypted payload ({len(encrypted_bytes)} bytes)")
                print(f"    Encryption overhead: {len(encrypted_bytes) - len(embedding_bytes)} bytes (IV + padding)")
                print(f"    Time: {stage_time:.4f}s")
            
            # Register for integrity tracking
            encrypted_hash = self.integrity_validator.register_stage(
                'encrypted', encrypted_bytes
            )
            
            # Stage 3: DNA encoding
            if self.verbose:
                print("\n[STAGE 3] DNA encoding...")
            
            stage_start = time.time()
            dna_payload = dna_codec.bytes_to_dna(encrypted_bytes)
            dna_stats = dna_codec.get_dna_statistics(dna_payload)
            stage_time = time.time() - stage_start
            
            if self.verbose:
                print(f"  ✓ DNA sequence generated ({len(dna_payload)} nucleotides)")
                print(f"    Expansion ratio: {len(dna_payload) / len(encrypted_bytes):.2f}x")
                print(f"    GC-content: {dna_stats['gc_content']:.2%}")
                print(f"    Time: {stage_time:.4f}s")
            
            # Register for integrity tracking
            dna_hash = self.integrity_validator.register_stage(
                'dna', dna_payload.encode('utf-8')
            )
            
            # Stage 4: Create JSON payload
            if self.verbose:
                print("\n[STAGE 4] Creating steganographic payload...")
            
            payload_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'algorithm': 'AES-256-CBC + DNA',
                'dna': dna_payload,
                'hashes': {
                    'embedding': embedding_hash,
                    'encrypted': encrypted_hash,
                    'dna': dna_hash,
                },
                'metadata': {
                    'embedding_shape': [128],
                    'embedding_dtype': 'float32',
                    'dna_length': len(dna_payload),
                    'dna_stats': dna_stats,
                },
            }
            
            json_payload = json.dumps(payload_data)
            payload_size = len(json_payload.encode('utf-8'))
            
            if self.verbose:
                print(f"  ✓ JSON payload created ({payload_size} bytes)")
                print(f"    Time: <1ms")
            
            # Stage 5: Steganography
            if self.verbose:
                print("\n[STAGE 5] Hiding payload in carrier image...")
            
            stage_start = time.time()
            stego_result = steganography.hide_payload(
                carrier_image_path, json_payload, output_stego_path
            )
            stage_time = time.time() - stage_start
            
            if self.verbose:
                print(f"  ✓ Payload hidden in stego image")
                print(f"    Stego image: {output_stego_path}")
                print(f"    Capacity used: {stego_result['capacity_used_percent']:.2f}%")
                print(f"    Time: {stage_time:.4f}s")
            
            # Compute overall metrics
            total_time = time.time() - start_time
            
            result = {
                'success': True,
                'embedding_bytes': embedding_bytes,
                'embedding_array': embedding_array,
                'encrypted_bytes': encrypted_bytes,
                'dna_payload': dna_payload,
                'json_payload': payload_data,
                'stego_image_path': output_stego_path,
                'metrics': {
                    'embedding_size': len(embedding_bytes),
                    'encrypted_size': len(encrypted_bytes),
                    'dna_length': len(dna_payload),
                    'payload_size': payload_size,
                    'encryption_overhead': len(encrypted_bytes) - len(embedding_bytes),
                    'dna_expansion_ratio': len(dna_payload) / len(encrypted_bytes),
                    'total_time': total_time,
                    'stego_result': stego_result,
                },
                'hashes': {
                    'embedding': embedding_hash,
                    'encrypted': encrypted_hash,
                    'dna': dna_hash,
                },
                'dna_stats': dna_stats,
            }
            
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"[SUCCESS] Embedding pipeline completed in {total_time:.4f}s")
                print(f"{'='*60}\n")
            
            return result
            
        except Exception as e:
            error_msg = f"Pipeline failed: {str(e)}"
            if self.verbose:
                print(f"\n[ERROR] {error_msg}\n")
            raise EmbeddingPipelineError(error_msg)
    
    def get_integrity_report(self) -> dict:
        """Get integrity verification report."""
        return self.integrity_validator.get_report()
