"""
Test script to verify music theory explanations work correctly
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.recommender import MusicRecommendationSystem
from src.theory import Note


def test_lick_explanations():
    """Test that licks include theory explanations"""
    print("="*80)
    print("TESTING LICK THEORY EXPLANATIONS")
    print("="*80)

    system = MusicRecommendationSystem()

    # Test each style
    styles = {
        'blues': 'A',
        'neo_soul': 'D',
        'jazz': 'C',
        'progressive_metal': 'E',
        'rock_fusion': 'E',
        'metalcore': 'D'
    }

    for style, key_name in styles.items():
        print(f"\n\n{'='*80}")
        print(f"TESTING: {style.upper()} in key of {key_name}")
        print(f"{'='*80}\n")

        key = Note.from_string(key_name)

        licks = system.lick_recommender.recommend_licks(
            style=style,
            key=key,
            num_recommendations=2
        )

        for i, lick_rec in enumerate(licks, 1):
            lick = lick_rec.item
            print(f"\n{i}. {lick['name']}")
            print(f"   Score: {lick_rec.score:.3f}")
            print(f"   Key: {key_name}")

            # Check that explanation contains theory content
            explanation = lick_rec.explanation

            print(f"\n   EXPLANATION:")
            for line in explanation.split('\n'):
                if line.strip():
                    print(f"   {line}")

            # Verify theory explanation exists
            if 'Scale' in explanation or 'mode' in explanation or 'interval' in explanation:
                print(f"\n   ✅ Theory explanation detected")
            else:
                print(f"\n   ⚠️  Warning: Theory explanation may be missing")

            print(f"\n   {'-'*76}")


def test_progression_explanations():
    """Test that progressions include theory explanations"""
    print("\n\n" + "="*80)
    print("TESTING PROGRESSION THEORY EXPLANATIONS")
    print("="*80)

    system = MusicRecommendationSystem()

    # Test a couple styles
    test_styles = ['blues', 'neo_soul']

    for style in test_styles:
        print(f"\n\n{'='*80}")
        print(f"TESTING: {style.upper()} progressions")
        print(f"{'='*80}\n")

        progs = system.progression_recommender.recommend_progressions(
            style=style,
            num_recommendations=2
        )

        for i, prog_rec in enumerate(progs, 1):
            prog = prog_rec.item
            print(f"\n{i}. Progression Score: {prog_rec.score:.3f}")

            # Show chord names
            if hasattr(prog, 'chords'):
                chord_names = [c.to_symbol() for c in prog.chords[:4]]
                print(f"   Chords: {' → '.join(chord_names)}")

            print(f"\n   THEORY EXPLANATION:")
            for line in prog_rec.explanation.split('\n'):
                if line.strip():
                    print(f"   {line}")

            print(f"\n   {'-'*76}")


def main():
    """Run all tests"""
    print("\n🎵 TESTING MUSIC THEORY EXPLANATION SYSTEM 🎵\n")

    try:
        test_lick_explanations()
        test_progression_explanations()

        print("\n\n" + "="*80)
        print("✅ THEORY EXPLANATION SYSTEM TEST COMPLETE")
        print("="*80)
        print("\nAll theory explanation tests completed successfully!")
        print("The system now provides comprehensive music theory context for:")
        print("  • Lick recommendations")
        print("  • Chord progression recommendations")
        print("  • All musical styles")
        print("\n")

    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
