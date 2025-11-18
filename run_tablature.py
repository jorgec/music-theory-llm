#!/usr/bin/env python3
"""
Quality of Life Script: Tablature Generator

Generate guitar tablature for licks with timing markers and validation.

Usage:
    python run_tablature.py --style rock_fusion --key E
    python run_tablature.py --style jazz --key C --num 3
    python run_tablature.py --style blues --key A --save-to-file
"""

import argparse
import sys
from pathlib import Path

from src.recommender import MusicRecommendationSystem
from src.theory import Note
from src.lick_tablature import (
    generate_lick_tablature_with_timing,
    validate_lick_length,
    RHYTHM_SPECS
)


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


def main():
    parser = argparse.ArgumentParser(
        description='Generate guitar tablature for licks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate tablature for a lick
  %(prog)s --style rock_fusion --key E

  # Generate for multiple licks
  %(prog)s --style jazz --key C --num 5

  # Save to file
  %(prog)s --style blues --key A --save-to-file

  # Show rhythm specifications
  %(prog)s --show-rhythms

Available styles: rock_fusion, neo_soul, blues, jazz, prog_metal, metalcore
Available keys: C, C#, D, D#, E, F, F#, G, G#, A, A#, B (and flats)
        """
    )

    # Mode selection
    parser.add_argument(
        '--show-rhythms',
        action='store_true',
        help='Show available rhythm specifications and exit'
    )

    # Required arguments (unless --show-rhythms)
    parser.add_argument(
        '--style',
        type=str,
        choices=VALID_STYLES,
        help='Musical style'
    )

    parser.add_argument(
        '--key',
        type=str,
        help='Musical key (e.g., E, C, A, F#, Bb)'
    )

    # Optional arguments
    parser.add_argument(
        '--num',
        type=int,
        default=1,
        help='Number of licks to generate tablature for (default: 1)'
    )

    parser.add_argument(
        '--save-to-file',
        action='store_true',
        help='Save tablature to text files'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs/tablature',
        help='Output directory for tablature files (default: outputs/tablature)'
    )

    parser.add_argument(
        '--show-validation',
        action='store_true',
        default=True,
        help='Show length validation results (default: enabled)'
    )

    args = parser.parse_args()

    # Show rhythm specifications
    if args.show_rhythms:
        print_section("RHYTHM SPECIFICATIONS")
        print(f"{'Rhythm':<20} {'BPM':<8} {'Duration':<12} {'Min Notes':<12} {'Typical Notes'}")
        print_separator('-')
        for rhythm_name, spec in sorted(RHYTHM_SPECS.items()):
            print(f"{rhythm_name:<20} {spec['bpm']:<8} {spec['note_duration']:<12} "
                  f"{spec['min_notes']:<12} {spec['typical_notes']}")
        print()
        print(f"Total rhythms: {len(RHYTHM_SPECS)}")
        return

    # Validate required arguments
    if not args.style or not args.key:
        parser.error("--style and --key are required (unless using --show-rhythms)")

    # Validate key
    if args.key not in VALID_KEYS:
        print(f"[ERROR] Invalid key: {args.key}")
        print(f"Valid keys: {', '.join(VALID_KEYS)}")
        sys.exit(1)

    # Validate count
    if args.num < 1 or args.num > 20:
        print("[ERROR] Number of licks must be between 1 and 20")
        sys.exit(1)

    # Print configuration
    print_section("TABLATURE GENERATOR")
    print(f"Style: {args.style}")
    print(f"Key: {args.key}")
    print(f"Number of licks: {args.num}")
    print(f"Save to file: {'Yes' if args.save_to_file else 'No'}")
    if args.save_to_file:
        print(f"Output directory: {args.output_dir}")

    # Initialize system
    print("\nInitializing system...")
    try:
        system = MusicRecommendationSystem()
        key = Note.from_string(args.key)
    except Exception as e:
        print(f"[ERROR] Failed to initialize: {e}")
        sys.exit(1)

    # Get recommendations
    print(f"Getting {args.num} lick recommendation(s)...")
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
        print("[ERROR] No licks found")
        sys.exit(1)

    # Create output directory if saving
    if args.save_to_file:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Generate tablature
    print_section(f"TABLATURE FOR {len(recommendations)} LICK(S)")

    generated_count = 0
    validation_passed = 0

    for idx, rec in enumerate(recommendations, 1):
        lick = rec.item
        score = rec.score

        print(f"\n[{idx}] {lick['name']}")
        print(f"Score: {score:.3f}")
        print_separator('-')

        # Basic info
        artist = lick.get('artist', 'Unknown')
        rhythm = lick.get('rhythm', 'medium')

        print(f"Artist: {artist}")
        print(f"Rhythm: {rhythm}")
        print(f"Intervals: {lick['intervals']}")
        print()

        # Generate tablature
        try:
            tab = generate_lick_tablature_with_timing(lick, key)
            print(tab)
            generated_count += 1

            # Validate length
            if args.show_validation:
                is_valid, reason = validate_lick_length(lick)
                print()
                if is_valid:
                    print("[OK] Lick length validated")
                    validation_passed += 1
                else:
                    print(f"[WARNING] {reason}")

            # Save to file
            if args.save_to_file:
                safe_name = lick['name'].replace(' ', '_').replace('/', '-')
                filename = f"{args.style}_{args.key}_{safe_name}.txt"
                output_path = output_dir / filename

                with open(output_path, 'w') as f:
                    f.write(f"{lick['name']}\n")
                    f.write(f"Artist: {artist}\n")
                    f.write(f"Style: {args.style}\n")
                    f.write(f"Key: {args.key}\n")
                    f.write(f"Rhythm: {rhythm}\n")
                    f.write(f"Intervals: {lick['intervals']}\n")
                    f.write("\n")
                    f.write(tab)
                    f.write("\n\n")
                    if args.show_validation:
                        f.write(f"Validation: {'PASS' if is_valid else 'WARNING'}\n")
                        if not is_valid:
                            f.write(f"Reason: {reason}\n")

                print(f"\nSaved to: {filename}")

        except Exception as e:
            print(f"[ERROR] Failed to generate tablature: {e}")

        print()

    # Summary
    print_section("SUMMARY")
    print(f"Tablature generated: {generated_count}/{len(recommendations)}")
    if args.show_validation:
        print(f"Validation passed: {validation_passed}/{generated_count}")
        print(f"Pass rate: {(validation_passed/generated_count*100):.1f}%" if generated_count > 0 else "N/A")
    if args.save_to_file:
        print(f"Files saved to: {args.output_dir}")
    print("\nDone!")


if __name__ == '__main__':
    main()
