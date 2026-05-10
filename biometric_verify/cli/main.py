"""
Command-line interface for biometric verification system.
Provides CLI commands for embedding, verification, and benchmarking.
"""

import argparse
import sys
import os
import json
from datetime import datetime
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core import crypto, embeddings
from pipeline.embedding_pipeline import EmbeddingPipeline
from pipeline.verification_pipeline import VerificationPipeline
from metrics import research_metrics
from bio_io import image_handler, report_generator


class CLI:
    """Command-line interface for biometric verification."""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with all commands."""
        parser = argparse.ArgumentParser(
            description='Secure Biometric Identity Verification System',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Examples:
  # Embed biometric in carrier image
  %(prog)s embed face.jpg carrier.png output_stego.png
  
  # Verify stego image
  %(prog)s verify output_stego.png --key-file key.bin
  
  # Run benchmarks
  %(prog)s benchmark face.jpg carrier.png --iterations 10
  
  # Generate synthetic embedding
  %(prog)s gen-embedding --output embedding.bin
            '''
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Command to execute')
        
        # Embed command
        embed_parser = subparsers.add_parser('embed', help='Embed biometric in image')
        embed_parser.add_argument('face_image', help='Path to face image')
        embed_parser.add_argument('carrier_image', help='Path to carrier image')
        embed_parser.add_argument('output_image', help='Path for output stego image')
        embed_parser.add_argument('--key-file', help='Save AES key to file')
        embed_parser.add_argument('--report', help='Save JSON report to file')
        embed_parser.set_defaults(func=self.cmd_embed)
        
        # Verify command
        verify_parser = subparsers.add_parser('verify', help='Verify stego image')
        verify_parser.add_argument('stego_image', help='Path to stego image')
        verify_parser.add_argument('--key-file', help='Path to AES key file')
        verify_parser.add_argument('--key-hex', help='AES key as hex string')
        verify_parser.add_argument('--report', help='Save JSON report to file')
        verify_parser.set_defaults(func=self.cmd_verify)
        
        # Benchmark command
        benchmark_parser = subparsers.add_parser('benchmark', help='Run benchmarks')
        benchmark_parser.add_argument('face_image', help='Path to face image')
        benchmark_parser.add_argument('carrier_image', help='Path to carrier image')
        benchmark_parser.add_argument('--iterations', type=int, 
                                     default=config.BENCHMARK_ITERATIONS,
                                     help='Number of iterations')
        benchmark_parser.add_argument('--csv', help='Save results to CSV file')
        benchmark_parser.set_defaults(func=self.cmd_benchmark)
        
        # Generate embedding command
        gen_parser = subparsers.add_parser('gen-embedding', 
                                           help='Generate synthetic embedding')
        gen_parser.add_argument('--output', help='Save embedding to file')
        gen_parser.add_argument('--seed', type=int, help='Random seed')
        gen_parser.set_defaults(func=self.cmd_gen_embedding)
        
        return parser
    
    def cmd_embed(self, args):
        """Execute embed command."""
        try:
            print("\n[CLI] Biometric Embedding Pipeline")
            print("=" * 60)
            
            # Validate inputs
            if not os.path.exists(args.face_image):
                print(f"[ERROR] Face image not found: {args.face_image}")
                return False
            
            if not os.path.exists(args.carrier_image):
                print(f"[ERROR] Carrier image not found: {args.carrier_image}")
                return False
            
            # Generate AES key
            aes_key = crypto.generate_random_key()
            
            # Run pipeline
            pipeline = EmbeddingPipeline(aes_key, verbose=True)
            result = pipeline.run(args.face_image, args.carrier_image, args.output_image)
            
            # Save key if requested
            if args.key_file:
                with open(args.key_file, 'wb') as f:
                    f.write(aes_key)
                print(f"\n[KEY] Saved AES key to {args.key_file}")
            
            # Generate and save report if requested
            if args.report:
                report = report_generator.generate_json_report(result)
                report_generator.save_json_report(report, args.report)
                print(f"[REPORT] Saved to {args.report}")
            
            print("\n[SUCCESS] Embedding complete!")
            return True
            
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
            return False
    
    def cmd_verify(self, args):
        """Execute verify command."""
        try:
            print("\n[CLI] Biometric Verification Pipeline")
            print("=" * 60)
            
            if not os.path.exists(args.stego_image):
                print(f"[ERROR] Stego image not found: {args.stego_image}")
                return False
            
            # Load or parse AES key
            if args.key_file:
                if not os.path.exists(args.key_file):
                    print(f"[ERROR] Key file not found: {args.key_file}")
                    return False
                with open(args.key_file, 'rb') as f:
                    aes_key = f.read()
            elif args.key_hex:
                aes_key = bytes.fromhex(args.key_hex)
            else:
                print("[ERROR] Must provide --key-file or --key-hex")
                return False
            
            # Run verification pipeline
            pipeline = VerificationPipeline(aes_key, verbose=True)
            result = pipeline.run(args.stego_image)
            
            # Generate report if requested
            if args.report:
                report = report_generator.generate_verification_report(result)
                report_generator.save_json_report(report, args.report)
                print(f"\n[REPORT] Saved to {args.report}")
            
            status = "✓ PASSED" if result['integrity_verified'] else "✗ FAILED"
            print(f"\n[RESULT] Verification {status}")
            return result['integrity_verified']
            
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
            return False
    
    def cmd_benchmark(self, args):
        """Execute benchmark command."""
        try:
            print("\n[CLI] Benchmarking Pipeline")
            print("=" * 60)
            print(f"Iterations: {args.iterations}")
            
            results = []
            
            for i in range(args.iterations):
                print(f"\n[Run {i+1}/{args.iterations}]", end='', flush=True)
                
                try:
                    # Extract embedding
                    embedding = embeddings.extract_face_embedding(args.face_image)
                    
                    # Run embedding pipeline
                    aes_key = crypto.generate_random_key()
                    pipeline = EmbeddingPipeline(aes_key, verbose=False)
                    
                    import time
                    start = time.time()
                    result = pipeline.run(args.face_image, args.carrier_image, 
                                        f'temp_stego_{i}.png')
                    elapsed = time.time() - start
                    
                    results.append({
                        'run': i + 1,
                        'total_time_s': elapsed,
                        'embedding_size': result['metrics']['embedding_size'],
                        'encrypted_size': result['metrics']['encrypted_size'],
                        'dna_length': result['metrics']['dna_length'],
                        'payload_size': result['metrics']['payload_size'],
                    })
                    
                    print(f" ✓ {elapsed:.4f}s")
                    
                    # Cleanup
                    if os.path.exists(f'temp_stego_{i}.png'):
                        os.remove(f'temp_stego_{i}.png')
                        
                except Exception as e:
                    print(f" ✗ Failed: {str(e)}")
                    continue
            
            # Generate summary
            if results:
                summary = report_generator.generate_performance_summary(results)
                
                print("\n" + "=" * 60)
                print("[SUMMARY]")
                print(f"Successful runs: {len(results)}/{args.iterations}")
                print(f"Average time: {summary['timing_statistics']['mean_seconds']:.4f}s")
                print(f"Std dev: {summary['timing_statistics']['std_dev_seconds']:.4f}s")
                print(f"Min: {summary['timing_statistics']['min_seconds']:.4f}s")
                print(f"Max: {summary['timing_statistics']['max_seconds']:.4f}s")
                
                # Save CSV if requested
                if args.csv:
                    report_generator.generate_csv_benchmark(results, args.csv)
                    print(f"\n[CSV] Saved to {args.csv}")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
            return False
    
    def cmd_gen_embedding(self, args):
        """Generate synthetic embedding."""
        try:
            print("\n[CLI] Generating Synthetic Embedding")
            print("=" * 60)
            
            embedding = embeddings.generate_synthetic_embedding(seed=args.seed)
            
            print(f"Generated 128-dimensional embedding")
            print(f"Shape: {embedding.shape}")
            print(f"Mean: {np.mean(embedding):.4f}")
            print(f"Std: {np.std(embedding):.4f}")
            
            if args.output:
                with open(args.output, 'wb') as f:
                    f.write(embedding.astype(np.float32).tobytes())
                print(f"\n[SAVED] Embedding to {args.output}")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
            return False
    
    def run(self, args=None):
        """Run CLI."""
        if args is None:
            args = sys.argv[1:]
        
        # If no command provided, show help
        if not args:
            self.parser.print_help()
            return 0
        
        parsed_args = self.parser.parse_args(args)
        
        # Execute command
        if hasattr(parsed_args, 'func'):
            success = parsed_args.func(parsed_args)
            return 0 if success else 1
        else:
            self.parser.print_help()
            return 1


def main():
    """Main entry point."""
    cli = CLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
