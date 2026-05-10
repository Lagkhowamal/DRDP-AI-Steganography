"""
Report generation module for research metrics and results.
Generates JSON reports and CSV benchmarks for Production-ready.
"""

import json
import csv
import os
from datetime import datetime
import config


class ReportGeneratorError(Exception):
    """Raised when report generation fails."""
    pass


def generate_json_report(pipeline_result: dict, metrics: dict = None, 
                        include_payload: bool = False) -> dict:
    """
    Generate comprehensive JSON report from pipeline results.
    
    Args:
        pipeline_result: Dictionary from EmbeddingPipeline.run()
        metrics: Optional additional metrics dict
        include_payload: Whether to include large DNA payload
    
    Returns:
        Report dictionary suitable for JSON serialization
    """
    try:
        report = {
            'timestamp': datetime.now().isoformat(),
            'system': 'Secure Biometric Identity Verification',
            'version': '1.0.0',
            'status': 'success' if pipeline_result.get('success', False) else 'failed',
        }
        
        # Pipeline metrics
        if 'metrics' in pipeline_result:
            report['metrics'] = {
                'embedding_size_bytes': pipeline_result['metrics'].get('embedding_size'),
                'encrypted_size_bytes': pipeline_result['metrics'].get('encrypted_size'),
                'dna_length': pipeline_result['metrics'].get('dna_length'),
                'payload_size_bytes': pipeline_result['metrics'].get('payload_size'),
                'encryption_overhead_bytes': pipeline_result['metrics'].get('encryption_overhead'),
                'dna_expansion_ratio': pipeline_result['metrics'].get('dna_expansion_ratio'),
                'total_time_seconds': pipeline_result['metrics'].get('total_time'),
            }
        
        # Steganography results
        if 'metrics' in pipeline_result and 'stego_result' in pipeline_result['metrics']:
            stego = pipeline_result['metrics']['stego_result']
            report['steganography'] = {
                'carrier_size_bytes': stego.get('carrier_size'),
                'stego_size_bytes': stego.get('stego_size'),
                'capacity_used_percent': stego.get('capacity_used_percent'),
                'output_path': stego.get('output_path'),
            }
        
        # DNA statistics
        if 'dna_stats' in pipeline_result:
            stats = pipeline_result['dna_stats']
            report['dna_analysis'] = {
                'total_length': stats.get('total_length'),
                'nucleotide_counts': stats.get('nucleotide_counts'),
                'nucleotide_ratios': stats.get('nucleotide_ratios'),
                'gc_content': stats.get('gc_content'),
            }
        
        # Hashes for verification
        if 'hashes' in pipeline_result:
            report['integrity'] = {
                'algorithm': 'SHA256',
                'embedding_hash': pipeline_result['hashes'].get('embedding'),
                'encrypted_hash': pipeline_result['hashes'].get('encrypted'),
                'dna_hash': pipeline_result['hashes'].get('dna'),
            }
        
        # Optional: DNA payload (can be large)
        if include_payload and 'dna_payload' in pipeline_result:
            report['payload'] = {
                'dna_sequence': pipeline_result['dna_payload'][:500] + '...',  # First 500 chars
                'full_length': len(pipeline_result['dna_payload']),
            }
        
        # Additional metrics if provided
        if metrics:
            report['additional_metrics'] = metrics
        
        return report
        
    except Exception as e:
        raise ReportGeneratorError(f"JSON report generation failed: {str(e)}")


def save_json_report(report: dict, output_path: str) -> str:
    """
    Save JSON report to file.
    
    Args:
        report: Report dictionary
        output_path: Path for output JSON file
    
    Returns:
        Path to saved report
        
    Raises:
        ReportGeneratorError: If save operation fails
    """
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        if config.VERBOSE_LOGGING:
            print(f"[REPORT] JSON report saved to {output_path}")
        
        return output_path
        
    except Exception as e:
        raise ReportGeneratorError(f"Failed to save JSON report: {str(e)}")


def generate_verification_report(verification_result: dict) -> dict:
    """
    Generate report from verification pipeline results.
    
    Args:
        verification_result: Dictionary from VerificationPipeline.run()
    
    Returns:
        Report dictionary
    """
    try:
        report = {
            'timestamp': datetime.now().isoformat(),
            'system': 'Biometric Verification Pipeline',
            'verification_status': 'passed' if verification_result.get('integrity_verified') else 'failed',
            'integrity_verified': verification_result.get('integrity_verified'),
            'metrics': {
                'recovered_embedding_size_bytes': verification_result['metrics'].get('recovered_embedding_size'),
                'dna_length': verification_result['metrics'].get('dna_length'),
                'total_time_seconds': verification_result['metrics'].get('total_time'),
            },
            'comparison': {
                'embedding_distance': verification_result.get('embedding_distance'),
                'comparison_successful': verification_result.get('comparison_successful'),
            },
        }
        
        if verification_result.get('integrity_errors'):
            report['integrity_errors'] = verification_result['integrity_errors']
        
        return report
        
    except Exception as e:
        raise ReportGeneratorError(f"Verification report generation failed: {str(e)}")


