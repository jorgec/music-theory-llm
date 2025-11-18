"""
Demonstration of Eric Johnson and Greg Howe Techniques

Shows:
- Eric Johnson's signature techniques:
  * Open-voiced triads with open strings
  * Add9 and 6/9 voicings
  * Lydian and Mixolydian color voicings
  * String-skipping arpeggios
  * Pentatonic arpeggio patterns
  * Hybrid picking rolls
  * Chord-arpeggio fusion
  * Triad soloing up the neck

- Greg Howe's signature fusion techniques:
  * Fluid legato cascades
  * Two-hand tapping
  * Chromatic fusion lines
  * Sweep-tap hybrids
  * Modal superimposition
  * Intervallic sequences
  * Rock-jazz fusion phrases
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.guitar import EricJohnsonVoicings, GuitarTablature, NeckVisualization
from src.recommender import MusicRecommendationSystem
from src.theory import Note


def print_header(title: str):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\n")


def demo_eric_johnson_voicings():
    """Demonstrate Eric Johnson's signature chord voicings"""
    print_header("ERIC JOHNSON SIGNATURE VOICINGS")

    root = Note.from_string('G')
    tab = GuitarTablature()

    print("🎸 Eric Johnson's Open-Voiced Triads\n")
    print("Using open strings as color tones for shimmer and resonance:\n")

    # Open-voiced triad with open strings
    voicing = EricJohnsonVoicings.get_open_voiced_triad(root, position=3, use_open_strings=True)
    print(tab.generate_chord_diagram(voicing))
    print("\nThis voicing uses open B and E strings to create EJ's signature open sound")
    print("-" * 80)

    print("\n\n🎹 Eric Johnson Add9 Voicing\n")
    print("The add9 chord is a signature Eric Johnson sound:\n")

    voicing = EricJohnsonVoicings.get_add9_voicing(root, position=3, use_open_strings=True)
    print(tab.generate_chord_diagram(voicing))
    print("\nAdd9 chords (1-3-5-9) create the bright, shimmering texture EJ is famous for")
    print("-" * 80)

    print("\n\n🎼 Eric Johnson 6/9 Voicing\n")
    print("Lush, jazzy 6/9 voicings:\n")

    voicing = EricJohnsonVoicings.get_6_9_voicing(root, position=7)
    print(tab.generate_chord_diagram(voicing))
    print("\n6/9 chords combine major 6th and major 9th for sophisticated textures")
    print("-" * 80)


def demo_eric_johnson_modal_colors():
    """Demonstrate Eric Johnson's modal color voicings"""
    print_header("ERIC JOHNSON MODAL COLORS")

    root = Note.from_string('C')
    tab = GuitarTablature()

    print("☀️ Lydian Color Voicing - 'Cliffs of Dover' Sound\n")
    print("Lydian mode with raised 4th (#11) creates bright, uplifting textures:\n")

    voicing = EricJohnsonVoicings.get_lydian_color_voicing(root, position=5)
    print(tab.generate_chord_diagram(voicing))
    print("\nLydian's #11 (raised 4th) is the signature sound of 'Cliffs of Dover'")
    print("-" * 80)

    print("\n\n🎵 Mixolydian Color Voicing\n")
    print("Mixolydian mode (major with b7) for bluesy-rock textures:\n")

    voicing = EricJohnsonVoicings.get_mixolydian_color_voicing(root, position=5)
    print(tab.generate_chord_diagram(voicing))
    print("\nMixolydian creates the perfect blend of major brightness and blues feel")
    print("-" * 80)


