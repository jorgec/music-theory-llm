#!/bin/bash
# Setup Script 03: Data Preparation
# Creates necessary directories and prepares data structures

set -e  # Exit on error

echo "================================"
echo "03: Preparing Data Directories"
echo "================================"

# Create data directories
echo "[INFO] Creating data directories..."

directories=(
    "data"
    "data/styles"
    "data/raw"
    "data/processed"
    "models"
    "models/checkpoints"
    "models/saved"
    "logs"
    "outputs"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "[OK] Created: $dir"
    else
        echo "[INFO] Already exists: $dir"
    fi
done

# Create .gitkeep files to preserve empty directories
echo "[INFO] Creating .gitkeep files..."
for dir in "${directories[@]}"; do
    if [ ! -f "$dir/.gitkeep" ]; then
        touch "$dir/.gitkeep"
    fi
done

# Check if data preparation scripts exist
echo ""
echo "[INFO] Checking for data preparation scripts..."

if [ -f "prepare_music_data.py" ]; then
    echo "[OK] Found: prepare_music_data.py"
    echo "[INFO] To generate training data, run: python prepare_music_data.py"
else
    echo "[WARNING] prepare_music_data.py not found"
fi

# List existing data files
echo ""
echo "[INFO] Existing data files:"
if [ -d "data/styles" ]; then
    file_count=$(find data/styles -type f | wc -l)
    if [ "$file_count" -gt 0 ]; then
        echo "[OK] Found $file_count data file(s) in data/styles/"
        ls -lh data/styles/ 2>/dev/null || echo "[INFO] No files to list"
    else
        echo "[INFO] No data files found in data/styles/"
        echo "[INFO] The system will use the built-in lick database"
    fi
fi

echo ""
echo "[OK] Data preparation complete"
echo "================================"
