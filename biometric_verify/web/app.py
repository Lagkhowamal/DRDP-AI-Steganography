"""
Flask web interface for biometric verification system.
Provides interactive web UI for embedding and verification.
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_file
import json
from datetime import datetime
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from core import crypto, embeddings
from pipeline.embedding_pipeline import EmbeddingPipeline
from pipeline.verification_pipeline import VerificationPipeline
from metrics import research_metrics
from bio_io import report_generator


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload

# Session storage for pipeline results
session_results = {}


@app.route('/')
def index():
    """Home page with upload form."""
    return render_template('index.html')


@app.route('/embed', methods=['POST'])
def embed():
    """Embed biometric in carrier image."""
    try:
        # Check if files were uploaded
        if 'face_image' not in request.files or 'carrier_image' not in request.files:
            return jsonify({'error': 'Missing required files'}), 400
        
        face_file = request.files['face_image']
        carrier_file = request.files['carrier_image']
        
        if face_file.filename == '' or carrier_file.filename == '':
            return jsonify({'error': 'No selected files'}), 400
        
        # Save uploaded files to temp directory
        temp_dir = 'temp_uploads'
        os.makedirs(temp_dir, exist_ok=True)
        
        face_path = os.path.join(temp_dir, 'face.jpg')
        carrier_path = os.path.join(temp_dir, 'carrier.png')
        
        face_file.save(face_path)
        carrier_file.save(carrier_path)
        
        # Generate AES key
        aes_key = crypto.generate_random_key()
        
        # Generate unique session ID
        session_id = f"session_{int(datetime.now().timestamp())}_{os.urandom(4).hex()}"
        
        # Run embedding pipeline
        output_path = os.path.join(temp_dir, f'stego_{session_id}.png')
        
        pipeline = EmbeddingPipeline(aes_key, verbose=False)
        result = pipeline.run(face_path, carrier_path, output_path)
        
        # Generate report
        report = report_generator.generate_json_report(result)
        
        # Store session result
        session_results[session_id] = {
            'result': result,
            'report': report,
            'aes_key': aes_key.hex(),
            'output_path': output_path,
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'report': report,
            'aes_key': aes_key.hex(),
            'message': 'Embedding completed successfully',
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/verify', methods=['POST'])
def verify():
    """Verify stego image."""
    try:
        if 'stego_image' not in request.files:
            return jsonify({'error': 'Missing stego image'}), 400
        
        if 'aes_key' not in request.form:
            return jsonify({'error': 'Missing AES key'}), 400
        
        stego_file = request.files['stego_image']
        aes_key_hex = request.form['aes_key']
        
        if stego_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Save stego image
        temp_dir = 'temp_uploads'
        os.makedirs(temp_dir, exist_ok=True)
        
        stego_path = os.path.join(temp_dir, 'verify_stego.png')
        stego_file.save(stego_path)
        
        # Reconstruct AES key
        aes_key = bytes.fromhex(aes_key_hex)
        
        # Run verification pipeline
        pipeline = VerificationPipeline(aes_key, verbose=False)
        result = pipeline.run(stego_path)
        
        # Generate report
        report = report_generator.generate_verification_report(result)
        
        return jsonify({
            'success': True,
            'verification_passed': result['integrity_verified'],
            'report': report,
            'embedding_distance': result.get('embedding_distance'),
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<session_id>')
def download_stego(session_id):
    """Download stego image."""
    try:
        if session_id not in session_results:
            return 'Session not found', 404
        
        output_path = session_results[session_id]['output_path']
        
        if not os.path.exists(output_path):
            return 'File not found', 404
        
        return send_file(output_path, as_attachment=True, 
                        download_name='stego_image.png')
        
    except Exception as e:
        return f'Error: {str(e)}', 500


@app.route('/metrics')
def metrics():
    """Display research metrics."""
    metrics_data = {
        'psnr_typical': '45-50 dB (LSB steganography)',
        'ssim_typical': '> 0.95 (high imperceptibility)',
        'embedding_size': '512 bytes (128D float32)',
        'encryption_overhead': '32 bytes (IV)',
        'dna_expansion': '~4x (8 bits → 4 nucleotides)',
        'payload_max': '~10 KB per typical image',
    }
    
    return render_template('metrics.html', metrics=metrics_data)


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})


def run_app(debug=False, host='localhost', port=5000):
    """Run Flask app."""
    print(f"\n[WEB] Starting Biometric Verification Web Interface")
    print(f"[WEB] http://{host}:{port}")
    print(f"[WEB] Press Ctrl+C to stop\n")
    
    app.run(debug=debug, host=host, port=port)


if __name__ == '__main__':
    run_app()
