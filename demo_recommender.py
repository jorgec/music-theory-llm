"""
Demonstration of the Music Theory Recommendation System

Shows how to get recommendations for:
- Chord progressions
- Melodies
- Licks and riffs

Focused on priority styles: neo soul, blues, progressive metal, rock fusion
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.recommender import MusicRecommendationSystem
from src.theory import Note


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}\n")


def demo_progression_recommendations():
    """Demonstrate chord progression recommendations"""
    print_section("CHORD PROGRESSION RECOMMENDATIONS")

    system = MusicRecommendationSystem()

    # Test priority styles
    priority_styles = ['neo_soul', 'blues', 'progressive_metal', 'rock_fusion']
    key = Note.from_string('C')

    for style in priority_styles:
        print(f"\n🎵 {style.upper().replace('_', ' ')} in {key.name}")
        print("-" * 70)

        try:
            recommendations = system.progression_recommender.recommend_progressions(
                style=style,
                key=key,
                num_recommendations=3
            )

            for i, rec in enumerate(recommendations, 1):
                prog = rec.item
                chord_names = [c.to_symbol() for c in prog.chords]

                print(f"\n  {i}. Score: {rec.score:.3f}")
                print(f"     Progression: {' → '.join(chord_names)}")
                print(f"     {rec.explanation}")

        except ValueError as e:
            print(f"  ⚠ {e}")


def demo_next_chord_prediction():
    """Demonstrate next chord prediction"""
    print_section("NEXT CHORD PREDICTION")

    system = MusicRecommendationSystem()

    # Example: Given a neo soul progression, what comes next?
    from src.theory import Chord, ChordQuality, Scale

    key = Note.from_string('C')
    scale = Scale.major(key)

    # Start with Cmaj7 - Am9
    current_progression = [
        Chord(scale.notes[0], ChordQuality.MAJOR_7),  # Cmaj7
        Chord(scale.notes[5], ChordQuality.MINOR_9),  # Am9
    ]

    print("Current progression: Cmaj7 → Am9")
    print("\nWhat should come next in neo soul style?\n")

    next_chords = system.progression_recommender.recommend_next_chord(
        current_progression=current_progression,
        style='neo_soul',
        top_k=5
    )

    for i, (chord_key, prob, explanation) in enumerate(next_chords, 1):
        print(f"  {i}. {chord_key}")
        print(f"     Probability: {prob*100:.1f}%")
        print(f"     {explanation}\n")


def demo_lick_recommendations():
    """Demonstrate lick recommendations"""
    print_section("LICK & RIFF RECOMMENDATIONS")

    system = MusicRecommendationSystem()

    # Test each priority style
    priority_styles = ['neo_soul', 'blues', 'progressive_metal', 'rock_fusion']
    key = Note.from_string('E')

    for style in priority_styles:
        print(f"\n🎸 {style.upper().replace('_', ' ')} Licks in {key.name}")
        print("-" * 70)

        licks = system.lick_recommender.recommend_licks(
            style=style,
            key=key,
            num_recommendations=3
        )

        for i, rec in enumerate(licks, 1):
            lick_data = rec.item
            print(f"\n  {i}. {lick_data['name']} (Score: {rec.score:.2f})")
            print(f"     {rec.explanation}")
            print(f"     Rhythm: {lick_data['rhythm']}")
            print(f"     Notes: {' - '.join(lick_data['transposed_notes'])}")


def demo_complete_recommendations():
    """Demonstrate complete recommendations for a style"""
    print_section("COMPLETE MUSIC RECOMMENDATIONS")

    system = MusicRecommendationSystem()

    # Get complete recommendations for neo soul in D
    style = 'neo_soul'
    key = Note.from_string('D')

    print(f"Getting complete recommendations for {style.upper()} in {key.name}...\n")

    results = system.get_complete_recommendations(
        style=style,
        key=key,
        include_progressions=True,
        include_melodies=False,  # Skip for now (no trained model)
        include_licks=True
    )

    # Show progressions
    if 'progressions' in results:
        print("📊 CHORD PROGRESSIONS")
        print("-" * 70)
        for i, rec in enumerate(results['progressions'][:2], 1):
            prog = rec.item
            chord_names = [c.to_symbol() for c in prog.chords]
            print(f"\n  {i}. {' → '.join(chord_names)}")
            print(f"     Score: {rec.score:.3f}")
            print(f"     {rec.explanation}")

    # Show licks
    if 'licks' in results:
        print("\n\n🎸 LICKS & RIFFS")
        print("-" * 70)
        for i, rec in enumerate(results['licks'][:2], 1):
            lick = rec.item
            print(f"\n  {i}. {lick['name']} (Score: {rec.score:.2f})")
            print(f"     {rec.explanation}")
            print(f"     Notes: {' - '.join(lick['transposed_notes'][:8])}")


def demo_all_priority_styles():
    """Show recommendations for all priority styles"""
    print_section("ALL PRIORITY STYLES OVERVIEW")

    system = MusicRecommendationSystem()
    key = Note.from_string('A')

    print(f"Recommendations in {key.name} for all priority styles:\n")

    for style in system.PRIORITY_STYLES:
        print(f"\n🎵 {style.upper().replace('_', ' ')}")
        print("-" * 70)

        # Get top progression
        try:
            progs = system.progression_recommender.recommend_progressions(
                style=style,
                key=key,
                num_recommendations=1
            )

            if progs:
                prog = progs[0].item
                chord_names = [c.to_symbol() for c in prog.chords]
                print(f"  Progression: {' → '.join(chord_names)}")

            # Get top lick
            licks = system.lick_recommender.recommend_licks(
                style=style,
                key=key,
                num_recommendations=1
            )

            if licks:
                lick_rec = licks[0]
                print(f"  Lick: {lick_rec.item['name']} - {lick_rec.explanation}")

        except Exception as e:
            print(f"  ⚠ Error: {e}")


def main():
    """Run all demonstrations"""
    print("\n" + "="*70)
    print(" 🎵 MUSIC THEORY RECOMMENDATION SYSTEM DEMO 🎵")
    print("="*70)
    print("\nPriority Styles: Neo Soul, Blues, Progressive Metal, Rock Fusion")
    print("="*70)

    # Run demonstrations
    demo_progression_recommendations()
    demo_next_chord_prediction()
    demo_lick_recommendations()
    demo_complete_recommendations()
    demo_all_priority_styles()

    # Summary
    print_section("SUMMARY")
    print("The recommendation system provides:")
    print("  ✓ Chord progression recommendations with explanations")
    print("  ✓ Next chord prediction based on style patterns")
    print("  ✓ Style-specific licks and riffs in any key")
    print("  ✓ Complete musical recommendations for composition")
    print("\nPriority styles are fully supported:")
    print("  • Neo Soul - Extended chords, chromatic movement")
    print("  • Blues - Pentatonic licks, dominant 7ths")
    print("  • Progressive Metal - Modal progressions, technical riffs")
    print("  • Rock Fusion - Jazz-rock hybrids, complex harmony")
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
