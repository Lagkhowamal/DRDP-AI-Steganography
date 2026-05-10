"""
Setup script for biometric verification system.
"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='biometric-verify',
    version='1.0.0',
    author='Lagkhowamal',
    description='Secure Biometric Identity Verification System - AES + DNA Encoding + LSB Steganography',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Lagkhowamal/DRDP-AI-Steganography',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'opencv-python>=4.8.0',
        'face-recognition>=1.3.5',
        'numpy>=1.24.0',
        'Pillow>=10.0.0',
        'pycryptodome>=3.18.0',
        'stegano>=0.11.0',
        'Flask>=3.0.0',
        'scikit-image>=0.21.0',
    ],
    entry_points={
        'console_scripts': [
            'biometric-verify=biometric_verify.cli.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='biometric face recognition encryption steganography DNA security',
)
