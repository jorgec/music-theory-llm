#!/usr/bin/env python3
"""
Quality of Life Script: MIDI File Analyzer

Analyze MIDI files (single or multi-track) with comprehensive music theory explanations.

Usage:
    python run_midi_analyzer.py --file song.mid
    python run_midi_analyzer.py --file progression.mid --save-report
    python run_midi_analyzer.py --file lick.mid --show-detailed
"""

import argparse
import sys
from pathlib import Path

from src.midi_io import MidiReader


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
        description='Analyze MIDI files with music theory explanations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a MIDI file
  %(prog)s --file my_song.mid

  # Analyze with detailed output
  %(prog)s --file lick.mid --show-detailed

  # Save analysis to file
  %(prog)s --file progression.mid --save-report

  # Analyze multiple files
  %(prog)s --file file1.mid file2.mid file3.mid
        """
    )

    # Required arguments
    parser.add_argument(
        '--file',
        type=str,
        nargs='+',
        required=True,
        help='MIDI file(s) to analyze'
    )

    # Optional arguments
    parser.add_argument(
        '--show-detailed',
        action='store_true',
        help='Show detailed pitch and interval analysis'
    )

    parser.add_argument(
        '--save-report',
        action='store_true',
        help='Save analysis report to text file'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs/analysis',
        help='Output directory for reports (default: outputs/analysis)'
    )

    parser.add_argument(
        '--show-tracks',
        action='store_true',
        default=True,
        help='Show individual track information (default: enabled)'
    )

    args = parser.parse_args()

    # Validate files exist
    midi_files = []
    for file_path in args.file:
        path = Path(file_path)
        if not path.exists():
            print(f"[ERROR] File not found: {file_path}")
            continue
        if path.suffix.lower() not in ['.mid', '.midi']:
            print(f"[WARNING] Not a MIDI file: {file_path}")
            continue
        midi_files.append(path)

    if not midi_files:
        print("[ERROR] No valid MIDI files found")
        sys.exit(1)

    # Create output directory if saving
    if args.save_report:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize reader
    print_section("MIDI FILE ANALYZER")
    print(f"Files to analyze: {len(midi_files)}")
    print()

    reader = MidiReader()

    # Analyze each file
    for idx, midi_file in enumerate(midi_files, 1):
        print_section(f"ANALYZING FILE {idx}/{len(midi_files)}")
        print(f"File: {midi_file.name}")
        print(f"Path: {midi_file}")
        print()

        try:
            # Comprehensive analysis with theory
            analysis = reader.analyze_midi_with_theory(str(midi_file))

            # Display theory explanation
            print(analysis['theory_explanation'])

            # Detailed information
            if args.show_detailed:
                print()
                print_separator('-')
                print("DETAILED ANALYSIS")
                print_separator('-')
                print()

                # Most common pitches
                if analysis.get('most_common_pitches'):
                    print("Most Common Pitches:")
                    for i, pitch_info in enumerate(analysis['most_common_pitches'], 1):
                        print(f"  {i}. {pitch_info['note_name']} "
                              f"(MIDI {pitch_info['pitch']}) - "
                              f"{pitch_info['count']} times")
                    print()

                # Common intervals
                if analysis.get('common_intervals'):
                    print("Most Common Intervals:")
                    for i, interval_info in enumerate(analysis['common_intervals'], 1):
                        semitones = interval_info['semitones']
                        direction = "↑" if semitones > 0 else "↓" if semitones < 0 else "="
                        print(f"  {i}. {direction}{abs(semitones)} semitones - "
                              f"{interval_info['count']} times")
                    print()

            # Track details
            if args.show_tracks and analysis.get('tracks'):
                print()
                print_separator('-')
                print("TRACK DETAILS")
                print_separator('-')
                print()

                for track in analysis['tracks']:
                    print(f"Track {track['track_number']}: {track['track_name']}")
                    print(f"  Total notes: {len(track.get('notes', []))}")

                    # Show first few notes
                    notes = track.get('notes', [])
                    if notes:
                        print(f"  First notes:")
                        for i, note in enumerate(notes[:5], 1):
                            print(f"    {i}. {note['note_name']} at {note['time']:.2f}s")
                    print()

            # Save report
            if args.save_report:
                report_filename = f"{midi_file.stem}_analysis.txt"
                report_path = output_dir / report_filename

                with open(report_path, 'w') as f:
                    f.write(analysis['theory_explanation'])
                    f.write("\n\n")
                    f.write("=" * 70)
                    f.write("\nDETAILED DATA\n")
                    f.write("=" * 70)
                    f.write("\n\n")

                    f.write(f"Filename: {analysis['filename']}\n")
                    f.write(f"Duration: {analysis['total_time']:.2f} seconds\n")
                    f.write(f"Tempo: {analysis['tempo']:.1f} BPM\n")
                    f.write(f"Tracks: {analysis['track_count']}\n")
                    f.write(f"Total notes: {analysis['total_notes']}\n\n")

                    # Key detection
                    detected_key = analysis.get('detected_key')
                    if detected_key and detected_key['key']:
                        f.write(f"Detected key: {detected_key['key']} {detected_key['mode']}\n")
                        f.write(f"Key confidence: {detected_key['confidence']:.2%}\n\n")

                    # Pitch range
                    pitch_range = analysis.get('pitch_range')
                    if pitch_range:
                        f.write(f"Pitch range: {pitch_range['lowest']} - {pitch_range['highest']}\n")
                        f.write(f"Span: {pitch_range['span']} semitones\n\n")

                    # Tracks
                    f.write("TRACKS:\n")
                    for track in analysis.get('tracks', []):
                        f.write(f"  Track {track['track_number']}: {track['track_name']}\n")
                        f.write(f"    Messages: {track.get('messages', 0)}\n")
                        f.write(f"    Notes: {len(track.get('notes', []))}\n")

                print(f"Report saved to: {report_path}")
                print()

        except Exception as e:
            print(f"[ERROR] Failed to analyze {midi_file.name}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Summary
    print_section("SUMMARY")
    print(f"Analyzed {len(midi_files)} file(s)")
    if args.save_report:
        print(f"Reports saved to: {args.output_dir}")
    print("\nDone!")


if __name__ == '__main__':
    main()
