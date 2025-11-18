#!/usr/bin/env python3
"""
Quality of Life Script: Lick Recommender

Get personalized guitar lick recommendations based on style and key.
Includes music theory explanations and optional tablature/MIDI export.

Usage:
    python run_lick_recommender.py --style rock_fusion --key E
    python run_lick_recommender.py --style jazz --key C --num 10 --export-midi
    python run_lick_recommender.py --style blues --key A --show-tablature
"""

import argparse
import sys
from pathlib import Path

from src.recommender import MusicRecommendationSystem
from src.theory import Note
from src.lick_tablature import (
    generate_lick_tablature_with_timing,
    validate_lick_length
)
from src.midi_io import export_lick_to_midi


VALID_STYLES = [
    'rock_fusion',
    'neo_soul',
    'blues',
    'jazz',
    'prog_metal',
    'metalcore'
]

VALID_KEYS = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']


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


def format_lick_output(lick, key, index, show_theory=True, show_tablature=False):
    """Format a single lick recommendation for display"""
    print(f"\n[{index}] {lick['name']}")
    print_separator('-', 80)

    # Basic info
    artist = lick.get('artist', 'Unknown')
    style_tag = lick.get('style', 'General')
    rhythm = lick.get('rhythm', 'medium')

    print(f"Artist: {artist}")
    print(f"Style: {style_tag}")
    print(f"Rhythm: {rhythm}")
    print(f"Key: {key.name}")
    print(f"Intervals: {lick['intervals']}")
    print(f"Note count: {len(lick['intervals'])}")

    # Description
    if 'description' in lick:
        print(f"\nDescription:")
        print(f"  {lick['description']}")

    # Theory explanation
    if show_theory and 'theory_explanation' in lick:
        print(f"\nTheory:")
        for line in lick['theory_explanation'].split('\n')[:5]:
            if line.strip():
                print(f"  {line.strip()}")

    # Tablature
    if show_tablature:
        try:
            tab = generate_lick_tablature_with_timing(lick, key)
            print(f"\nTablature:")
            for line in tab.split('\n'):
                print(f"  {line}")

            # Validation
            is_valid, reason = validate_lick_length(lick)
            if is_valid:
                print("  [OK] Lick length validated")
            else:
                print(f"  [WARNING] {reason}")
        except Exception as e:
            print(f"  [ERROR] Could not generate tablature: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Get personalized guitar lick recommendations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --style rock_fusion --key E
  %(prog)s --style jazz --key C --num 10 --show-theory
  %(prog)s --style blues --key A --show-tablature --export-midi

Available styles: rock_fusion, neo_soul, blues, jazz, prog_metal, metalcore
Available keys: C, C#, D, D#, E, F, F#, G, G#, A, A#, B (and flats)
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

    parser.add_argument(
        '--key',
        type=str,
        required=True,
        help='Musical key (e.g., E, C, A, F#, Bb)'
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
        '--show-tablature',
        action='store_true',
        help='Display guitar tablature for each lick'
    )

    parser.add_argument(
        '--export-midi',
        action='store_true',
        help='Export licks to MIDI files'
    )

    parser.add_argument(
        '--midi-tempo',
        type=int,
        default=120,
        help='Tempo for MIDI export (default: 120 BPM)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs/licks',
        help='Output directory for MIDI files (default: outputs/licks)'
    )

    args = parser.parse_args()

    # Validate key
    if args.key not in VALID_KEYS:
        print(f"[ERROR] Invalid key: {args.key}")
        print(f"Valid keys: {', '.join(VALID_KEYS)}")
        sys.exit(1)

    # Validate number of recommendations
    if args.num < 1 or args.num > 50:
        print("[ERROR] Number of recommendations must be between 1 and 50")
        sys.exit(1)

    # Determine theory display
    show_theory = args.show_theory and not args.no_theory

    # Print header
    print_section("GUITAR LICK RECOMMENDER")
    print(f"Style: {args.style}")
    print(f"Key: {args.key}")
    print(f"Recommendations: {args.num}")
    print(f"Theory explanations: {'Yes' if show_theory else 'No'}")
    print(f"Tablature: {'Yes' if args.show_tablature else 'No'}")
    print(f"MIDI export: {'Yes' if args.export_midi else 'No'}")

    # Initialize system
    print("\nInitializing recommendation system...")
    try:
        system = MusicRecommendationSystem()
        key = Note.from_string(args.key)
    except Exception as e:
        print(f"[ERROR] Failed to initialize system: {e}")
        sys.exit(1)

    # Get recommendations
    print(f"Generating {args.num} recommendations for {args.style} in key of {args.key}...")
    try:
        recommendations = system.lick_recommender.recommend_licks(
            style=args.style,
            key=key,
            num_recommendations=args.num
        )
    except Exception as e:
        print(f"[ERROR] Failed to get recommendations: {e}")
        sys.exit(1)

    if not recommendations:
        print("[WARNING] No recommendations found")
        sys.exit(0)

    # Display recommendations
    print_section(f"TOP {len(recommendations)} LICK RECOMMENDATIONS")

    for idx, rec in enumerate(recommendations, 1):
        lick = rec.item
        score = rec.score

        # Add score to display
        print(f"\nScore: {score:.3f}")

        format_lick_output(
            lick,
            key,
            idx,
            show_theory=show_theory,
            show_tablature=args.show_tablature
        )

    # Export to MIDI if requested
    if args.export_midi:
        print_section("MIDI EXPORT")
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        exported_count = 0
        for idx, rec in enumerate(recommendations, 1):
            lick = rec.item

            # Create safe filename
            safe_name = lick['name'].replace(' ', '_').replace('/', '-')
            filename = f"{args.style}_{args.key}_{safe_name}.mid"
            output_path = output_dir / filename

            try:
                export_lick_to_midi(
                    lick,
                    key,
                    str(output_path),
                    tempo=args.midi_tempo
                )
                print(f"[{idx}] Exported: {filename}")
                exported_count += 1
            except Exception as e:
                print(f"[{idx}] [ERROR] Failed to export {filename}: {e}")

        print(f"\nExported {exported_count}/{len(recommendations)} licks to: {output_dir}")

    # Summary
    print_section("SUMMARY")
    print(f"Total recommendations: {len(recommendations)}")
    print(f"Style: {args.style}")
    print(f"Key: {args.key}")
    if args.export_midi:
        print(f"MIDI files: {output_dir}")
    print("\nDone!")


if __name__ == '__main__':
    main()
