#!/bin/bash
# Setup Script 01: Python Environment Setup
# Compatible with Mac M1/M2
# Creates a clean Python virtual environment

set -e  # Exit on error

echo "================================"
echo "01: Setting up Python Environment"
echo "================================"

# Check Python version
PYTHON_CMD=""
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
elif command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "[ERROR] Python 3.9+ not found. Please install Python 3.9 or later."
    exit 1
fi

echo "[INFO] Using Python: $PYTHON_CMD"
$PYTHON_CMD --version

# Check if running on Mac M1/M2
if [[ $(uname -m) == "arm64" ]]; then
    echo "[INFO] Detected Apple Silicon (M1/M2) - ARM64 architecture"
    echo "[INFO] PyTorch will use Metal Performance Shaders (MPS) for GPU acceleration"
else
    echo "[INFO] Architecture: $(uname -m)"
fi

# Create virtual environment
echo "[INFO] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "[WARNING] Virtual environment 'venv' already exists"
    read -p "Remove and recreate? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        $PYTHON_CMD -m venv venv
        echo "[OK] Virtual environment recreated"
    else
        echo "[INFO] Keeping existing virtual environment"
    fi
else
    $PYTHON_CMD -m venv venv
    echo "[OK] Virtual environment created"
fi

# Activate virtual environment
echo "[INFO] To activate the virtual environment, run:"
echo "    source venv/bin/activate"

echo ""
echo "[OK] Environment setup complete"
echo "================================"
