"""
Configuration and constants for secure biometric identity verification system.
Designed for technical publication and extensibility for future quantum/blockchain modules.
Author: Secure Biometric System Prototype
Date: 2026
"""

# =========================
# CRYPTOGRAPHY CONFIGURATION
# =========================

# AES-256 key size (32 bytes = 256 bits)
AES_KEY_SIZE = 32

# Supported encryption modes for future extensibility
ENCRYPTION_ALGORITHMS = ['AES_CBC']

# Hash algorithm for integrity verification
HASH_ALGORITHM = 'sha256'


# =========================
# DNA ENCODING CONFIGURATION
# =========================

# Standard DNA mapping: 2-bit binary to DNA nucleotide
DNA_MAPPING = {
    '00': 'A',  # Adenine
    '01': 'T',  # Thymine
    '10': 'G',  # Guanine
    '11': 'C'   # Cytosine
}

# Reverse mapping for decoding
REVERSE_DNA_MAPPING = {v: k for k, v in DNA_MAPPING.items()}


# =========================
# IMAGE & STEGANOGRAPHY CONFIGURATION
# =========================

# Supported image formats
SUPPORTED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'bmp']

# JPEG compression quality for output
JPEG_QUALITY = 95

# PNG compression level (0-9, where 9 is maximum compression)
PNG_COMPRESSION = 6

# Steganography method (LSB, DCT, etc.)
STEGANOGRAPHY_METHOD = 'LSB'


# =========================
# FACE RECOGNITION CONFIGURATION
# =========================

# Number of up-sampling passes for face detection
FACE_DETECTION_UPSAMPLES = 1

# Number of CNN layers to process (higher = more accurate, slower)
FACE_DETECTION_MODEL = 'hog'  # 'hog' or 'cnn' (CNN requires CUDA)


# =========================
# RESEARCH METRICS CONFIGURATION
# =========================

# Maximum payload size per image (bytes) - for capacity testing
MAX_PAYLOAD_SIZE = 10000

# Minimum PSNR threshold for steganography quality (dB)
MIN_PSNR_THRESHOLD = 40.0

# Benchmark repetition count
BENCHMARK_ITERATIONS = 10


# =========================
# PIPELINE CONFIGURATION
# =========================

# Enable verbose logging
VERBOSE_LOGGING = True

# Enable timing measurements for each stage
MEASURE_TIMING = True


# =========================
# EXTENSIBILITY HOOKS FOR FUTURE MODULES
# =========================

# Post-Quantum Cryptography (Kyber)
ENABLE_PQC_ENCRYPTION = False
PQC_ALGORITHM = 'Kyber1024'  # Placeholder for future

# Blockchain Integration
ENABLE_BLOCKCHAIN_VERIFICATION = False
BLOCKCHAIN_NETWORK = 'ethereum'  # Placeholder for future

# Advanced Steganography Methods
ENABLE_DCT_STEGANOGRAPHY = False
ENABLE_AI_STEGANOGRAPHY = False

# Liveness Detection
ENABLE_LIVENESS_DETECTION = False

# Behavioral Verification
ENABLE_BEHAVIORAL_VERIFICATION = False


# =========================
# OUTPUT & REPORTING CONFIGURATION
# =========================

# Default output directory for reports
DEFAULT_OUTPUT_DIR = './output'

# JSON report filename template
JSON_REPORT_TEMPLATE = 'report_{timestamp}.json'

# CSV benchmark filename template
CSV_BENCHMARK_TEMPLATE = 'benchmark_{timestamp}.csv'

# Enable detailed metrics in reports
DETAILED_METRICS = True


# =========================
# TESTING & DEVELOPMENT CONFIGURATION
# =========================

# Generate synthetic test embeddings (for testing without real faces)
USE_SYNTHETIC_EMBEDDINGS_FOR_TESTING = True

# Synthetic embedding dimension (face_recognition uses 128D)
SYNTHETIC_EMBEDDING_DIM = 128

# Seed for reproducible synthetic data
RANDOM_SEED = 42
