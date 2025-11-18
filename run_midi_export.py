#!/usr/bin/env python3
"""
Quality of Life Script: MIDI Export

Export licks and chord progressions to MIDI files.

Usage:
    python run_midi_export.py --lick --style rock_fusion --key E --output my_lick.mid
    python run_midi_export.py --progression --style jazz --key C --output progression.mid
    python run_midi_export.py --lick --style blues --key A --tempo 90
"""

import argparse
import sys
from pathlib import Path

from src.recommender import MusicRecommendationSystem
from src.theory import Note
from src.midi_io import export_lick_to_midi, export_progression_to_midi


VALID_STYLES = [
    'rock_fusion',
    'neo_soul',
    'blues',
    'jazz',
    'prog_metal',
    'metalcore'
]

VALID_KEYS = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']


def main():
    parser = argparse.ArgumentParser(
        description='Export licks and chord progressions to MIDI files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export a lick
  %(prog)s --lick --style rock_fusion --key E --output fusion_lick.mid

  # Export a chord progression
  %(prog)s --progression --style jazz --key C --output jazz_changes.mid

  # Export with custom tempo
  %(prog)s --lick --style blues --key A --tempo 90 --velocity 100

  # Export top N licks
  %(prog)s --lick --style neo_soul --key D --count 3 --output-dir outputs/neo_soul

Available styles: rock_fusion, neo_soul, blues, jazz, prog_metal, metalcore
Available keys: C, C#, D, D#, E, F, F#, G, G#, A, A#, B (and flats)
        """
    )

    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--lick',
        action='store_true',
        help='Export a lick to MIDI'
    )
    mode_group.add_argument(
        '--progression',
        action='store_true',
        help='Export a chord progression to MIDI'
    )

    # Required arguments
    parser.add_argument(
        '--style',
        type=str,
        required=True,
        choices=VALID_STYLES,
        help='Musical style'
    )

    parser.add_argument(
        '--key',
        type=str,
        required=True,
        help='Musical key (e.g., E, C, A, F#, Bb)'
    )

    # Output arguments
    parser.add_argument(
        '--output',
        type=str,
        help='Output MIDI filename (default: auto-generated)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs/midi',
        help='Output directory (default: outputs/midi)'
    )

    # Export options
    parser.add_argument(
        '--count',
        type=int,
        default=1,
        help='Number of items to export (default: 1)'
    )

    parser.add_argument(
        '--tempo',
        type=int,
        default=120,
        help='Tempo in BPM (default: 120)'
    )

    parser.add_argument(
        '--velocity',
        type=int,
        default=80,
        help='MIDI velocity for notes (0-127, default: 80)'
    )

    parser.add_argument(
        '--duration',
        type=float,
        default=0.25,
        help='Note duration in beats for licks (default: 0.25)'
    )

    parser.add_argument(
        '--chord-duration',
        type=float,
        default=4.0,
        help='Chord duration in beats for progressions (default: 4.0)'
    )

    args = parser.parse_args()

    # Validate inputs
    if args.key not in VALID_KEYS:
        print(f"[ERROR] Invalid key: {args.key}")
        print(f"Valid keys: {', '.join(VALID_KEYS)}")
        sys.exit(1)

    if args.tempo < 40 or args.tempo > 240:
        print("[ERROR] Tempo must be between 40 and 240 BPM")
        sys.exit(1)

    if args.velocity < 0 or args.velocity > 127:
        print("[ERROR] Velocity must be between 0 and 127")
        sys.exit(1)

    if args.count < 1 or args.count > 20:
        print("[ERROR] Count must be between 1 and 20")
        sys.exit(1)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Print configuration
    print("=" * 80)
    print(" MIDI EXPORT")
    print("=" * 80)
    print()
    print(f"Mode: {'Lick' if args.lick else 'Chord Progression'}")
    print(f"Style: {args.style}")
    print(f"Key: {args.key}")
    print(f"Tempo: {args.tempo} BPM")
    print(f"Velocity: {args.velocity}")
    print(f"Count: {args.count}")
    print(f"Output directory: {output_dir}")
    print()

    # Initialize system
    print("Initializing system...")
    try:
        system = MusicRecommendationSystem()
        key = Note.from_string(args.key)
    except Exception as e:
        print(f"[ERROR] Failed to initialize: {e}")
        sys.exit(1)

    exported_count = 0

    # Export licks
    if args.lick:
        print(f"Getting {args.count} lick recommendation(s)...")
        try:
            recommendations = system.lick_recommender.recommend_licks(
                style=args.style,
                key=key,
                num_recommendations=args.count
            )
        except Exception as e:
            print(f"[ERROR] Failed to get recommendations: {e}")
            sys.exit(1)

        if not recommendations:
            print("[ERROR] No licks found")
            sys.exit(1)

        print(f"\nExporting {len(recommendations)} lick(s) to MIDI...")
        print("-" * 80)

        for idx, rec in enumerate(recommendations, 1):
            lick = rec.item

            # Generate filename
            if args.output and args.count == 1:
                filename = args.output
            else:
                safe_name = lick['name'].replace(' ', '_').replace('/', '-')
                filename = f"{args.style}_{args.key}_{safe_name}.mid"

            output_path = output_dir / filename

            try:
                export_lick_to_midi(
                    lick,
                    key,
                    str(output_path),
                    tempo=args.tempo,
                    velocity=args.velocity,
                    duration_beats=args.duration
                )

                file_size = output_path.stat().st_size
                print(f"[{idx}] {lick['name']}")
                print(f"     File: {filename}")
                print(f"     Size: {file_size} bytes")
                print(f"     Intervals: {lick['intervals']}")
                exported_count += 1

            except Exception as e:
                print(f"[{idx}] [ERROR] Failed: {e}")

    # Export progressions
    elif args.progression:
        print(f"Getting {args.count} progression recommendation(s)...")
        try:
            recommendations = system.progression_recommender.recommend_progressions(
                style=args.style,
                num_recommendations=args.count
            )
        except Exception as e:
            print(f"[ERROR] Failed to get recommendations: {e}")
            sys.exit(1)

        if not recommendations:
            print("[ERROR] No progressions found")
            sys.exit(1)

        print(f"\nExporting {len(recommendations)} progression(s) to MIDI...")
        print("-" * 80)

        for idx, rec in enumerate(recommendations, 1):
            progression = rec.item

            # Generate filename
            if args.output and args.count == 1:
                filename = args.output
            else:
                # Get chord names for filename
                chord_names = '_'.join([str(c) for c in progression.chords[:3]])
                filename = f"progression_{args.style}_{chord_names}.mid"

            output_path = output_dir / filename

            try:
                export_progression_to_midi(
                    progression,
                    str(output_path),
                    tempo=args.tempo,
                    velocity=args.velocity,
                    chord_duration_beats=args.chord_duration
                )

                file_size = output_path.stat().st_size
                chord_list = ' -> '.join([str(c) for c in progression.chords])
                print(f"[{idx}] {chord_list}")
                print(f"     File: {filename}")
                print(f"     Size: {file_size} bytes")
                print(f"     Chords: {len(progression.chords)}")
                exported_count += 1

            except Exception as e:
                print(f"[{idx}] [ERROR] Failed: {e}")

    # Summary
    print()
    print("=" * 80)
    print(f"Successfully exported {exported_count}/{args.count} file(s)")
    print(f"Output directory: {output_dir}")
    print("=" * 80)


if __name__ == '__main__':
    main()
