#!/usr/bin/env python3
"""
Prepare Training Data

Script to download, process, and prepare training data for the Music Theory ML Model.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.data_loaders import TrainingDataLoader, quick_start_dataset
from data.lick_database import BluesRockLickDatabase, export_licks_to_json


def main():
    print("=" * 80)
    print("MUSIC THEORY ML - TRAINING DATA PREPARATION")
    print("=" * 80)
    print()

    print("This script will help you prepare training data for the model.")
    print()

    # Create data directories
    data_dir = Path("data")
    (data_dir / "raw").mkdir(parents=True, exist_ok=True)
    (data_dir / "processed").mkdir(parents=True, exist_ok=True)

    print("Options:")
    print("  1. Quick Start (500 progressions, ready in <1 min)")
    print("  2. music21 Corpus (requires music21 library)")
    print("  3. Generate Synthetic Data (1000+ progressions)")
    print("  4. Export Lick Database")
    print("  5. Full Dataset (all sources)")
    print("  6. Exit")
    print()

    choice = input("Choose option (1-6): ").strip()

    loader = TrainingDataLoader()

    if choice == '1':
        print("\n🚀 Creating quick start dataset...")
        quick_start_dataset()
        print("\n✓ Ready to train!")
        print("  Run: python train.py --task progression --epochs 10")

    elif choice == '2':
        print("\n📚 Loading from music21 corpus...")
        try:
            limit = int(input("How many pieces to load? (default 100): ") or "100")
            progressions = loader.load_from_music21_corpus(limit=limit)

            if progressions:
                output = "data/processed/music21_progressions.json"
                loader.save_progressions(progressions, output)
                print(f"\n✓ Saved {len(progressions)} progressions to {output}")
            else:
                print("\n⚠ No progressions loaded. Is music21 installed?")
                print("  Install with: pip install music21")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("  Make sure music21 is installed: pip install music21")

    elif choice == '3':
        print("\n🎲 Generating synthetic progressions...")
        try:
            num = int(input("How many to generate? (default 1000): ") or "1000")
            progressions = loader.generate_synthetic_progressions(num)

            output = "data/processed/synthetic_progressions.json"
            loader.save_progressions(progressions, output)
            print(f"\n✓ Generated and saved {len(progressions)} progressions to {output}")

        except Exception as e:
            print(f"\n❌ Error: {e}")

    elif choice == '4':
        print("\n🎸 Exporting lick database...")
        try:
            output = "data/licks.json"
            export_licks_to_json(output)

            # Also show summary
            db = BluesRockLickDatabase()
            print(f"\n✓ Exported {len(db.licks)} licks to {output}")
            print("\nDatabase includes:")
            print("  • BB King, Albert King, Muddy Waters")
            print("  • Jimi Hendrix, Eric Clapton, Jimmy Page")
            print("  • Carlos Santana, David Gilmour, Jeff Beck")
            print("  • Eddie Van Halen, SRV, Angus Young")

        except Exception as e:
            print(f"\n❌ Error: {e}")

    elif choice == '5':
        print("\n📦 Creating full dataset (this may take several minutes)...")

        sources = ['synthetic']

        # Ask about music21
        use_music21 = input("Include music21 corpus? (y/n, requires music21): ").lower().strip()
        if use_music21 == 'y':
            sources.append('music21')

        try:
            limit = int(input("Limit per source? (default 1000): ") or "1000")

            dataset = loader.create_training_dataset(
                output_dir="data/processed",
                sources=sources,
                limit_per_source=limit
            )

            print("\n✓ Full dataset created!")
            print("\nYou can now:")
            print("  1. Train chord progression model:")
            print("     python train.py --task progression --epochs 20")
            print()
            print("  2. Train scale identification model:")
            print("     python train.py --task scale --epochs 15")
            print()
            print("  3. Train with statistical analyzer:")
            print("     See examples/intelligence_demo.py")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

    elif choice == '6':
        print("\nExiting...")
        return

    else:
        print("\n❌ Invalid choice")
        return

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Review your data:")
    print("   ls -lh data/processed/")
    print()
    print("2. Train a model:")
    print("   python train.py --task progression --epochs 20")
    print()
    print("3. Use statistical analysis:")
    print("   python examples/intelligence_demo.py")
    print()
    print("4. Fine-tune on your data:")
    print("   See INTELLIGENCE.md for examples")
    print()


if __name__ == '__main__':
    main()
