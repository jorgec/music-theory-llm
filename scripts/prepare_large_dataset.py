"""
Prepare comprehensive training data for improved music theory model
Non-interactive script that combines synthetic data with real music21 corpus
"""

import sys
import pickle
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.data_loaders import TrainingDataLoader
from src.theory import ChordProgression

def main():
    print("=" * 60)
    print("PREPARING COMPREHENSIVE TRAINING DATA")
    print("=" * 60)

    loader = TrainingDataLoader()
    all_progressions = []

    # 1. Generate synthetic data (good baseline)
    print("\n1. Generating synthetic progressions...")
    synthetic = loader.generate_synthetic_progressions(num_progressions=2000)
    all_progressions.extend(synthetic)
    print(f"   ✓ Generated {len(synthetic)} synthetic progressions")

    # 2. Try to load from music21 corpus (if available)
    print("\n2. Loading from music21 corpus...")
    try:
        music21_data = loader.load_from_music21_corpus(limit=1000)
        all_progressions.extend(music21_data)
        print(f"   ✓ Loaded {len(music21_data)} progressions from music21")
    except Exception as e:
        print(f"   ⚠ Could not load music21 data: {e}")
        print("   → Continuing with synthetic data only")

    # 3. Save combined dataset
    print(f"\n3. Saving combined dataset...")
    output_dir = Path(__file__).parent.parent / 'data' / 'processed'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'training_data_large.pkl'
    with open(output_file, 'wb') as f:
        pickle.dump(all_progressions, f)

    print(f"   ✓ Saved {len(all_progressions)} progressions to {output_file}")

    # 4. Print statistics
    print("\n" + "=" * 60)
    print("DATASET STATISTICS")
    print("=" * 60)
    print(f"Total progressions: {len(all_progressions)}")

    # Count by style if available
    styles = {}
    for prog in all_progressions:
        style = getattr(prog, 'style', 'unknown')
        styles[style] = styles.get(style, 0) + 1

    print("\nBy style:")
    for style, count in sorted(styles.items(), key=lambda x: -x[1]):
        print(f"  {style}: {count}")

    # Calculate average length
    avg_length = sum(len(p.chords) for p in all_progressions) / len(all_progressions)
    print(f"\nAverage progression length: {avg_length:.1f} chords")

    print("\n" + "=" * 60)
    print("✓ Dataset preparation complete!")
    print("=" * 60)

    return all_progressions

if __name__ == '__main__':
    main()
