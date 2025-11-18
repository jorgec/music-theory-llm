#!/usr/bin/env python3
"""
Training Data Input Script

Allows adding licks and chord progressions to the training data via multiple input methods:
1. Interactive CLI prompts
2. MIDI file import
3. Audio file analysis
4. Batch CSV import
5. Text-based interval notation

Assumes 16th notes by default but allows for rhythm/tempo modifications.

Usage:
    python add_training_data.py --interactive
    python add_training_data.py --from-midi file.mid --style jazz
    python add_training_data.py --from-audio file.wav --style blues
    python add_training_data.py --from-csv licks.csv
"""

import argparse
import sys
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

# Optional imports for MIDI/audio analysis
try:
    from src.midi_io import MidiReader
    MIDI_AVAILABLE = True
except ImportError:
    MIDI_AVAILABLE = False
    print("[WARNING] MIDI support not available")

try:
    from src.audio_analyzer import AudioAnalyzer
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("[WARNING] Audio analysis not available")


VALID_STYLES = [
    # Original styles
    'rock_fusion',
    'neo_soul',
    'blues',
    'jazz',
    'progressive_metal',
    'metalcore',
    # New styles - expanded coverage
    'soul',         # Motown, Stax, Gospel-influenced
    'funk',         # P-Funk, Tower of Power, Modern funk
    'pop_rock',     # 80s rock, power ballads, arena rock
    'pop',          # 90s pop, 2000s, Top 40, EDM-pop
    'rnb'           # Contemporary R&B, trap-soul
]

# Rhythm types with 16th notes as default
RHYTHM_TYPES = {
    '16ths': {'note_duration': 0.25, 'bpm_range': (120, 180), 'description': '16th notes (default)'},
    '8ths': {'note_duration': 0.5, 'bpm_range': (80, 140), 'description': '8th notes'},
    'triplets': {'note_duration': 0.333, 'bpm_range': (90, 150), 'description': 'Triplet feel'},
    'syncopated': {'note_duration': 0.25, 'bpm_range': (100, 140), 'description': 'Syncopated 16ths'},
    'legato': {'note_duration': 0.25, 'bpm_range': (100, 160), 'description': 'Legato 16ths'},
    'staccato': {'note_duration': 0.125, 'bpm_range': (120, 180), 'description': 'Staccato 16ths'},
    'custom': {'note_duration': None, 'bpm_range': (60, 240), 'description': 'Custom rhythm'}
}

TECHNIQUES = [
    # Picking techniques
    'alternate picking', 'economy picking', 'sweep picking', 'hybrid picking',
    'legato', 'hammer-ons/pull-offs', 'tapping', 'string skipping',

    # Harmonic techniques
    'arpeggios', 'chord tones', 'extended chords', 'altered tones',
    'chromatic approach', 'voice leading', 'chord melody', 'superimposition',

    # Stylistic techniques
    'bends', 'vibrato', 'slides', 'palm muting',
    'syncopation', 'rhythmic displacement', 'polyrhythms',
    'modal playing', 'outside playing', 'chord substitution'
]


def print_separator(char='=', length=80):
    """Print visual separator"""
    print(char * length)


def print_section(title):
    """Print section header"""
    print()
    print_separator('=')
    print(f" {title}")
    print_separator('=')
    print()


def get_user_choice(prompt: str, choices: List[str], allow_custom: bool = False) -> str:
    """Get user choice from a list"""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")
    if allow_custom:
        print(f"  {len(choices) + 1}. Custom (enter your own)")

    while True:
        try:
            choice_input = input("\nEnter number: ").strip()
            choice_num = int(choice_input)
            if 1 <= choice_num <= len(choices):
                return choices[choice_num - 1]
            elif allow_custom and choice_num == len(choices) + 1:
                return input("Enter custom value: ").strip()
            else:
                print(f"Invalid choice. Enter 1-{len(choices)}")
        except ValueError:
            print("Invalid input. Enter a number.")


