<div align="center">
  <img src="https://img.shields.io/badge/Status-Research--Prototype-blue?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Security-AES--256--CBC-green?style=for-the-badge" alt="Security">
  <img src="https://img.shields.io/badge/Encoding-DNA-red?style=for-the-badge" alt="Encoding">
</div>

<h1 align="center">🔐 Secure Biometric Identity Verification</h1>

<p align="center">
  <strong>Secure Biometric System | AES-256 + DNA Encoding + LSB Steganography</strong>
</p>

<div align="center">
  <p>A robust framework for secure biometric template protection using a multi-layer transformation pipeline.</p>
</div>

<hr />

## 📖 Overview

This project implements a complete secure biometric pipeline designed for high-integrity identity verification. It transforms raw biometric embeddings into a steganographic "payload" that is encrypted, DNA-encoded, and hidden within a carrier image.

### 🛠 The Pipeline
1.  **Extraction**: Generate a 128-D face embedding (biometric vector).
2.  **Encryption**: Secure the vector with **AES-256-CBC**.
3.  **Encoding**: Convert encrypted bytes into **DNA nucleotide sequences** (A, T, G, C).
4.  **Hiding**: Embed the DNA sequence into a carrier image using **LSB Steganography**.

<hr />

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- `pip` package manager

### Installation
```bash
# Clone the repository
git clone https://github.com/Lagkhowamal/DRDP-AI-Steganography.git
cd DRDP-AI-Steganography

# Install dependencies
pip install -r biometric_verify/requirements.txt
```

<hr />

## 💻 Usage

### 🌐 Web Interface (GUI)
Launch the interactive Flask dashboard:
```bash
python -m biometric_verify.web.app
```
*Open `http://localhost:5000` in your browser.*

### ⌨️ Command Line (CLI)
**Embed data:**
```bash
python biometric_verify/cli/main.py embed face.jpg carrier.png stego.png --key-file aes.key
```

**Verify data:**
```bash
python biometric_verify/cli/main.py verify stego.png --key-file aes.key
```

<hr />

## 📊 Research Metrics
The system provides publication-ready metrics:
- **PSNR**: Peak Signal-to-Noise Ratio (typical > 45dB)
- **SSIM**: Structural Similarity Index (typical > 0.95)
- **GC-Content**: DNA nucleotide distribution analysis
- **Throughput**: Execution timing for each pipeline stage

<hr />

## 📂 Project Structure
```
biometric_verify/
├── core/         # AES, DNA, Hashing, Embeddings, Steganography
├── pipeline/     # Embedding & Verification Orchestration
├── bio_io/       # Image Handlers & Report Generators
├── metrics/      # PSNR, SSIM, Benchmarking
├── web/          # Flask GUI (HTML/JS/CSS)
└── cli/          # Command Line Interface
```

<hr />

<div align="center">
  <p><i>Developed for Biometric Core demonstration purposes.</i></p>
  <p>© 2026 Lagkhowamal | MIT License</p>
</div>
