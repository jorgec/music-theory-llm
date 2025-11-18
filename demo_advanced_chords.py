"""
Demonstration of Advanced Chord Support

Shows the system's ability to handle:
- Extended chords (9ths, 11ths, 13ths)
- Altered dominants (7b9, 7#9, 7#11, 7alt)
- Half-diminished chords (m7b5)
- Diminished chords
- Complex jazz and blues voicings
- Authentic licks for each style
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.recommender import MusicRecommendationSystem
from src.theory import Note, Chord, ChordQuality


def print_header(title: str):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\n")


def demo_advanced_jazz_chords():
    """Demonstrate advanced jazz chord progressions"""
    print_header("ADVANCED JAZZ CHORDS")

    system = MusicRecommendationSystem()

    print("Jazz progressions with extended and altered chords:\n")

    keys = [Note.from_string(k) for k in ['C', 'F', 'Bb']]

    for key in keys:
        print(f"🎹 Key of {key.name}")
        print("-" * 80)

        progs = system.progression_recommender.recommend_progressions(
            style='jazz',
            key=key,
            num_recommendations=5
        )

        # Filter for progressions with advanced chords
        advanced_progs = []
        for rec in progs:
            prog = rec.item
            symbols = [c.to_symbol() for c in prog.chords]
            # Check if contains advanced chord types
            if any(x in ''.join(symbols) for x in ['7b9', '7#9', 'm7b5', '7alt', '13', '11']):
                advanced_progs.append((rec, symbols))

        for i, (rec, symbols) in enumerate(advanced_progs[:3], 1):
            print(f"\n  {i}. {' → '.join(symbols)}")
            print(f"     Score: {rec.score:.3f}")
            print(f"     {rec.explanation}")

        if not advanced_progs:
            # Show any progressions
            for i, rec in enumerate(progs[:2], 1):
                symbols = [c.to_symbol() for c in rec.item.chords]
                print(f"\n  {i}. {' → '.join(symbols)}")
                print(f"     Score: {rec.score:.3f}")

        print()


def demo_advanced_blues_chords():
    """Demonstrate advanced blues chord progressions"""
    print_header("ADVANCED BLUES CHORDS")

    system = MusicRecommendationSystem()

    print("Blues progressions with altered dominants and diminished chords:\n")

    keys = [Note.from_string(k) for k in ['E', 'A', 'G']]

    for key in keys:
        print(f"🎸 Key of {key.name}")
        print("-" * 80)

        progs = system.progression_recommender.recommend_progressions(
            style='blues',
            key=key,
            num_recommendations=5
        )

        # Filter for advanced blues chords
        advanced_progs = []
        for rec in progs:
            prog = rec.item
            symbols = [c.to_symbol() for c in prog.chords]
            if any(x in ''.join(symbols) for x in ['7#9', '7b9', 'dim', '13', '9']):
                advanced_progs.append((rec, symbols))

        for i, (rec, symbols) in enumerate(advanced_progs[:3], 1):
            print(f"\n  {i}. {' → '.join(symbols)}")
            print(f"     Score: {rec.score:.3f}")
            print(f"     {rec.explanation}")

        if not advanced_progs:
            for i, rec in enumerate(progs[:2], 1):
                symbols = [c.to_symbol() for c in rec.item.chords]
                print(f"\n  {i}. {' → '.join(symbols)}")
                print(f"     Score: {rec.score:.3f}")

        print()


def demo_chord_quality_support():
    """Demonstrate all supported chord qualities"""
    print_header("SUPPORTED CHORD QUALITIES")

    from src.theory.chords import CHORD_SYMBOLS, ChordQuality

    print("The system supports the following chord types:\n")

    categories = {
        "Triads": [ChordQuality.MAJOR, ChordQuality.MINOR, ChordQuality.DIMINISHED,
                   ChordQuality.AUGMENTED, ChordQuality.SUSPENDED_2, ChordQuality.SUSPENDED_4],
        "7th Chords": [ChordQuality.MAJOR_7, ChordQuality.MINOR_7, ChordQuality.DOMINANT_7,
                       ChordQuality.DIMINISHED_7, ChordQuality.HALF_DIMINISHED_7,
                       ChordQuality.AUGMENTED_7, ChordQuality.MINOR_MAJOR_7],
        "9th Chords": [ChordQuality.MAJOR_9, ChordQuality.MINOR_9, ChordQuality.DOMINANT_9,
                       ChordQuality.DOMINANT_7_FLAT_9, ChordQuality.DOMINANT_7_SHARP_9],
        "11th Chords": [ChordQuality.DOMINANT_11, ChordQuality.MINOR_11, ChordQuality.MAJOR_11],
        "13th Chords": [ChordQuality.DOMINANT_13, ChordQuality.MINOR_13, ChordQuality.MAJOR_13,
                        ChordQuality.DOMINANT_7_FLAT_13],
        "Altered": [ChordQuality.ALTERED, ChordQuality.DOMINANT_7_SHARP_11],
        "Other": [ChordQuality.POWER_CHORD, ChordQuality.MAJOR_6, ChordQuality.MINOR_6,
                  ChordQuality.MAJOR_6_9, ChordQuality.MINOR_6_9],
    }

    root = Note.from_string('C')

    for category, qualities in categories.items():
        print(f"📊 {category}")
        print("-" * 40)
        for quality in qualities:
            chord = Chord(root, quality)
            symbol = chord.to_symbol()
            intervals = quality.value
            print(f"  {symbol:12} {quality.name:25} {intervals}")
        print()


def demo_blues_licks():
    """Demonstrate extensive blues lick database"""
    print_header("BLUES LICKS DATABASE")

    system = MusicRecommendationSystem()

    print("Comprehensive blues licks with techniques:\n")

    key = Note.from_string('A')

    licks = system.lick_recommender.recommend_licks(
        style='blues',
        key=key,
        num_recommendations=10
    )

    for i, rec in enumerate(licks, 1):
        lick = rec.item
        print(f"{i}. {lick['name']} (Score: {rec.score:.2f})")
        print(f"   {rec.explanation}")
        print(f"   Rhythm: {lick['rhythm']}")
        if 'techniques' in lick:
            print(f"   Techniques: {', '.join(lick['techniques'])}")
        print(f"   Notes: {' - '.join(lick['transposed_notes'][:8])}")
        print()


def demo_jazz_licks():
    """Demonstrate extensive jazz lick database"""
    print_header("JAZZ LICKS DATABASE")

    system = MusicRecommendationSystem()

    print("Advanced jazz licks for various chord types:\n")

    key = Note.from_string('D')

    licks = system.lick_recommender.recommend_licks(
        style='jazz',
        key=key,
        num_recommendations=10
    )

    for i, rec in enumerate(licks, 1):
        lick = rec.item
        print(f"{i}. {lick['name']} (Score: {rec.score:.2f})")
        print(f"   {rec.explanation}")
        print(f"   Rhythm: {lick['rhythm']}")
        if 'techniques' in lick:
            print(f"   Techniques: {', '.join(lick['techniques'])}")
        print(f"   Notes: {' - '.join(lick['transposed_notes'][:8])}")
        print()


def demo_specific_chords():
    """Demonstrate specific requested chord types"""
    print_header("SPECIFIC REQUESTED CHORDS")

    print("Examples of the specifically requested chord types:\n")

    examples = [
        ("Dm7", ChordQuality.MINOR_7),
        ("GMaj7", ChordQuality.MAJOR_7),
        ("C7#9", ChordQuality.DOMINANT_7_SHARP_9),
        ("Dm7b5", ChordQuality.HALF_DIMINISHED_7),
        ("Bdim7", ChordQuality.DIMINISHED_7),
        ("E7b9", ChordQuality.DOMINANT_7_FLAT_9),
        ("A7alt", ChordQuality.ALTERED),
        ("F13", ChordQuality.DOMINANT_13),
    ]

    for symbol_desc, quality in examples:
        # Extract root
        root_str = symbol_desc[0]
        if len(symbol_desc) > 1 and symbol_desc[1] in ['#', 'b']:
            root_str = symbol_desc[:2]

        root = Note.from_string(root_str)
        chord = Chord(root, quality)

        intervals = quality.value
        symbol = chord.to_symbol()

        print(f"✓ {symbol:15} Intervals: {intervals}")

    print("\nAll requested chord types are fully supported!")


def main():
    """Run all demonstrations"""
    print("\n" + "="*80)
    print(" 🎵 ADVANCED CHORD SUPPORT DEMONSTRATION 🎵")
    print("="*80)
    print("\nShowcasing:")
    print("  • Extended chords (9ths, 11ths, 13ths)")
    print("  • Altered dominants (7b9, 7#9, 7#11, 7alt)")
    print("  • Half-diminished (m7b5) and diminished chords")
    print("  • Comprehensive blues and jazz lick databases")
    print("="*80)

    demo_specific_chords()
    demo_chord_quality_support()
    demo_advanced_jazz_chords()
    demo_advanced_blues_chords()
    demo_blues_licks()
    demo_jazz_licks()

    # Summary
    print_header("SUMMARY")
    print("The Music Theory ML system now includes:")
    print("  ✓ 32+ chord quality types (triads through 13ths)")
    print("  ✓ Advanced altered dominant chords (7b9, 7#9, 7alt, 7#11)")
    print("  ✓ Half-diminished (m7b5) and diminished 7th support")
    print("  ✓ 10 blues licks with authentic techniques")
    print("  ✓ 10 jazz licks covering bebop, altered scales, and more")
    print("  ✓ Context-aware recommendations for all chord types")
    print("\nAll requested chord types are fully implemented!")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