def interactive_lick_input() -> Dict:
    """Interactive CLI for adding a lick"""
    print_section("INTERACTIVE LICK INPUT")

    lick = {}

    # Basic information
    lick['name'] = input("Lick name: ").strip()
    lick['artist'] = input("Artist (optional): ").strip() or "User Contributed"

    # Style selection
    lick['style'] = get_user_choice("Select style:", VALID_STYLES)

    # Interval input
    print("\nInterval pattern input")
    print("Examples:")
    print("  - Major scale: 0, 2, 4, 5, 7, 9, 11, 12")
    print("  - Pentatonic: 0, 2, 4, 7, 9, 12")
    print("  - Chord arpeggio: 0, 4, 7, 12")
    print("  - Chromatic approach: 0, 1, 2, 4, 5, 7")

    while True:
        intervals_input = input("\nEnter intervals (comma-separated): ").strip()
        try:
            intervals = [int(x.strip()) for x in intervals_input.split(',')]
            if len(intervals) < 3:
                print("Need at least 3 intervals. Try again.")
                continue
            lick['intervals'] = intervals
            break
        except ValueError:
            print("Invalid format. Use comma-separated numbers (e.g., 0, 2, 4, 7)")

    # Rhythm/timing
    print("\nRhythm/Timing (default: 16th notes)")
    rhythm_choice = get_user_choice("Select rhythm type:", list(RHYTHM_TYPES.keys()))
    lick['rhythm'] = rhythm_choice

    if rhythm_choice == 'custom':
        note_duration = float(input("Note duration in beats: ").strip())
        bpm = int(input("Suggested BPM: ").strip())
    else:
        note_duration = RHYTHM_TYPES[rhythm_choice]['note_duration']
        bpm_min, bpm_max = RHYTHM_TYPES[rhythm_choice]['bpm_range']
        bpm = int(input(f"BPM ({bpm_min}-{bpm_max}, press Enter for {(bpm_min+bpm_max)//2}): ").strip() or (bpm_min+bpm_max)//2)

    lick['note_duration'] = note_duration
    lick['bpm'] = bpm

    # Techniques
    print("\nTechniques used in this lick")
    print("Available techniques:")
    for i, tech in enumerate(TECHNIQUES, 1):
        print(f"  {i}. {tech}")

    tech_input = input("\nEnter technique numbers (comma-separated, or Enter to skip): ").strip()
    if tech_input:
        try:
            tech_indices = [int(x.strip()) - 1 for x in tech_input.split(',')]
            lick['techniques'] = [TECHNIQUES[i] for i in tech_indices if 0 <= i < len(TECHNIQUES)]
        except (ValueError, IndexError):
            lick['techniques'] = []
    else:
        lick['techniques'] = []

    # Description
    lick['description'] = input("\nDescription (include harmonic context): ").strip()

    # Harmonic context (important for functional harmony)
    print("\nHarmonic Context (optional but recommended)")
    chord_context = input("Chord(s) this lick works over (e.g., Dm7, G7, Cmaj7): ").strip()
    if chord_context:
        lick['chord_context'] = chord_context

    functional_harmony = input("Functional harmony (e.g., ii-V-I, I-IV-V): ").strip()
    if functional_harmony:
        lick['functional_harmony'] = functional_harmony

    return lick


def import_from_midi(midi_path: str, style: str) -> Optional[Dict]:
    """Import lick from MIDI file"""
    if not MIDI_AVAILABLE:
        print("[ERROR] MIDI support not available. Install mido: pip install mido")
        return None

    print(f"\nImporting from MIDI: {midi_path}")

    try:
        reader = MidiReader()

        # Analyze MIDI file
        analysis = reader.analyze_midi_with_theory(midi_path)

        # Extract intervals
        intervals = reader.extract_melody(midi_path)

        if not intervals:
            print("[ERROR] Could not extract melody from MIDI file")
            return None

        # Create lick from MIDI data
        lick = {
            'name': input(f"Lick name (default: {Path(midi_path).stem}): ").strip() or Path(midi_path).stem,
            'artist': input("Artist: ").strip() or "MIDI Import",
            'style': style,
            'intervals': intervals,
            'rhythm': '16ths',  # Default to 16ths
            'note_duration': 0.25,
            'bpm': int(analysis.get('tempo', 120)),
            'techniques': [],
            'description': input("Description: ").strip() or f"Imported from {Path(midi_path).name}"
        }

        # Add detected key information
        detected_key = analysis.get('detected_key', {})
        if detected_key and detected_key.get('key'):
            lick['detected_key'] = f"{detected_key['key']} {detected_key.get('mode', '')}"
            lick['description'] += f" | Detected key: {lick['detected_key']}"

        print(f"[OK] Imported {len(intervals)} notes from MIDI")
        print(f"     Tempo: {lick['bpm']} BPM")
        if 'detected_key' in lick:
            print(f"     Key: {lick['detected_key']}")

        return lick

    except Exception as e:
        print(f"[ERROR] Failed to import MIDI: {e}")
        return None


def import_from_audio(audio_path: str, style: str) -> Optional[Dict]:
    """Import lick from audio file (experimental)"""
    if not AUDIO_AVAILABLE:
        print("[ERROR] Audio analysis not available. Install librosa: pip install librosa soundfile")
        return None

    print(f"\nAnalyzing audio: {audio_path}")
    print("[NOTE] Audio-to-lick conversion is experimental")

    try:
        analyzer = AudioAnalyzer()
        analysis = analyzer.analyze_audio_file(audio_path)

        print(f"\nDetected:")
        print(f"  Tempo: {analysis.get('tempo', 'Unknown')} BPM")
        print(f"  Key: {analysis.get('key', 'Unknown')} {analysis.get('mode', '')}")

        # Since we can't extract exact notes from audio easily,
        # prompt user to enter intervals manually
        print("\n[INFO] Please manually enter the interval pattern from the audio")

        intervals_input = input("Enter intervals (comma-separated): ").strip()
        try:
            intervals = [int(x.strip()) for x in intervals_input.split(',')]
        except ValueError:
            print("[ERROR] Invalid interval format")
            return None

        lick = {
            'name': input(f"Lick name (default: {Path(audio_path).stem}): ").strip() or Path(audio_path).stem,
            'artist': input("Artist: ").strip() or "Audio Import",
            'style': style,
            'intervals': intervals,
            'rhythm': '16ths',
            'note_duration': 0.25,
            'bpm': int(analysis.get('tempo', 120)),
            'techniques': [],
            'description': input("Description: ").strip() or f"Transcribed from {Path(audio_path).name}",
            'detected_key': f"{analysis.get('key', '')} {analysis.get('mode', '')}".strip()
        }

        return lick

    except Exception as e:
        print(f"[ERROR] Failed to analyze audio: {e}")
        return None


def import_from_csv(csv_path: str) -> List[Dict]:
    """Import multiple licks from CSV file"""
    print(f"\nImporting from CSV: {csv_path}")

    licks = []

    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Parse intervals
                intervals_str = row.get('intervals', '')
                try:
                    intervals = [int(x.strip()) for x in intervals_str.split(',')]
                except ValueError:
                    print(f"[WARNING] Skipping row with invalid intervals: {row.get('name', 'Unknown')}")
                    continue

                # Parse techniques
                techniques_str = row.get('techniques', '')
                techniques = [t.strip() for t in techniques_str.split(';') if t.strip()]

                lick = {
                    'name': row.get('name', 'Untitled'),
                    'artist': row.get('artist', 'Unknown'),
                    'style': row.get('style', 'blues'),
                    'intervals': intervals,
                    'rhythm': row.get('rhythm', '16ths'),
                    'note_duration': float(row.get('note_duration', 0.25)),
                    'bpm': int(row.get('bpm', 120)),
                    'techniques': techniques,
                    'description': row.get('description', '')
                }

                # Optional fields
                if row.get('chord_context'):
                    lick['chord_context'] = row.get('chord_context')
                if row.get('functional_harmony'):
                    lick['functional_harmony'] = row.get('functional_harmony')

                licks.append(lick)
                print(f"[OK] Imported: {lick['name']}")

        print(f"\nImported {len(licks)} licks from CSV")
        return licks

    except FileNotFoundError:
        print(f"[ERROR] File not found: {csv_path}")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to import CSV: {e}")
        return []


def save_lick_to_json(lick: Dict, output_dir: str = "training_data"):
    """Save lick to JSON file"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate filename
    safe_name = lick['name'].replace(' ', '_').replace('/', '-')
    filename = f"{lick['style']}_{safe_name}.json"

    file_path = output_path / filename

    with open(file_path, 'w') as f:
        json.dump(lick, f, indent=2)

    print(f"[OK] Saved to: {file_path}")
    return file_path


def create_csv_template(output_path: str = "lick_template.csv"):
    """Create a CSV template for batch import"""
    headers = [
        'name', 'artist', 'style', 'intervals', 'rhythm', 'note_duration',
        'bpm', 'techniques', 'description', 'chord_context', 'functional_harmony'
    ]

    example_rows = [
        {
            'name': 'Example Lick 1',
            'artist': 'John Doe',
            'style': 'jazz',
            'intervals': '0, 2, 4, 5, 7, 9, 11, 12',
            'rhythm': '16ths',
            'note_duration': '0.25',
            'bpm': '140',
            'techniques': 'legato; alternate picking; chromatic approach',
            'description': 'Jazz major scale run with chromatic approaches',
            'chord_context': 'Cmaj7',
            'functional_harmony': 'I chord'
        },
        {
            'name': 'Example Lick 2',
            'artist': 'Jane Smith',
            'style': 'blues',
            'intervals': '0, 3, 5, 6, 7, 10, 12',
            'rhythm': '16ths',
            'note_duration': '0.25',
            'bpm': '90',
            'techniques': 'bends; vibrato',
            'description': 'Blues pentatonic with b5 (blues note)',
            'chord_context': 'A7',
            'functional_harmony': 'I7 blues'
        }
    ]

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(example_rows)

    print(f"[OK] Created CSV template: {output_path}")
    print("Edit this file and import with: python add_training_data.py --from-csv lick_template.csv")


def main():
    parser = argparse.ArgumentParser(
        description='Add licks and progressions to training data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python add_training_data.py --interactive

  # Import from MIDI
  python add_training_data.py --from-midi solo.mid --style jazz

  # Import from audio (experimental)
  python add_training_data.py --from-audio guitar.wav --style blues

  # Batch import from CSV
  python add_training_data.py --from-csv my_licks.csv

  # Create CSV template
  python add_training_data.py --create-template

Note: Default assumes 16th notes (0.25 beat duration) but can be customized
        """
    )

    # Input modes (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--interactive', action='store_true',
                           help='Interactive CLI input mode')
    mode_group.add_argument('--from-midi', type=str, metavar='FILE',
                           help='Import from MIDI file')
    mode_group.add_argument('--from-audio', type=str, metavar='FILE',
                           help='Import from audio file (experimental)')
    mode_group.add_argument('--from-csv', type=str, metavar='FILE',
                           help='Batch import from CSV file')
    mode_group.add_argument('--create-template', action='store_true',
                           help='Create CSV template for batch import')

    # Optional arguments
    parser.add_argument('--style', type=str, choices=VALID_STYLES,
                       help='Musical style (required for MIDI/audio import)')
    parser.add_argument('--output-dir', type=str, default='training_data',
                       help='Output directory (default: training_data)')
    parser.add_argument('--no-save', action='store_true',
                       help='Preview only, do not save')

    args = parser.parse_args()

    # Validate style for MIDI/audio import
    if (args.from_midi or args.from_audio) and not args.style:
        parser.error("--style is required for MIDI/audio import")

    print_section("TRAINING DATA INPUT")

    # Handle different input modes
    licks = []

    if args.create_template:
        create_csv_template()
        return 0

    elif args.interactive:
        lick = interactive_lick_input()
        licks = [lick]

    elif args.from_midi:
        lick = import_from_midi(args.from_midi, args.style)
        if lick:
            licks = [lick]

    elif args.from_audio:
        lick = import_from_audio(args.from_audio, args.style)
        if lick:
            licks = [lick]

    elif args.from_csv:
        licks = import_from_csv(args.from_csv)

    # Preview and save
    if not licks:
        print("[ERROR] No licks to save")
        return 1

    print_section("PREVIEW")
    for lick in licks:
        print(f"Name: {lick['name']}")
        print(f"Artist: {lick['artist']}")
        print(f"Style: {lick['style']}")
        print(f"Intervals: {lick['intervals']}")
        print(f"Rhythm: {lick['rhythm']} @ {lick.get('bpm', 120)} BPM")
        print(f"Note duration: {lick.get('note_duration', 0.25)} beats (16th note = 0.25)")
        print(f"Description: {lick['description']}")
        if lick.get('techniques'):
            print(f"Techniques: {', '.join(lick['techniques'])}")
        if lick.get('chord_context'):
            print(f"Chord context: {lick['chord_context']}")
        if lick.get('functional_harmony'):
            print(f"Functional harmony: {lick['functional_harmony']}")
        print()

    # Save
    if not args.no_save:
        confirm = input(f"Save {len(licks)} lick(s) to {args.output_dir}? (y/n): ").strip().lower()
        if confirm == 'y':
            for lick in licks:
                save_lick_to_json(lick, args.output_dir)
            print(f"\n[OK] Saved {len(licks)} lick(s)")
            print(f"Next steps:")
            print(f"1. Review JSON files in {args.output_dir}/")
            print(f"2. Integrate into src/recommender.py lick database")
            print(f"3. Run: python test_lick_quality.py to validate quality")
        else:
            print("Cancelled")

    return 0


if __name__ == '__main__':
    sys.exit(main())