def demo_eric_johnson_techniques():
    """Demonstrate Eric Johnson's playing techniques"""
    print_header("ERIC JOHNSON PLAYING TECHNIQUES")

    root = Note.from_string('E')

    print("🎼 String-Skipping Arpeggios\n")
    print("Creates open, harp-like sounds by skipping strings:\n")

    arpeggio = EricJohnsonVoicings.get_string_skipping_arpeggio(root, position=7)
    for i, note in enumerate(arpeggio, 1):
        print(f"  {i}. String {note.string + 1}, Fret {note.fret:2d} - {note.note.name}")
    print("\nSkipping strings creates wider intervals and more open voicings")
    print("-" * 80)

    print("\n\n🎸 Pentatonic 'Arpeggio-like' Patterns\n")
    print("Blending pentatonic scales with arpeggio approaches:\n")

    pattern = EricJohnsonVoicings.get_pentatonic_arpeggio_pattern(root, position=5)
    for i, note in enumerate(pattern, 1):
        print(f"  {i}. String {note.string + 1}, Fret {note.fret:2d} - {note.note.name}")
    print("\nMajor pentatonic (1-2-3-5-6) played as arpeggiated pattern")
    print("-" * 80)

    print("\n\n🖐️ Hybrid Picking 'Rolls'\n")
    print("Pick + fingers creating cascading patterns:\n")

    roll = EricJohnsonVoicings.get_hybrid_picking_roll(root, position=5)
    techniques = ['Pick', 'Middle finger', 'Ring finger', 'Middle finger', 'Pick']
    for i, (note, tech) in enumerate(zip(roll, techniques), 1):
        print(f"  {i}. String {note.string + 1}, Fret {note.fret:2d} ({tech})")
    print("\nTypical pick-middle-ring-middle pattern creates harp-like cascades")
    print("-" * 80)

    print("\n\n🎶 Chord-Arpeggio Fusion\n")
    print("Seamlessly blending strummed chords with arpeggiated notes:\n")

    fusion = EricJohnsonVoicings.get_chord_arpeggio_fusion(root, position=5)
    for i, note in enumerate(fusion, 1):
        marker = " (CHORD)" if i in [1, 2, 3, 6, 7] else " (ARPEGGIO)"
        print(f"  {i}. String {note.string + 1}, Fret {note.fret:2d}{marker}")
    print("\nAlternates between chord stabs and single-note lines")
    print("-" * 80)


def demo_eric_johnson_triad_soloing():
    """Demonstrate Eric Johnson's triad soloing approach"""
    print_header("ERIC JOHNSON TRIAD SOLOING")

    root = Note.from_string('D')

    print("Using triads melodically as if soloing with single notes\n")
    print("Moving through inversions up the neck:\n")

    voicings = EricJohnsonVoicings.get_triad_soloing_pattern(root, position=5)

    inversion_names = ['Root Position', 'First Inversion', 'Second Inversion']

    for i, voicing in enumerate(voicings, 1):
        inv_name = inversion_names[voicing.inversion]
        print(f"\n{i}. Position {voicing.position} - {inv_name}")
        for note in voicing.notes:
            print(f"   String {note.string + 1}, Fret {note.fret:2d}")

    print("\nThis creates melodic movement while maintaining full harmonic support")
    print("-" * 80)


def demo_greg_howe_licks():
    """Demonstrate Greg Howe fusion licks"""
    print_header("GREG HOWE FUSION TECHNIQUES")

    system = MusicRecommendationSystem()
    key = Note.from_string('A')

    print("Greg Howe's signature rock-jazz fusion techniques\n")
    print(f"Key of {key.name} - Fusion Style\n")

    # Get all fusion licks
    licks = system.lick_recommender.recommend_licks(
        style='rock_fusion',
        key=key,
        num_recommendations=15
    )

    # Filter for Greg Howe licks
    greg_howe_licks = [l for l in licks if 'Greg Howe' in l.item['name']]

    if not greg_howe_licks:
        print("No Greg Howe licks found - showing all fusion licks")
        greg_howe_licks = licks[:7]

    for i, lick_rec in enumerate(greg_howe_licks, 1):
        lick = lick_rec.item
        print(f"\n{i}. {lick['name']}")
        print(f"   Score: {lick_rec.score:.3f}")
        print(f"   {lick_rec.explanation}")
        print(f"   Rhythm: {lick['rhythm']}")
        if 'techniques' in lick:
            print(f"   Techniques: {', '.join(lick['techniques'])}")
        print(f"   Intervals: {lick['intervals']}")
        print(f"   Notes: {' - '.join(lick['transposed_notes'][:10])}")
        print("   " + "-" * 76)


def demo_blues_eric_johnson_licks():
    """Demonstrate Eric Johnson blues licks"""
    print_header("ERIC JOHNSON BLUES LICKS")

    system = MusicRecommendationSystem()
    key = Note.from_string('A')

    print(f"Eric Johnson's signature blues approach in {key.name}\n")

    # Get blues licks
    licks = system.lick_recommender.recommend_licks(
        style='blues',
        key=key,
        num_recommendations=30
    )

    # Filter for Eric Johnson licks
    ej_licks = [l for l in licks if 'Eric Johnson' in l.item['name']]

    for i, lick_rec in enumerate(ej_licks, 1):
        lick = lick_rec.item
        print(f"\n{i}. {lick['name']}")
        print(f"   Score: {lick_rec.score:.3f}")
        print(f"   {lick_rec.explanation}")
        print(f"   Rhythm: {lick['rhythm']}")
        if 'techniques' in lick:
            print(f"   Techniques: {', '.join(lick['techniques'])}")
        print(f"   Notes: {' - '.join(lick['transposed_notes'][:12])}")
        print("   " + "-" * 76)


