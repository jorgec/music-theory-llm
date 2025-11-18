#!/bin/bash
# Setup Script 04: Installation Verification
# Verifies that all components are correctly installed

set -e  # Exit on error

echo "================================"
echo "04: Verifying Installation"
echo "================================"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "[WARNING] Virtual environment not activated"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo "[ERROR] Virtual environment not found"
        exit 1
    fi
fi

echo "[INFO] Python environment: $VIRTUAL_ENV"
python --version
echo ""

# Verify core imports
echo "[INFO] Verifying core Python imports..."

verification_script=$(cat << 'EOF'
import sys

def check_import(module_name, display_name=None):
    if display_name is None:
        display_name = module_name
    try:
        __import__(module_name)
        print(f"  [OK] {display_name}")
        return True
    except ImportError as e:
        print(f"  [ERROR] {display_name}: {e}")
        return False

all_ok = True

print("Core Libraries:")
all_ok &= check_import("torch", "PyTorch")
all_ok &= check_import("numpy", "NumPy")
all_ok &= check_import("pandas", "Pandas")

print("\nMusic Processing:")
all_ok &= check_import("music21", "music21")
all_ok &= check_import("mido", "mido")
all_ok &= check_import("pretty_midi", "pretty_midi")

print("\nProject Modules:")
all_ok &= check_import("src.theory", "src.theory")
all_ok &= check_import("src.recommender", "src.recommender")
all_ok &= check_import("src.theory_explainer", "src.theory_explainer")

print("\nDevelopment Tools:")
all_ok &= check_import("pytest", "pytest")
all_ok &= check_import("black", "black")

if all_ok:
    print("\n[OK] All imports successful")
    sys.exit(0)
else:
    print("\n[ERROR] Some imports failed")
    sys.exit(1)
EOF
)

echo "$verification_script" | python
verification_status=$?

echo ""

# Check PyTorch MPS support on Mac M1/M2
if [[ $(uname -m) == "arm64" ]]; then
    echo "[INFO] Checking Metal Performance Shaders (MPS) support..."
    python -c "import torch; mps=torch.backends.mps.is_available(); print('[OK] MPS available' if mps else '[WARNING] MPS not available - will use CPU')"
    echo ""
fi

# Check directory structure
echo "[INFO] Verifying directory structure..."
required_dirs=("src" "data" "models" "logs")
all_dirs_ok=true

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "  [OK] $dir/"
    else
        echo "  [ERROR] $dir/ not found"
        all_dirs_ok=false
    fi
done

echo ""

# Final status
if [ $verification_status -eq 0 ] && [ "$all_dirs_ok" = true ]; then
    echo "================================"
    echo "[OK] Installation verified successfully!"
    echo "================================"
    echo ""
    echo "Next steps:"
    echo "  1. Run demos: python demo_complete_artist_showcase.py"
    echo "  2. Test system: python test_theory_explanations.py"
    echo "  3. Train models: python train_priority_styles.py"
    echo ""
    exit 0
else
    echo "================================"
    echo "[ERROR] Installation verification failed"
    echo "================================"
    echo "Please review errors above and re-run setup scripts"
    exit 1
fi
