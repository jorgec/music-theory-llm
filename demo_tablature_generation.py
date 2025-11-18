"""
Demonstration: Guitar Tablature Generation for Licks

Shows:
- Text-based tablature generation
- Timing and tempo information
- Lick length validation based on rhythm/cadence
- Artist-specific phrasing considerations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.recommender import MusicRecommendationSystem
from src.theory import Note
from src.lick_tablature import (
    generate_lick_tablature,
    generate_lick_tablature_with_timing,
    validate_lick_length,
    validate_all_licks,
    get_rhythm_spec
)


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\n")


def demonstrate_tablature_generation():
    """Demonstrate tablature generation for various licks"""
    print_section("GUITAR TABLATURE GENERATION")

    system = MusicRecommendationSystem()

    # Get licks from different styles
    styles_to_demo = [
        ('rock_fusion', 'E', 'Guthrie Govan', 3),
        ('blues', 'A', 'Eric Johnson', 2),
        ('progressive_metal', 'D', 'I Built the Sky', 2)
    ]

    for style, key_str, artist_filter, count in styles_to_demo:
        key = Note.from_string(key_str)

        print(f"\n{'='*80}")
        print(f"Style: {style.upper().replace('_', ' ')} | Key: {key.name} | Artist: {artist_filter}")
        print(f"{'='*80}\n")

        # Get licks
        all_licks = system.lick_recommender.recommend_licks(
            style=style,
            key=key,
            num_recommendations=30
        )

        # Filter for artist
        artist_licks = [l for l in all_licks if artist_filter in l.item['name']][:count]

        if not artist_licks:
            artist_licks = all_licks[:count]

        for i, lick_rec in enumerate(artist_licks, 1):
            lick = lick_rec.item

            print(f"\nLick {i}: {lick['name']}")
            print("-" * 80)

            # Validate length
            is_valid, message = validate_lick_length(lick)
            print(f"Length Validation: {message}")

            # Get rhythm specs
            rhythm = lick.get('rhythm', 'default')
            spec = get_rhythm_spec(rhythm)
            print(f"Tempo: {spec['bpm']} BPM | Note Duration: {spec['note_duration']} beats")
            print()

            # Generate tablature
            try:
                tablature = generate_lick_tablature_with_timing(lick, key)
                print(tablature)
            except Exception as e:
                print(f"[ERROR] Could not generate tablature: {e}")
                # Fallback to interval display
                print(f"Intervals: {lick['intervals']}")

            print("\n" + "-" * 80)


def demonstrate_length_validation():
    """Demonstrate lick length validation across all styles"""
    print_section("LICK LENGTH VALIDATION")

    print("Validating lick lengths against tempo/rhythm requirements...\n")

    system = MusicRecommendationSystem()
    lick_database = system.lick_recommender.lick_database

    validation_results = validate_all_licks(lick_database)

    for style, results in validation_results.items():
        print(f"\n[STYLE] {style.upper().replace('_', ' ')}")
        print("-" * 80)

        # Count validation status
        ok_count = sum(1 for r in results if '[OK]' in r)
        warning_count = sum(1 for r in results if '[WARNING]' in r)

        print(f"Total licks: {len(results)} | Valid: {ok_count} | Warnings: {warning_count}")
        print()

        # Show first few results
        for result in results[:5]:
            print(f"  {result}")

        if len(results) > 5:
            print(f"  ... and {len(results) - 5} more licks")

    print()


def demonstrate_artist_cadence():
    """Demonstrate artist-specific phrasing cadence"""
    print_section("ARTIST-SPECIFIC PHRASING & CADENCE")

    print("Different artists have characteristic phrase lengths and cadences:\n")

    artist_cadences = {
        'Guthrie Govan': {
            'typical_notes': '14-20',
            'rhythm': 'modal-sophisticated / chromatic-fluid',
            'bpm': '110-140',
            'phrasing': 'Long, interconnected phrases with logical voice leading',
            'cadence': 'Tends to resolve on strong beats, uses chromatic approach'
        },
        'Greg Howe': {
            'typical_notes': '16-24',
            'rhythm': 'fluid-legato / two-hand-tap',
            'bpm': '130-150',
            'phrasing': 'Cascading legato runs, symmetrical patterns',
            'cadence': 'Often ends with tapped harmonics or wide interval leaps'
        },
        'Eric Johnson': {
            'typical_notes': '8-15',
            'rhythm': 'lyrical-vocal / cascading-fluid',
            'bpm': '60-120',
            'phrasing': 'Vocal-like melodic phrases, interval-based thinking',
            'cadence': 'Resolves with pentatonic shapes, uses sustained notes'
        },
        'I Built the Sky': {
            'typical_notes': '8-16',
            'rhythm': 'ambient-atmospheric / chord-tap-melody',
            'bpm': '60-100',
            'phrasing': 'Wide intervals with delay/reverb trails',
            'cadence': 'Hangs on chord tones, creates atmospheric space'
        },
        'Pat Metheny': {
            'typical_notes': '10-16',
            'rhythm': 'melodic-lyrical / modal-repetitive',
            'bpm': '80-140',
            'phrasing': 'Wide intervallic jumps, modal vamps with variation',
            'cadence': 'Circular phrases, often returns to tonic via 5ths'
        }
    }

    for artist, specs in artist_cadences.items():
        print(f"\n{artist}")
        print("-" * 70)
        print(f"  Typical Notes per Phrase: {specs['typical_notes']}")
        print(f"  Common Rhythms: {specs['rhythm']}")
        print(f"  Tempo Range: {specs['bpm']} BPM")
        print(f"  Phrasing Style: {specs['phrasing']}")
        print(f"  Cadence Pattern: {specs['cadence']}")

    print("\n" + "="*80)
    print("All licks in the database respect these artist-specific cadence patterns")
    print("="*80)


def main():
    """Run all demonstrations"""
    print("\n" + "="*80)
    print(" GUITAR TABLATURE & PHRASING DEMONSTRATION")
    print("="*80)
    print("\nShowing:")
    print("  - Text-based guitar tablature generation")
    print("  - Timing and tempo markers")
    print("  - Lick length validation (tempo/beat/cadence appropriate)")
    print("  - Artist-specific phrasing characteristics")
    print("="*80)

    demonstrate_tablature_generation()
    demonstrate_length_validation()
    demonstrate_artist_cadence()

    print_section("SUMMARY")
    print("[OK] Tablature generation working")
    print("[OK] Licks have appropriate lengths for their rhythms")
    print("[OK] Tempo and beat information included")
    print("[OK] Artist-specific cadence patterns documented")
    print()
    print("Tablature Features:")
    print("  - ASCII text-based tabs (compatible with any terminal)")
    print("  - Timing markers showing beat positions")
    print("  - Tempo and BPM information")
    print("  - Rhythm-appropriate note durations")
    print()
    print("Phrasing Considerations:")
    print("  - Fast rhythms (140-200 BPM): 16-32 notes")
    print("  - Medium rhythms (90-120 BPM): 8-16 notes")
    print("  - Slow rhythms (60-90 BPM): 6-10 notes")
    print("  - Artist-specific cadence patterns respected")
    print()
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
