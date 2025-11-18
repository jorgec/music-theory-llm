#!/bin/bash
# Master Setup Script - Music Theory ML System
# Compatible with Mac M1/M2
# Orchestrates all setup steps

set -e  # Exit on error

echo ""
echo "========================================================================"
echo "  MUSIC THEORY ML SYSTEM - COMPLETE SETUP"
echo "========================================================================"
echo ""
echo "  700 EPOCHS | 650M+ PARAMETERS | 20+ ARTISTS | 65+ LICKS"
echo "  With Comprehensive Music Theory Explanations"
echo ""
echo "  Compatible with Mac M1/M2 (ARM64) and Intel (x86_64)"
echo ""
echo "========================================================================"
echo ""

# Check if we're in the project root
if [ ! -f "requirements.txt" ]; then
    echo "[ERROR] requirements.txt not found"
    echo "[ERROR] Please run this script from the project root directory"
    exit 1
fi

# Make all setup scripts executable
echo "[INFO] Making setup scripts executable..."
chmod +x setup/*.sh
echo "[OK] Setup scripts are executable"
echo ""

# Function to run setup step with error handling
run_setup_step() {
    local script=$1
    local description=$2

    echo ""
    echo "--------------------------------------------------------------------"
    echo "Running: $description"
    echo "--------------------------------------------------------------------"

    if bash "$script"; then
        echo "[OK] $description completed successfully"
        return 0
    else
        echo "[ERROR] $description failed"
        echo "[ERROR] Setup aborted. Please fix the error and run again."
        echo ""
        echo "To re-run individual steps:"
        echo "  ./setup/01_environment.sh   - Python environment"
        echo "  ./setup/02_dependencies.sh  - Install dependencies"
        echo "  ./setup/03_data.sh          - Prepare data directories"
        echo "  ./setup/04_verify.sh        - Verify installation"
        exit 1
    fi
}

# Run all setup steps
run_setup_step "setup/01_environment.sh" "Python Environment Setup"
echo ""
echo "[INFO] Please activate the virtual environment for the next steps:"
echo "      source venv/bin/activate"
echo ""
read -p "Press Enter after activating the virtual environment..."

run_setup_step "setup/02_dependencies.sh" "Dependencies Installation"
run_setup_step "setup/03_data.sh" "Data Preparation"
run_setup_step "setup/04_verify.sh" "Installation Verification"

# Final success message
echo ""
echo "========================================================================"
echo "  [OK] SETUP COMPLETE!"
echo "========================================================================"
echo ""
echo "Your Music Theory ML System is ready to use!"
echo ""
echo "Quick Start Guide:"
echo ""
echo "  1. Activate environment (if not already active):"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run demonstrations:"
echo "     python demo_complete_artist_showcase.py"
echo "     python demo_eric_johnson_greg_howe.py"
echo ""
echo "  3. Test theory explanations:"
echo "     python test_theory_explanations.py"
echo ""
echo "  4. Train models (700 epochs):"
echo "     python train_priority_styles.py"
echo ""
echo "  5. Generate music with theory explanations:"
echo "     python -c \"from src.recommender import MusicRecommendationSystem; \\"
echo "                from src.theory import Note; \\"
echo "                system = MusicRecommendationSystem(); \\"
echo "                licks = system.lick_recommender.recommend_licks('rock_fusion', Note.from_string('E'), num_recommendations=3); \\"
echo "                [print(f'{l.item[\\\"name\\\"]}: {l.explanation}') for l in licks]\""
echo ""
echo "Documentation:"
echo "  - README.md - Project overview"
echo "  - requirements.txt - Dependencies with M1/M2 notes"
echo "  - src/theory_explainer.py - Theory explanation system"
echo ""
echo "========================================================================"
echo ""
