#!/usr/bin/env python3
"""
Quality of Life Script: Audio File Analyzer

Analyze audio files (WAV, MP3, etc.) with tempo detection, key detection,
and music theory explanations.

Usage:
    python run_audio_analyzer.py --file song.wav
    python run_audio_analyzer.py --file guitar_solo.mp3 --save-report
    python run_audio_analyzer.py --file track.wav --show-detailed
"""

import argparse
import sys
from pathlib import Path

from src.audio_analyzer import AudioAnalyzer


SUPPORTED_FORMATS = ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac']


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
        description='Analyze audio files with tempo, key detection, and music theory explanations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze an audio file
  %(prog)s --file my_song.wav

  # Analyze with detailed output
  %(prog)s --file guitar_solo.mp3 --show-detailed

  # Save analysis to file
  %(prog)s --file track.wav --save-report

  # Analyze multiple files
  %(prog)s --file file1.wav file2.mp3 file3.flac

Supported formats: WAV, MP3, FLAC, OGG, M4A, AAC
Note: Requires librosa library (pip install librosa soundfile)
        """
    )

    # Required arguments
    parser.add_argument(
        '--file',
        type=str,
        nargs='+',
        required=True,
        help='Audio file(s) to analyze'
    )

    # Optional arguments
    parser.add_argument(
        '--show-detailed',
        action='store_true',
        help='Show detailed harmonic and spectral analysis'
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
        '--show-beats',
        action='store_true',
        help='Show detected beat times (first 20 beats)'
    )

    args = parser.parse_args()

    # Validate files exist
    audio_files = []
    for file_path in args.file:
        path = Path(file_path)
        if not path.exists():
            print(f"[ERROR] File not found: {file_path}")
            continue
        if path.suffix.lower() not in SUPPORTED_FORMATS:
            print(f"[WARNING] Unsupported format: {file_path}")
            print(f"Supported: {', '.join(SUPPORTED_FORMATS)}")
            continue
        audio_files.append(path)

    if not audio_files:
        print("[ERROR] No valid audio files found")
        sys.exit(1)

    # Create output directory if saving
    if args.save_report:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Print header
    print_section("AUDIO FILE ANALYZER")
    print(f"Files to analyze: {len(audio_files)}")
    print()

    # Check for librosa
    try:
        analyzer = AudioAnalyzer()
    except ImportError as e:
        print(f"[ERROR] {e}")
        print("\nPlease install required libraries:")
        print("  pip install librosa soundfile")
        sys.exit(1)

    # Analyze each file
    for idx, audio_file in enumerate(audio_files, 1):
        print_section(f"ANALYZING FILE {idx}/{len(audio_files)}")
        print(f"File: {audio_file.name}")
        print(f"Path: {audio_file}")
        print()

        try:
            # Analyze audio
            analysis = analyzer.analyze_audio_file(str(audio_file))

            # Display theory explanation
            print()
            print(analysis['theory_explanation'])

            # Detailed information
            if args.show_detailed:
                print()
                print_separator('-')
                print("DETAILED ANALYSIS")
                print_separator('-')
                print()

                # Tempo details
                if analysis.get('tempo'):
                    print(f"Tempo: {analysis['tempo']:.1f} BPM")
                    print(f"Tempo confidence: {analysis.get('tempo_confidence', 0):.1%}")
                    print(f"Tempo range: {analysis.get('tempo_range', 'unknown')}")
                    print(f"Detected beats: {analysis.get('beat_count', 0)}")
                    print()

                # Key detection details
                if analysis.get('key'):
                    print(f"Detected key: {analysis['key']} {analysis.get('mode', '')}")
                    print(f"Key confidence: {analysis.get('key_confidence', 0):.1%}")
                    print()

                # Harmonic content
                print(f"Harmonic ratio: {analysis.get('harmonic_ratio', 0):.2%}")
                print(f"Spectral centroid: {analysis.get('spectral_centroid_mean', 0):.1f} Hz")
                print(f"Spectral rolloff: {analysis.get('spectral_rolloff_mean', 0):.1f} Hz")
                print()

                # Prominent pitches
                prominent_pitches = analysis.get('prominent_pitches', [])
                if prominent_pitches:
                    print(f"Prominent pitches: {', '.join(prominent_pitches)}")
                    print()

            # Beat times
            if args.show_beats:
                beat_times = analysis.get('beat_times', [])
                if beat_times:
                    print()
                    print_separator('-')
                    print("BEAT TIMES (first 20)")
                    print_separator('-')
                    print()

                    for i, beat_time in enumerate(beat_times[:20], 1):
                        print(f"  Beat {i}: {beat_time:.3f}s")

                    if len(beat_times) > 20:
                        print(f"  ... and {len(beat_times) - 20} more beats")
                    print()

            # Save report
            if args.save_report:
                report_filename = f"{audio_file.stem}_analysis.txt"
                report_path = output_dir / report_filename

                with open(report_path, 'w') as f:
                    f.write(analysis['theory_explanation'])
                    f.write("\n\n")
                    f.write("=" * 70)
                    f.write("\nDETAILED DATA\n")
                    f.write("=" * 70)
                    f.write("\n\n")

                    f.write(f"Filename: {analysis['filename']}\n")
                    f.write(f"Duration: {analysis['duration']:.2f} seconds\n")
                    f.write(f"Sample rate: {analysis['sample_rate']} Hz\n\n")

                    # Tempo
                    if analysis.get('tempo'):
                        f.write(f"Tempo: {analysis['tempo']:.1f} BPM\n")
                        f.write(f"Tempo confidence: {analysis.get('tempo_confidence', 0):.2%}\n")
                        f.write(f"Tempo range: {analysis.get('tempo_range', 'unknown')}\n")
                        f.write(f"Detected beats: {analysis.get('beat_count', 0)}\n\n")

                    # Key
                    if analysis.get('key'):
                        f.write(f"Detected key: {analysis['key']} {analysis.get('mode', '')}\n")
                        f.write(f"Key confidence: {analysis.get('key_confidence', 0):.2%}\n\n")

                    # Harmonic analysis
                    f.write(f"Harmonic ratio: {analysis.get('harmonic_ratio', 0):.2%}\n")
                    f.write(f"Spectral centroid: {analysis.get('spectral_centroid_mean', 0):.1f} Hz\n")
                    f.write(f"Spectral rolloff: {analysis.get('spectral_rolloff_mean', 0):.1f} Hz\n\n")

                    # Prominent pitches
                    prominent_pitches = analysis.get('prominent_pitches', [])
                    if prominent_pitches:
                        f.write(f"Prominent pitches: {', '.join(prominent_pitches)}\n\n")

                    # Beat times
                    beat_times = analysis.get('beat_times', [])
                    if beat_times:
                        f.write(f"\nBeat times ({len(beat_times)} total):\n")
                        for i, beat_time in enumerate(beat_times, 1):
                            f.write(f"  Beat {i}: {beat_time:.3f}s\n")

                print(f"Report saved to: {report_path}")
                print()

        except Exception as e:
            print(f"[ERROR] Failed to analyze {audio_file.name}: {e}")
            import traceback
            if args.show_detailed:
                traceback.print_exc()
            continue

    # Summary
    print_section("SUMMARY")
    print(f"Analyzed {len(audio_files)} file(s)")
    if args.save_report:
        print(f"Reports saved to: {args.output_dir}")
    print("\nDone!")


if __name__ == '__main__':
    main()
