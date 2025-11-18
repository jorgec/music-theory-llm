"""
Demonstration of Artist-Specific Licks and Enhanced Features

Shows:
- John Mayer and Josh Smith blues licks
- Eric Johnson and Joe Bonamassa techniques
- Mateus Asato and Lari Basilio neo soul
- Intervals and Plini progressive metal
- Frank Gambale fusion
- Chick Corea, Pat Metheny, Allan Holdsworth jazz
- Architects, Polaris, Invent Animate metalcore
- Increased model parameters and epochs
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.recommender import MusicRecommendationSystem
from src.theory import Note


def print_header(title: str):
    """Print formatted section header"""
    print(f"\\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\\n")


def demo_blues_artists():
    """Demonstrate blues artist licks"""
    print_header("BLUES ARTIST LICKS")

    system = MusicRecommendationSystem()
    key = Note.from_string('A')

    print(f"Blues licks in the style of modern masters (Key of {key.name}):\\n")

    artists = {
        'John Mayer': ['Cascading', 'Hendrix-Blues', 'Chord Melody'],
        'Josh Smith': ['String Bending', 'Blues-Fusion', 'Pentatonic Pivot'],
        'Eric Johnson': ['Violin-Tone', 'Pentatonic Cascades', 'Chord-Melody Hybrid'],
        'Joe Bonamassa': ['Power Blues', 'British Blues', 'String Bending Masterclass']
    }

    licks = system.lick_recommender.recommend_licks(
        style='blues',
        key=key,
        num_recommendations=30  # Get many licks
    )

    for artist, keywords in artists.items():
        print(f"\\n🎸 {artist} Style:")
        print("-" * 70)

        artist_licks = [l for l in licks if any(kw in l.item['name'] for kw in keywords)]

        for lick_rec in artist_licks[:3]:
            lick = lick_rec.item
            print(f"\\n  • {lick['name']}")
            print(f"    {lick_rec.explanation}")
            print(f"    Rhythm: {lick['rhythm']}")
            if 'techniques' in lick:
                print(f"    Techniques: {', '.join(lick['techniques'])}")
            print(f"    Notes: {' - '.join(lick['transposed_notes'][:10])}")


def demo_neo_soul_artists():
    """Demonstrate neo soul artist licks"""
    print_header("NEO SOUL ARTIST LICKS")

    system = MusicRecommendationSystem()
    key = Note.from_string('D')

    print(f"Neo Soul licks in the style of modern virtuosos (Key of {key.name}):\\n")

    artists = {
        'Mateus Asato': ['Chord Melody', 'Pentatonic Extensions', 'Dorian Vamp'],
        'Lari Basilio': ['Fusion Run', 'Chord Stabs', 'Hybrid Picking']
    }

    licks = system.lick_recommender.recommend_licks(
        style='neo_soul',
        key=key,
        num_recommendations=20
    )

    for artist, keywords in artists.items():
        print(f"\\n🎹 {artist} Style:")
        print("-" * 70)

        artist_licks = [l for l in licks if any(kw in l.item['name'] for kw in keywords)]

        for lick_rec in artist_licks:
            lick = lick_rec.item
            print(f"\\n  • {lick['name']}")
            print(f"    {lick_rec.explanation}")
            print(f"    Rhythm: {lick['rhythm']}")
            if 'techniques' in lick:
                print(f"    Techniques: {', '.join(lick['techniques'])}")
            print(f"    Notes: {' - '.join(lick['transposed_notes'][:10])}")


def demo_prog_metal_artists():
    """Demonstrate progressive metal artist licks"""
    print_header("PROGRESSIVE METAL ARTIST LICKS")

    system = MusicRecommendationSystem()
    key = Note.from_string('E')

    print(f"Progressive Metal licks (Key of {key.name}):\\n")

    artists = {
        'Intervals': ['Polymetric Riff', 'Harmonic Minor Shred', 'Melodic Lead'],
        'Plini': ['Hybrid Shred', 'Chord Voicing', 'Cascading Tapping']
    }

    licks = system.lick_recommender.recommend_licks(
        style='progressive_metal',
        key=key,
        num_recommendations=20
    )

    for artist, keywords in artists.items():
        print(f"\\n🎸 {artist} Style:")
        print("-" * 70)

        artist_licks = [l for l in licks if any(kw in l.item['name'] for kw in keywords)]

        for lick_rec in artist_licks:
            lick = lick_rec.item
            print(f"\\n  • {lick['name']}")
            print(f"    {lick_rec.explanation}")
            print(f"    Rhythm: {lick['rhythm']}")
            if 'techniques' in lick:
                print(f"    Techniques: {', '.join(lick['techniques'])}")
            print(f"    Notes: {' - '.join(lick['transposed_notes'][:10])}")


def demo_jazz_fusion_artists():
    """Demonstrate jazz fusion artist licks"""
    print_header("JAZZ FUSION ARTIST LICKS")

    system = MusicRecommendationSystem()
    key = Note.from_string('C')

    print(f"Jazz Fusion licks from the masters (Key of {key.name}):\\n")

    # Jazz artists
    print("🎹 JAZZ LEGENDS:")
    print("-" * 70)

    jazz_artists = {
        'Chick Corea': ['Spanish Phrygian', 'Crystal Silence'],
        'Pat Metheny': ['Wide Interval', 'Bright Size Life', 'Modal Vamp'],
        'Allan Holdsworth': ['Legato Run', 'SUS4 Voicing', 'Chromatic Cascade']
    }

    jazz_licks = system.lick_recommender.recommend_licks(
        style='jazz',
        key=key,
        num_recommendations=30
    )

    for artist, keywords in jazz_artists.items():
        print(f"\\n  {artist}:")
        artist_licks = [l for l in jazz_licks if any(kw in l.item['name'] for kw in keywords)]

        for lick_rec in artist_licks:
            lick = lick_rec.item
            print(f"    • {lick['name']}: {lick_rec.explanation}")
            if 'techniques' in lick:
                print(f"      Techniques: {', '.join(lick['techniques'])}")

    # Fusion artists
    print("\\n\\n🎸 FUSION:")
    print("-" * 70)

    fusion_licks = system.lick_recommender.recommend_licks(
        style='rock_fusion',
        key=key,
        num_recommendations=10
    )

    gambale_licks = [l for l in fusion_licks if 'Gambale' in l.item['name']]

    for lick_rec in gambale_licks:
        lick = lick_rec.item
        print(f"\\n  • {lick['name']}")
        print(f"    {lick_rec.explanation}")
        if 'techniques' in lick:
            print(f"    Techniques: {', '.join(lick['techniques'])}")


def demo_metalcore_artists():
    """Demonstrate metalcore artist licks"""
    print_header("METALCORE ARTIST LICKS")

    system = MusicRecommendationSystem()
    key = Note.from_string('C')

    print(f"Modern Metalcore techniques (Key of {key.name}):\\n")

    artists = {
        'Architects': ['Breakdown Riff', 'Melodic Lead'],
        'Polaris': ['Progressive Riff', 'Ambient Clean'],
        'Invent Animate': ['Dissonant Chord', 'Tapping Sequence']
    }

    licks = system.lick_recommender.recommend_licks(
        style='metalcore',
        key=key,
        num_recommendations=20
    )

    for artist, keywords in artists.items():
        print(f"\\n🔥 {artist} Style:")
        print("-" * 70)

        artist_licks = [l for l in licks if any(kw in l.item['name'] for kw in keywords)]

        for lick_rec in artist_licks:
            lick = lick_rec.item
            print(f"\\n  • {lick['name']}")
            print(f"    {lick_rec.explanation}")
            print(f"    Rhythm: {lick['rhythm']}")
            if 'techniques' in lick:
                print(f"    Techniques: {', '.join(lick['techniques'])}")


def demo_model_parameters():
    """Show updated model parameters and configurations"""
    print_header("ENHANCED MODEL CONFIGURATIONS")

    print("🚀 NEW 100M PARAMETER MODEL:")
    print("-" * 70)
    print("  Target: 100M parameters")
    print("  Architecture: d_model=768, layers=10")
    print("  Training: 100 epochs")
    print("  Use case: Maximum capacity for complex artist-specific patterns")
    print()

    print("🎸 PRIORITY STYLE MODELS (Enhanced):")
    print("-" * 70)

    configs = {
        'Neo Soul': {
            'params': '~37M',
            'd_model': 512,
            'layers': 8,
            'epochs': 150,
            'artists': 'Mateus Asato, Lari Basilio, D\\'Angelo'
        },
        'Blues': {
            'params': '~21M',
            'd_model': 384,
            'layers': 6,
            'epochs': 120,
            'artists': 'John Mayer, Josh Smith, Eric Johnson, Joe Bonamassa'
        },
        'Progressive Metal': {
            'params': '~37M',
            'd_model': 512,
            'layers': 8,
            'epochs': 150,
            'artists': 'Intervals, Plini'
        },
        'Rock Fusion': {
            'params': '~37M',
            'd_model': 512,
            'layers': 8,
            'epochs': 150,
            'artists': 'Frank Gambale, Allan Holdsworth'
        },
        'Jazz': {
            'params': '~37M',
            'd_model': 512,
            'layers': 8,
            'epochs': 150,
            'artists': 'Chick Corea, Pat Metheny, Allan Holdsworth'
        },
        'Metalcore': {
            'params': '~21M',
            'd_model': 384,
            'layers': 6,
            'epochs': 120,
            'artists': 'Architects, Polaris, Invent Animate'
        }
    }

    for style, config in configs.items():
        print(f"\\n  {style}:")
        print(f"    Parameters: {config['params']} (d_model={config['d_model']}, layers={config['layers']})")
        print(f"    Training: {config['epochs']} epochs")
        print(f"    Artists: {config['artists']}")

    print("\\n  Total parameters across priority models: ~190M")


def main():
    """Run all demonstrations"""
    print("\\n" + "="*80)
    print(" 🎸 ARTIST-SPECIFIC LICKS & ENHANCED MODEL DEMO 🎸")
    print("="*80)
    print("\\nShowcasing signature techniques from guitar masters across all styles")
    print("="*80)

    demo_blues_artists()
    demo_neo_soul_artists()
    demo_prog_metal_artists()
    demo_jazz_fusion_artists()
    demo_metalcore_artists()
    demo_model_parameters()

    # Summary
    print_header("SUMMARY OF NEW FEATURES")
    print("Artist-Specific Licks Added:")
    print("  ✓ Blues: John Mayer (3), Josh Smith (3), Eric Johnson (3), Joe Bonamassa (3)")
    print("  ✓ Neo Soul: Mateus Asato (3), Lari Basilio (3)")
    print("  ✓ Progressive Metal: Intervals (3), Plini (3)")
    print("  ✓ Jazz: Chick Corea (2), Pat Metheny (3), Allan Holdsworth (3)")
    print("  ✓ Rock Fusion: Frank Gambale (3)")
    print("  ✓ Metalcore: Architects (2), Polaris (2), Invent Animate (2)")
    print()
    print("Total New Artist Licks: 38")
    print("Total Lick Database: 58+ comprehensive patterns")
    print()
    print("Model Enhancements:")
    print("  ✓ New 100M parameter model (d_model=768, layers=10, epochs=100)")
    print("  ✓ Priority models increased: 384-512 d_model, 6-8 layers")
    print("  ✓ Training epochs increased: 120-150 epochs for better learning")
    print("  ✓ Total capacity: ~290M parameters across all models")
    print()
    print("="*80 + "\\n")


if __name__ == '__main__':
    main()
