"""
Verification pipeline: extracts and recovers encrypted biometric data from stego images.
Core implementation for integrity verification and authentication.
"""

import time
import json
import numpy as np
import config
from core import crypto, dna_codec, integrity, steganography, embeddings


class VerificationPipelineError(Exception):
    """Raised when verification operations fail."""
    pass


class VerificationPipeline:
    """
    Complete decoding and verification pipeline.
    
    Process:
    1. Extract hidden payload from stego image
    2. Parse JSON payload and extract DNA sequence
    3. Decode DNA sequence back to encrypted bytes
    4. Decrypt bytes using AES-256 to recover embedding
    5. Verify integrity of recovered data
    6. Compare with original embedding (if provided)
    """
    
    def __init__(self, aes_key: bytes, verbose: bool = True):
        """
        Initialize verification pipeline.
        
        Args:
            aes_key: AES decryption key (32 bytes)
            verbose: Enable verbose logging
        """
        self.verbose = verbose or config.VERBOSE_LOGGING
        
        if not isinstance(aes_key, bytes) or len(aes_key) != config.AES_KEY_SIZE:
            raise VerificationPipelineError(
                f"AES key must be {config.AES_KEY_SIZE} bytes"
            )
        
        self.aes_key = aes_key
    
    def run(self, stego_image_path: str, original_embedding: np.ndarray = None) -> dict:
        """
        Execute full verification pipeline.
        
        Args:
            stego_image_path: Path to stego image
            original_embedding: Optional original embedding for comparison
        
        Returns:
            Dictionary with:
            - 'success': True if verification passed
            - 'recovered_embedding': reconstructed embedding
            - 'integrity_verified': boolean
            - 'embedding_distance': distance from original (if provided)
            - 'metrics': timing and comparison metrics
            - 'payload': extracted JSON payload
        
        Raises:
            VerificationPipelineError: If verification fails
        """
        try:
            start_time = time.time()
            
            # Stage 1: Extract payload from stego image
            if self.verbose:
                print("\n[STAGE 1] Extracting payload from stego image...")
            
            stage_start = time.time()
            json_payload_str = steganography.extract_payload(stego_image_path)
            stage_time = time.time() - stage_start
            
            if self.verbose:
                print(f"  ✓ Payload extracted ({len(json_payload_str)} bytes)")
                print(f"    Time: {stage_time:.4f}s")
            
            # Parse JSON
            try:
                json_payload = json.loads(json_payload_str)
            except json.JSONDecodeError as e:
                raise VerificationPipelineError(f"Invalid JSON payload: {str(e)}")
            
            # Stage 2: Extract DNA sequence
            if self.verbose:
                print("\n[STAGE 2] Extracting DNA sequence...")
            
            if 'dna' not in json_payload:
                raise VerificationPipelineError("No DNA sequence in payload")
            
            dna_payload = json_payload['dna']
            
            if self.verbose:
                print(f"  ✓ DNA sequence extracted ({len(dna_payload)} nucleotides)")
            
            # Stage 3: DNA decoding
            if self.verbose:
                print("\n[STAGE 3] DNA decoding...")
            
            stage_start = time.time()
            recovered_encrypted_bytes = dna_codec.dna_to_bytes(dna_payload)
            stage_time = time.time() - stage_start
            
            if self.verbose:
                print(f"  ✓ Decrypted to encrypted bytes ({len(recovered_encrypted_bytes)} bytes)")
                print(f"    Time: {stage_time:.4f}s")
            
            # Stage 4: Decryption
            if self.verbose:
                print("\n[STAGE 4] Decrypting with AES-256...")
            
            stage_start = time.time()
            recovered_embedding_bytes = crypto.decrypt_data(
                recovered_encrypted_bytes, self.aes_key
            )
            stage_time = time.time() - stage_start
            
            if self.verbose:
                print(f"  ✓ Decrypted embedding ({len(recovered_embedding_bytes)} bytes)")
                print(f"    Time: {stage_time:.4f}s")
            
            # Stage 5: Reconstruct embedding
            if self.verbose:
                print("\n[STAGE 5] Reconstructing embedding...")
            
            recovered_embedding = embeddings.bytes_to_embedding(recovered_embedding_bytes)
            
            if self.verbose:
                print(f"  ✓ Embedding reconstructed (shape: {recovered_embedding.shape})")
            
            # Stage 6: Integrity verification
            if self.verbose:
                print("\n[STAGE 6] Verifying integrity...")
            
            integrity_verified = True
            integrity_errors = []
            
            # Check stored hashes
            if 'hashes' in json_payload:
                stored_hashes = json_payload['hashes']
                
                # Verify embedding hash
                if 'embedding' in stored_hashes:
                    try:
                        computed_hash = integrity.generate_hash(recovered_embedding_bytes)
                        if computed_hash != stored_hashes['embedding']:
                            integrity_verified = False
                            integrity_errors.append(
                                f"Embedding hash mismatch: "
                                f"stored={stored_hashes['embedding'][:16]}..., "
                                f"computed={computed_hash[:16]}..."
                            )
                        else:
                            if self.verbose:
                                print(f"  ✓ Embedding hash verified")
                    except Exception as e:
                        integrity_verified = False
                        integrity_errors.append(f"Embedding hash verification failed: {str(e)}")
                
                # Verify DNA hash
                if 'dna' in stored_hashes:
                    try:
                        computed_dna_hash = integrity.generate_hash(dna_payload.encode('utf-8'))
                        if computed_dna_hash != stored_hashes['dna']:
                            integrity_verified = False
                            integrity_errors.append("DNA hash mismatch")
                        else:
                            if self.verbose:
                                print(f"  ✓ DNA hash verified")
                    except Exception as e:
                        integrity_verified = False
                        integrity_errors.append(f"DNA hash verification failed: {str(e)}")
            
            # Stage 7: Optional comparison with original
            embedding_distance = None
            comparison_successful = False
            
            if original_embedding is not None:
                if self.verbose:
                    print("\n[STAGE 7] Comparing with original embedding...")
                
                try:
                    embedding_distance = embeddings.compare_embeddings(
                        original_embedding, recovered_embedding
                    )
                    comparison_successful = True
                    
                    if self.verbose:
                        print(f"  ✓ Euclidean distance: {embedding_distance:.6f}")
                        
                        # Threshold for face recognition (typically 0.5-0.6)
                        if embedding_distance < 0.5:
                            print(f"    → Embeddings match (distance < 0.5)")
                        else:
                            print(f"    → Embeddings differ (distance >= 0.5)")
                except Exception as e:
                    if self.verbose:
                        print(f"  [WARNING] Comparison failed: {str(e)}")
            
            # Compute overall metrics
            total_time = time.time() - start_time
            
            result = {
                'success': integrity_verified,
                'recovered_embedding': recovered_embedding,
                'recovered_embedding_bytes': recovered_embedding_bytes,
                'integrity_verified': integrity_verified,
                'integrity_errors': integrity_errors,
                'embedding_distance': embedding_distance,
                'comparison_successful': comparison_successful,
                'metrics': {
                    'recovered_embedding_size': len(recovered_embedding_bytes),
                    'dna_length': len(dna_payload),
                    'encryption_overhead': len(recovered_encrypted_bytes) - len(recovered_embedding_bytes),
                    'total_time': total_time,
                },
                'payload': json_payload,
            }
            
            if self.verbose:
                status = "✓ PASSED" if integrity_verified else "✗ FAILED"
                print(f"\n{'='*60}")
                print(f"[VERIFICATION] {status}")
                print(f"Integrity verified: {integrity_verified}")
                if embedding_distance is not None:
                    print(f"Embedding distance: {embedding_distance:.6f}")
                print(f"Total time: {total_time:.4f}s")
                print(f"{'='*60}\n")
            
            return result
            
        except Exception as e:
            error_msg = f"Verification pipeline failed: {str(e)}"
            if self.verbose:
                print(f"\n[ERROR] {error_msg}\n")
            raise VerificationPipelineError(error_msg)