def demo_enhanced_training_configs():
    """Show enhanced training configurations"""
    print_header("ENHANCED TRAINING CONFIGURATIONS")

    print("🚀 OPTIMIZED FOR ARTIST-SPECIFIC NUANCES\n")
    print("-" * 80)

    configs = {
        'Blues (Eric Johnson Focus)': {
            'params': '~35M',
            'd_model': 448,
            'layers': 7,
            'epochs': 160,
            'artists': 'John Mayer, Josh Smith, Eric Johnson, Joe Bonamassa',
            'specialty': 'Eric Johnson open voicings, add9, intervallic chords'
        },
        'Rock Fusion (Greg Howe HIGH PRIORITY)': {
            'params': '~55M',
            'd_model': 640,
            'layers': 10,
            'epochs': 200,
            'artists': 'Greg Howe, Frank Gambale, Allan Holdsworth',
            'specialty': 'Greg Howe legato, tapping, chromatic fusion - HIGHEST priority'
        },
        'Neo Soul': {
            'params': '~45M',
            'd_model': 576,
            'layers': 9,
            'epochs': 180,
            'artists': 'Mateus Asato, Lari Basilio',
            'specialty': 'Extended voicings, ambient textures'
        },
        'Jazz': {
            'params': '~45M',
            'd_model': 576,
            'layers': 9,
            'epochs': 180,
            'artists': 'Chick Corea, Pat Metheny, Allan Holdsworth',
            'specialty': 'Advanced harmony, altered scales'
        },
        'Progressive Metal': {
            'params': '~45M',
            'd_model': 576,
            'layers': 9,
            'epochs': 180,
            'artists': 'Intervals, Plini',
            'specialty': 'Polymetric riffs, technical complexity'
        },
        'Metalcore': {
            'params': '~32M',
            'd_model': 448,
            'layers': 7,
            'epochs': 160,
            'artists': 'Architects, Polaris, Invent Animate',
            'specialty': 'Modern breakdowns, atmospheric sections'
        },
    }

    for style, config in configs.items():
        print(f"\n📊 {style}")
        print(f"   Parameters: {config['params']} (d_model={config['d_model']}, layers={config['layers']})")
        print(f"   Training: {config['epochs']} epochs")
        print(f"   Artists: {config['artists']}")
        print(f"   Specialty: {config['specialty']}")

    print("\n\nTotal combined parameters: ~257M")
    print("Training emphasis: Greg Howe (200 epochs), Eric Johnson techniques integrated\n")
    print("-" * 80)


def main():
    """Run all demonstrations"""
    print("\n" + "="*80)
    print(" 🎸 ERIC JOHNSON & GREG HOWE TECHNIQUES DEMO 🎸")
    print("="*80)
    print("\nShowcasing signature techniques from two fusion masters:")
    print("  • Eric Johnson: Open voicings, modal colors, hybrid picking")
    print("  • Greg Howe: Legato mastery, tapping, chromatic fusion")
    print("="*80)

    # Eric Johnson demonstrations
    demo_eric_johnson_voicings()
    demo_eric_johnson_modal_colors()
    demo_eric_johnson_techniques()
    demo_eric_johnson_triad_soloing()
    demo_blues_eric_johnson_licks()

    # Greg Howe demonstrations
    demo_greg_howe_licks()

    # Training configs
    demo_enhanced_training_configs()

    # Summary
    print_header("SUMMARY OF ENHANCEMENTS")
    print("Eric Johnson Techniques Added:")
    print("  ✓ Open-voiced triads with open string color tones")
    print("  ✓ Add9 and 6/9 voicings")
    print("  ✓ Lydian and Mixolydian modal colors")
    print("  ✓ String-skipping arpeggios")
    print("  ✓ Pentatonic arpeggio-like patterns")
    print("  ✓ Hybrid picking rolls")
    print("  ✓ Chord-arpeggio fusion")
    print("  ✓ Triad soloing patterns")
    print()
    print("Greg Howe Licks Added (HIGH PRIORITY):")
    print("  ✓ Fluid legato cascades (7 licks)")
    print("  ✓ Two-hand tapping sequences")
    print("  ✓ Chromatic fusion lines")
    print("  ✓ Sweep-tap hybrid techniques")
    print("  ✓ Modal superimposition")
    print("  ✓ Intervallic sequences")
    print("  ✓ Rock-jazz fusion phrases")
    print()
    print("Training Optimizations:")
    print("  ✓ Blues: 448 d_model, 7 layers, 160 epochs (Eric Johnson focus)")
    print("  ✓ Rock Fusion: 640 d_model, 10 layers, 200 epochs (Greg Howe HIGH PRIORITY)")
    print("  ✓ All styles: Enhanced parameters, extended epochs, optimized learning rates")
    print("  ✓ Total model capacity: ~257M parameters across all priority styles")
    print()
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
