"""
Demo: Advanced Harmonic Analysis and Suggestions

This script demonstrates the HarmonicAnalyzer capabilities:
- Passing chord suggestions
- Secondary dominants
- Tritone substitutions
- Modal interchange (borrowed chords)
- Chord extensions
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.theory import Note, Chord, ChordProgression, Scale
from src.utils import HarmonicAnalyzer


def demo_comprehensive_analysis():
    """Demonstrate comprehensive harmonic analysis"""

    print("=" * 80)
    print("COMPREHENSIVE HARMONIC ANALYSIS")
    print("=" * 80)
    print()

    # Create a I-IV-V-I progression in C major
    c_major = Scale.major(Note.from_string('C'))
    progression = ChordProgression.from_degrees([1, 4, 5, 1], c_major)

    print("Original Progression:")
    print(progression)
    print()

    analyzer = HarmonicAnalyzer()
    analysis = analyzer.analyze_progression(progression)

    print("Basic Analysis:")
    print(f"  Key: {analysis['key']} {analysis['scale_type']}")
    print(f"  Number of chords: {analysis['num_chords']}")
    print(f"  Cadence type: {analysis['cadence_type']}")
    print(f"  Roman numerals: {' - '.join(analysis['roman_numerals'])}")
    print(f"  Harmonic functions: {' → '.join(analysis['harmonic_functions'])}")
    print()

    return analysis


def demo_passing_chords():
    """Demonstrate passing chord suggestions"""

    print("\n" + "=" * 80)
    print("PASSING CHORD SUGGESTIONS")
    print("=" * 80)
    print()

    # Create progression with larger intervals
    c_major = Scale.major(Note.from_string('C'))
    progression = ChordProgression.from_degrees([1, 6, 4, 5], c_major)

    print("Original Progression:")
    print(progression)
    print()

    analyzer = HarmonicAnalyzer()
    passing_chords = analyzer.suggest_passing_chords(progression)

    print(f"Found {len(passing_chords)} passing chord suggestions:")
    print("-" * 80)

    for i, suggestion in enumerate(passing_chords, 1):
        print(f"\nSuggestion {i}:")
        print(f"  Chord: {suggestion.chord}")
        print(f"  Insert between positions: {suggestion.position[0]} and {suggestion.position[1]}")
        print(f"  Type: {suggestion.suggestion_type}")
        print(f"  Description: {suggestion.description}")
        print(f"  Voice Leading Quality: {suggestion.voice_leading_quality}/5")

    print()


def demo_secondary_dominants():
    """Demonstrate secondary dominant suggestions"""

    print("\n" + "=" * 80)
    print("SECONDARY DOMINANT SUGGESTIONS")
    print("=" * 80)
    print()

    # Create a simple progression
    g_major = Scale.major(Note.from_string('G'))
    progression = ChordProgression.from_degrees([1, 2, 5, 1], g_major)

    print("Original Progression (G major):")
    print(progression)
    print()

    analyzer = HarmonicAnalyzer()
    secondary_doms = analyzer.suggest_secondary_dominants(progression)

    print(f"Found {len(secondary_doms)} secondary dominant suggestions:")
    print("-" * 80)

    for i, suggestion in enumerate(secondary_doms[:5], 1):  # Show first 5
        print(f"\nSuggestion {i}:")
        print(f"  Chord: {suggestion.chord}")
        print(f"  Insert at position: {suggestion.position}")
        print(f"  Description: {suggestion.description}")
        print(f"  Voice Leading Quality: {suggestion.voice_leading_quality}/5")

    print()


def demo_tritone_substitutions():
    """Demonstrate tritone substitution suggestions"""

    print("\n" + "=" * 80)
    print("TRITONE SUBSTITUTION SUGGESTIONS")
    print("=" * 80)
    print()

    # Create progression with dominant chords
    c_major = Scale.major(Note.from_string('C'))

    # Manually create progression with 7th chords
    chords = [
        Chord.from_symbol('C'),
        Chord.from_symbol('G7'),  # Dominant 7th
        Chord.from_symbol('C')
    ]
    progression = ChordProgression(chords, c_major)

    print("Original Progression:")
    print(progression)
    print()

    analyzer = HarmonicAnalyzer()
    tritone_subs = analyzer.suggest_tritone_substitutions(progression)

    print(f"Found {len(tritone_subs)} tritone substitution suggestions:")
    print("-" * 80)

    for i, suggestion in enumerate(tritone_subs, 1):
        print(f"\nSuggestion {i}:")
        print(f"  Replace: {progression.chords[suggestion.position[0]]}")
        print(f"  With: {suggestion.chord}")
        print(f"  Description: {suggestion.description}")
        print(f"  Voice Leading Quality: {suggestion.voice_leading_quality}/5")

    print()


def demo_modal_interchange():
    """Demonstrate modal interchange (borrowed chords)"""

    print("\n" + "=" * 80)
    print("MODAL INTERCHANGE (BORROWED CHORDS)")
    print("=" * 80)
    print()

    # C major progression
    c_major = Scale.major(Note.from_string('C'))
    progression = ChordProgression.from_degrees([1, 4, 5, 1], c_major)

    print("Original Progression (C major):")
    print(progression)
    print()

    analyzer = HarmonicAnalyzer()
    borrowed_chords = analyzer.suggest_modal_interchange(progression)

    print(f"Found {len(borrowed_chords)} modal interchange suggestions:")
    print("-" * 80)
    print("\nShowing common borrowed chords from parallel minor:")

    # Group by chord type
    unique_chords = {}
    for suggestion in borrowed_chords:
        chord_str = str(suggestion.chord)
        if chord_str not in unique_chords:
            unique_chords[chord_str] = suggestion

    for i, (chord_str, suggestion) in enumerate(unique_chords.items(), 1):
        print(f"\n{i}. {suggestion.chord}")
        print(f"   {suggestion.description}")

    print()


def demo_chord_extensions():
    """Demonstrate chord extension suggestions"""

    print("\n" + "=" * 80)
    print("CHORD EXTENSION SUGGESTIONS")
    print("=" * 80)
    print()

    # Create a jazz-style progression
    d_minor = Scale.minor(Note.from_string('D'))
    chords = [
        Chord.from_symbol('Dm7'),
        Chord.from_symbol('G7'),
        Chord.from_symbol('Cmaj7'),
    ]
    progression = ChordProgression(chords, d_minor)

    print("Original Progression (ii-V-I in C):")
    for i, chord in enumerate(progression.chords):
        print(f"  {i + 1}. {chord}")
    print()

    analyzer = HarmonicAnalyzer()
    extensions = analyzer.suggest_chord_extensions(progression)

    print("Extension Suggestions:")
    print("-" * 80)

    for chord_ext in extensions:
        print(f"\n{chord_ext['position'] + 1}. {chord_ext['original_chord']}:")
        print("   Suggested extensions:")
        for ext in chord_ext['extensions'][:3]:  # Show top 3
            print(f"   • {ext['extension']}: {ext['description']}")

    print()


def demo_voice_leading_analysis():
    """Demonstrate voice leading analysis between chords"""

    print("\n" + "=" * 80)
    print("VOICE LEADING ANALYSIS")
    print("=" * 80)
    print()

    analyzer = HarmonicAnalyzer()

    # Example 1: Good voice leading (common tones)
    chord1 = Chord.from_symbol('C')
    chord2 = Chord.from_symbol('Am')

    print("Example 1: C → Am")
    print(f"  {chord1} → {chord2}")

    analysis = analyzer.analyze_voice_leading(chord1, chord2)

    print(f"\n  Common tones: {[str(n) for n in analysis['common_tones']]}")
    print(f"  Total voice motion: {analysis['total_motion']} semitones")
    print(f"  Average motion per voice: {analysis['avg_motion']:.2f} semitones")
    print(f"  Smooth voice leading: {'Yes' if analysis['smooth'] else 'No'}")
    print("\n  Voice movements:")
    for movement in analysis['voice_movements']:
        print(f"    {movement['from']} → {movement['to']} ({movement['distance']} semitones)")

    # Example 2: Less smooth voice leading
    print("\n" + "-" * 80)
    chord3 = Chord.from_symbol('C')
    chord4 = Chord.from_symbol('F#')

    print("\nExample 2: C → F# (tritone apart)")
    print(f"  {chord3} → {chord4}")

    analysis2 = analyzer.analyze_voice_leading(chord3, chord4)

    print(f"\n  Common tones: {[str(n) for n in analysis2['common_tones']]}")
    print(f"  Total voice motion: {analysis2['total_motion']} semitones")
    print(f"  Average motion per voice: {analysis2['avg_motion']:.2f} semitones")
    print(f"  Smooth voice leading: {'Yes' if analysis2['smooth'] else 'No'}")

    print()


def demo_complete_reharmonization():
    """Demonstrate a complete reharmonization workflow"""

    print("\n" + "=" * 80)
    print("COMPLETE REHARMONIZATION WORKFLOW")
    print("=" * 80)
    print()

    # Start with simple progression
    c_major = Scale.major(Note.from_string('C'))
    progression = ChordProgression.from_degrees([1, 6, 4, 5], c_major)

    print("Original Simple Progression:")
    print(progression)
    print()

    analyzer = HarmonicAnalyzer()

    print("Reharmonization Ideas:")
    print("-" * 80)

    # Get all suggestions
    passing = analyzer.suggest_passing_chords(progression)
    secondary = analyzer.suggest_secondary_dominants(progression)
    borrowed = analyzer.suggest_modal_interchange(progression)

    print("\n1. Add passing chords:")
    if passing:
        for sugg in passing[:2]:
            print(f"   • Insert {sugg.chord} between positions {sugg.position}")

    print("\n2. Add secondary dominants:")
    if secondary:
        for sugg in secondary[:2]:
            print(f"   • Insert {sugg.chord} before position {sugg.position[1]}")

    print("\n3. Try borrowed chords:")
    unique_borrowed = {}
    for sugg in borrowed:
        chord_str = str(sugg.chord)
        if chord_str not in unique_borrowed:
            unique_borrowed[chord_str] = sugg
            if len(unique_borrowed) <= 3:
                print(f"   • Try {sugg.chord}: {sugg.description.split(':')[1].strip()}")

    print("\n4. Add extensions to make it jazzier:")
    extensions = analyzer.suggest_chord_extensions(progression)
    if extensions:
        for chord_ext in extensions[:2]:
            ext = chord_ext['extensions'][0]
            print(f"   • {chord_ext['original_chord']} → {ext['extension']}")

    print()


if __name__ == '__main__':
    demo_comprehensive_analysis()
    demo_passing_chords()
    demo_secondary_dominants()
    demo_tritone_substitutions()
    demo_modal_interchange()
    demo_chord_extensions()
    demo_voice_leading_analysis()
    demo_complete_reharmonization()

    print("=" * 80)
    print("✓ Harmonic analysis demo completed!")
    print()
    print("Key Features Demonstrated:")
    print("  • Comprehensive progression analysis")
    print("  • Passing chord suggestions (chromatic & diatonic)")
    print("  • Secondary dominants (V/x)")
    print("  • Tritone substitutions")
    print("  • Modal interchange (borrowed chords)")
    print("  • Chord extensions (9, 11, 13)")
    print("  • Voice leading analysis")
    print("  • Complete reharmonization workflow")
    print("=" * 80)