def generate_csv_benchmark(benchmark_data: list, output_path: str) -> str:
    """
    Generate CSV file from benchmark data.
    
    Args:
        benchmark_data: List of benchmark result dictionaries
        output_path: Path for output CSV file
    
    Returns:
        Path to saved CSV file
        
    Raises:
        ReportGeneratorError: If generation fails
    """
    try:
        if not benchmark_data:
            raise ReportGeneratorError("No benchmark data provided")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Determine CSV headers
        headers = set()
        for row in benchmark_data:
            headers.update(row.keys())
        
        headers = sorted(list(headers))
        
        # Write CSV
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(benchmark_data)
        
        if config.VERBOSE_LOGGING:
            print(f"[REPORT] CSV benchmark saved to {output_path}")
            print(f"  Rows: {len(benchmark_data)}, Columns: {len(headers)}")
        
        return output_path
        
    except Exception as e:
        raise ReportGeneratorError(f"CSV benchmark generation failed: {str(e)}")


def generate_performance_summary(results_list: list) -> dict:
    """
    Generate performance summary from multiple runs.
    
    Useful for averaging results across multiple iterations.
    
    Args:
        results_list: List of pipeline results
    
    Returns:
        Summary statistics dictionary
    """
    try:
        if not results_list:
            raise ReportGeneratorError("No results provided")
        
        import numpy as np
        
        # Extract timings
        timings = [r.get('metrics', {}).get('total_time', 0) for r in results_list]
        
        # Extract sizes
        embedding_sizes = [r.get('metrics', {}).get('embedding_size', 0) for r in results_list]
        encrypted_sizes = [r.get('metrics', {}).get('encrypted_size', 0) for r in results_list]
        dna_lengths = [r.get('metrics', {}).get('dna_length', 0) for r in results_list]
        
        timings_array = np.array(timings)
        
        summary = {
            'total_runs': len(results_list),
            'timing_statistics': {
                'mean_seconds': float(np.mean(timings_array)),
                'median_seconds': float(np.median(timings_array)),
                'std_dev_seconds': float(np.std(timings_array)),
                'min_seconds': float(np.min(timings_array)),
                'max_seconds': float(np.max(timings_array)),
            },
            'average_sizes': {
                'embedding_bytes': np.mean(embedding_sizes),
                'encrypted_bytes': np.mean(encrypted_sizes),
                'dna_nucleotides': np.mean(dna_lengths),
            },
        }
        
        return summary
        
    except Exception as e:
        raise ReportGeneratorError(f"Performance summary generation failed: {str(e)}")


def format_report_for_terminal(report: dict) -> str:
    """
    Format report as human-readable text for terminal display.
    
    Args:
        report: Report dictionary
    
    Returns:
        Formatted text string
    """
    try:
        lines = []
        lines.append("=" * 70)
        lines.append(f"RESEARCH REPORT: {report.get('system', 'System')}")
        lines.append(f"Status: {report.get('status', 'Unknown')}")
        lines.append(f"Generated: {report.get('timestamp', 'Unknown')}")
        lines.append("=" * 70)
        
        # Metrics section
        if 'metrics' in report:
            lines.append("\n[METRICS]")
            for key, value in report['metrics'].items():
                if isinstance(value, float):
                    lines.append(f"  {key}: {value:.4f}")
                else:
                    lines.append(f"  {key}: {value}")
        
        # Steganography section
        if 'steganography' in report:
            lines.append("\n[STEGANOGRAPHY]")
            for key, value in report['steganography'].items():
                if key == 'capacity_used_percent' and isinstance(value, float):
                    lines.append(f"  {key}: {value:.2f}%")
                else:
                    lines.append(f"  {key}: {value}")
        
        # DNA analysis section
        if 'dna_analysis' in report:
            lines.append("\n[DNA ANALYSIS]")
            dna = report['dna_analysis']
            lines.append(f"  Total length: {dna.get('total_length')} nucleotides")
            if 'nucleotide_counts' in dna:
                counts = dna['nucleotide_counts']
                lines.append(f"  A: {counts.get('A')}, T: {counts.get('T')}, "
                           f"G: {counts.get('G')}, C: {counts.get('C')}")
            if 'gc_content' in dna:
                lines.append(f"  GC-content: {dna['gc_content']:.2%}")
        
        # Integrity section
        if 'integrity' in report:
            lines.append("\n[INTEGRITY]")
            integrity = report['integrity']
            lines.append(f"  Algorithm: {integrity.get('algorithm')}")
            lines.append(f"  Embedding hash: {integrity.get('embedding_hash', '')[:16]}...")
        
        lines.append("\n" + "=" * 70)
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error formatting report: {str(e)}"
