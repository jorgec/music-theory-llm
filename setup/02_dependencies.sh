#!/bin/bash
# Setup Script 02: Install Dependencies
# Compatible with Mac M1/M2
# Installs all required Python packages

set -e  # Exit on error

echo "================================"
echo "02: Installing Dependencies"
echo "================================"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "[WARNING] Virtual environment not activated"
    echo "[INFO] Attempting to activate venv..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "[OK] Virtual environment activated"
    else
        echo "[ERROR] Virtual environment not found. Run 01_environment.sh first"
        exit 1
    fi
fi

echo "[INFO] Using Python: $(which python)"
python --version

# Upgrade pip, setuptools, and wheel
echo "[INFO] Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install dependencies from requirements.txt
echo "[INFO] Installing dependencies from requirements.txt..."
echo "[INFO] This may take several minutes, especially on first install..."

if [ -f "requirements.txt" ]; then
    # Install with progress bar
    pip install -r requirements.txt --progress-bar=on
    echo "[OK] Dependencies installed successfully"
else
    echo "[ERROR] requirements.txt not found"
    exit 1
fi

# Verify PyTorch installation and MPS support (for Mac M1/M2)
echo ""
echo "[INFO] Verifying PyTorch installation..."
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"

if [[ $(uname -m) == "arm64" ]]; then
    echo "[INFO] Checking MPS (Metal Performance Shaders) support..."
    python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')" || echo "[WARNING] MPS check failed"
fi

echo ""
echo "[OK] Dependencies installation complete"
echo "================================"
