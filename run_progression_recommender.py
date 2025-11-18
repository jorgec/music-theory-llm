#!/usr/bin/env python3
"""
Quality of Life Script: Chord Progression Recommender

Get personalized chord progression recommendations based on style.
Includes music theory explanations and optional MIDI export.

Usage:
    python run_progression_recommender.py --style jazz --num 5
    python run_progression_recommender.py --style neo_soul --show-theory
    python run_progression_recommender.py --style blues --export-midi
"""

import argparse
import sys
from pathlib import Path

from src.recommender import MusicRecommendationSystem
from src.midi_io import export_progression_to_midi


VALID_STYLES = [
    'rock_fusion',
    'neo_soul',
    'blues',
    'jazz',
    'prog_metal',
    'metalcore'
]


def print_separator(char='-', length=80):
    """Print a visual separator"""
    print(char * length)


def print_section(title):
    """Print a section header"""
    print()
    print_separator('=')
    print(f" {title}")
    print_separator('=')
    print()


def format_progression_output(progression, index, show_theory=True):
    """Format a single progression recommendation for display"""
    print(f"\n[{index}] Chord Progression")
    print_separator('-', 80)

    # Chord sequence
    chord_names = ' -> '.join([str(c) for c in progression.chords])
    print(f"Chords: {chord_names}")
    print(f"Length: {len(progression.chords)} chords")

    # Scale info
    if progression.scale:
        print(f"Scale: {progression.scale.root.name} {progression.scale.mode.value}")

    # Harmonic function
    if hasattr(progression, 'harmonic_function') and progression.harmonic_function:
        print(f"Function: {progression.harmonic_function}")

    # Theory explanation
    if show_theory and hasattr(progression, 'theory_explanation') and progression.theory_explanation:
        print(f"\nTheory:")
        for line in progression.theory_explanation.split('\n')[:8]:
            if line.strip():
                print(f"  {line.strip()}")


def main():
    parser = argparse.ArgumentParser(
        description='Get personalized chord progression recommendations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --style jazz --num 5
  %(prog)s --style neo_soul --show-theory --export-midi
  %(prog)s --style blues --num 10 --midi-tempo 90

Available styles: rock_fusion, neo_soul, blues, jazz, prog_metal, metalcore
        """
    )

    # Required arguments
    parser.add_argument(
        '--style',
        type=str,
        required=True,
        choices=VALID_STYLES,
        help='Musical style for recommendations'
    )

    # Optional arguments
    parser.add_argument(
        '--num',
        type=int,
        default=5,
        help='Number of recommendations (default: 5)'
    )

    parser.add_argument(
        '--show-theory',
        action='store_true',
        default=True,
        help='Show music theory explanations (default: enabled)'
    )

    parser.add_argument(
        '--no-theory',
        action='store_true',
        help='Disable music theory explanations'
    )

    parser.add_argument(
        '--export-midi',
        action='store_true',
        help='Export progressions to MIDI files'
    )

    parser.add_argument(
        '--midi-tempo',
        type=int,
        default=120,
        help='Tempo for MIDI export (default: 120 BPM)'
    )

    parser.add_argument(
        '--chord-duration',
        type=float,
        default=4.0,
        help='Chord duration in beats for MIDI (default: 4.0)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs/progressions',
        help='Output directory for MIDI files (default: outputs/progressions)'
    )

    parser.add_argument(
        '--licks-for-progression',
        action='store_true',
        help='Show recommended licks for each progression'
    )

    parser.add_argument(
        '--licks-per-progression',
        type=int,
        default=3,
        help='Number of licks to show per progression (default: 3)'
    )

    args = parser.parse_args()

    # Validate number of recommendations
    if args.num < 1 or args.num > 50:
        print("[ERROR] Number of recommendations must be between 1 and 50")
        sys.exit(1)

    # Validate tempo
    if args.midi_tempo < 40 or args.midi_tempo > 240:
        print("[ERROR] MIDI tempo must be between 40 and 240 BPM")
        sys.exit(1)

    # Determine theory display
    show_theory = args.show_theory and not args.no_theory

    # Print header
    print_section("CHORD PROGRESSION RECOMMENDER")
    print(f"Style: {args.style}")
    print(f"Recommendations: {args.num}")
    print(f"Theory explanations: {'Yes' if show_theory else 'No'}")
    print(f"MIDI export: {'Yes' if args.export_midi else 'No'}")
    if args.licks_for_progression:
        print(f"Licks per progression: {args.licks_per_progression}")

    # Initialize system
    print("\nInitializing recommendation system...")
    try:
        system = MusicRecommendationSystem()
    except Exception as e:
        print(f"[ERROR] Failed to initialize system: {e}")
        sys.exit(1)

    # Get recommendations
    print(f"Generating {args.num} progression recommendations for {args.style}...")
    try:
        recommendations = system.progression_recommender.recommend_progressions(
            style=args.style,
            num_recommendations=args.num
        )
    except Exception as e:
        print(f"[ERROR] Failed to get recommendations: {e}")
        sys.exit(1)

    if not recommendations:
        print("[WARNING] No recommendations found")
        sys.exit(0)

    # Display recommendations
    print_section(f"TOP {len(recommendations)} PROGRESSION RECOMMENDATIONS")

    for idx, rec in enumerate(recommendations, 1):
        progression = rec.item
        score = rec.score

        # Add score to display
        print(f"\nScore: {score:.3f}")

        format_progression_output(
            progression,
            idx,
            show_theory=show_theory
        )

        # Show recommended licks for this progression
        if args.licks_for_progression and len(progression.chords) > 0:
            # Get key from first chord
            key = progression.chords[0].root

            print(f"\n  Recommended Licks for this Progression:")
            print(f"  " + "-" * 76)

            try:
                lick_recs = system.lick_recommender.recommend_licks(
                    style=args.style,
                    key=key,
                    num_recommendations=args.licks_per_progression
                )

                for lick_idx, lick_rec in enumerate(lick_recs, 1):
                    lick = lick_rec.item
                    artist = lick.get('artist', 'Unknown')
                    print(f"  [{lick_idx}] {lick['name']} - {artist}")

            except Exception as e:
                print(f"  [ERROR] Could not get lick recommendations: {e}")

    # Export to MIDI if requested
    if args.export_midi:
        print_section("MIDI EXPORT")
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        exported_count = 0
        for idx, rec in enumerate(recommendations, 1):
            progression = rec.item

            # Create safe filename
            chord_names = '_'.join([str(c) for c in progression.chords[:3]])
            filename = f"progression_{args.style}_{idx}_{chord_names}.mid"
            output_path = output_dir / filename

            try:
                export_progression_to_midi(
                    progression,
                    str(output_path),
                    tempo=args.midi_tempo,
                    chord_duration_beats=args.chord_duration
                )
                print(f"[{idx}] Exported: {filename}")
                exported_count += 1
            except Exception as e:
                print(f"[{idx}] [ERROR] Failed to export {filename}: {e}")

        print(f"\nExported {exported_count}/{len(recommendations)} progressions to: {output_dir}")

    # Summary
    print_section("SUMMARY")
    print(f"Total recommendations: {len(recommendations)}")
    print(f"Style: {args.style}")
    if args.export_midi:
        print(f"MIDI files: {output_dir}")
    print("\nDone!")


if __name__ == '__main__':
    main()
