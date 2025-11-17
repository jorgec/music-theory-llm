"""
Demo: Melody Suggestion System

This script demonstrates how to use the MelodySuggester to generate
intelligent melodic continuations given a chord progression and partial melody.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.theory import Note, Pitch, Chord, ChordProgression, Scale
from src.utils import MelodySuggester


def demo_melody_suggestions():
    """Demonstrate melody suggestion capabilities"""

    print("=" * 80)
    print("MELODY SUGGESTION DEMO")
    print("=" * 80)
    print()

    # Create a chord progression: I - V - vi - IV in C major
    c_major = Scale.major(Note.from_string('C'))
    progression = ChordProgression.from_degrees([1, 5, 6, 4], c_major)

    print("Chord Progression:")
    print(progression)
    print()

    # Create a partial melody
    partial_melody = [
        Pitch.from_string('E4'),
        Pitch.from_string('D4'),
        Pitch.from_string('C4'),
    ]

    print("Partial Melody:")
    print(" -> ".join(str(p) for p in partial_melody))
    print()

    # Create melody suggester
    suggester = MelodySuggester()

    # Get suggestions for continuing the melody
    print("\nGENERATING MELODIC CONTINUATIONS...")
    print("-" * 80)

    suggestions = suggester.suggest_continuations(
        partial_melody=partial_melody,
        progression=progression,
        current_chord_idx=1,  # Currently on the V chord
        num_suggestions=4,
        num_notes=4
    )

    for i, option in enumerate(suggestions, 1):
        print(f"\nOption {i}:")
        print(f"  Notes: {' -> '.join(str(p) for p in option.pitches)}")
        print(f"  Description: {option.description}")
        print(f"  Tension: {option.tension_trajectory}")
        print(f"  Voice Leading Quality: {option.voice_leading_quality}/5")

    print()
    print("=" * 80)


def demo_melody_harmony_analysis():
    """Demonstrate melody-harmony fit analysis"""

    print("\n" + "=" * 80)
    print("MELODY-HARMONY FIT ANALYSIS")
    print("=" * 80)
    print()

    # Create a melody over a C major chord
    melody = [
        Pitch.from_string('E4'),  # Chord tone (3rd)
        Pitch.from_string('F4'),  # Non-chord tone
        Pitch.from_string('G4'),  # Chord tone (5th)
        Pitch.from_string('A4'),  # Non-chord tone
        Pitch.from_string('G4'),  # Chord tone (5th)
        Pitch.from_string('E4'),  # Chord tone (3rd)
        Pitch.from_string('C4'),  # Chord tone (root)
    ]

    chord = Chord.from_symbol('C')

    print(f"Analyzing melody over {chord} chord:")
    print(f"Melody: {' - '.join(str(p) for p in melody)}")
    print()

    suggester = MelodySuggester()
    analysis = suggester.analyze_melody_harmony_fit(melody, chord)

    print("Analysis:")
    print(f"  Chord tones: {len(analysis['chord_tones'])} notes")
    for idx, pitch in analysis['chord_tones']:
        print(f"    Position {idx}: {pitch}")

    print(f"\n  Non-chord tones: {len(analysis['non_chord_tones'])} notes")
    for idx, pitch in analysis['non_chord_tones']:
        print(f"    Position {idx}: {pitch} (creates tension)")

    print(f"\n  Average tension: {analysis['avg_tension']:.2f}")
    print(f"  Tension points at positions: {analysis['tension_points']}")

    print()
    print("=" * 80)


def demo_starting_melody():
    """Demonstrate starting melody generation"""

    print("\n" + "=" * 80)
    print("STARTING MELODY GENERATION")
    print("=" * 80)
    print()

    # Create a progression in G major
    g_major = Scale.major(Note.from_string('G'))
    progression = ChordProgression.from_degrees([1, 4, 1, 5], g_major)

    print("Chord Progression (G major):")
    print(progression)
    print()

    suggester = MelodySuggester()

    print("Generating starting melodies for the first chord:")
    print("-" * 80)

    # Get starting melody suggestions
    suggestions = suggester.suggest_continuations(
        partial_melody=[],  # Empty - asking for starting melodies
        progression=progression,
        current_chord_idx=0,
        num_suggestions=3,
        num_notes=4
    )

    for i, option in enumerate(suggestions, 1):
        print(f"\nStarting Option {i}:")
        print(f"  Notes: {' -> '.join(str(p) for p in option.pitches)}")
        print(f"  Description: {option.description}")

    print()
    print("=" * 80)


if __name__ == '__main__':
    demo_melody_suggestions()
    demo_melody_harmony_analysis()
    demo_starting_melody()

    print("\n✓ Melody suggestion demo completed!")
    print("\nKey Features Demonstrated:")
    print("  • Intelligent melodic continuation with multiple options")
    print("  • Stepwise motion for smooth voice leading")
    print("  • Leaps with resolution for dramatic effect")
    print("  • Approach note patterns for tension-release")
    print("  • Arpeggiated patterns emphasizing harmony")
    print("  • Melody-harmony fit analysis")
    print("  • Starting melody generation")
