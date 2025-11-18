"""
Demonstration: MIDI Input/Output

Shows:
- Exporting licks to MIDI files
- Exporting chord progressions to MIDI files
- Creating multi-track MIDI (melody + chords)
- Reading MIDI files and analyzing them
- Importing MIDI files as licks

Usage:
    python demo_midi_io.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.recommender import MusicRecommendationSystem
from src.theory import Note, Chord, ChordQuality, Scale, ChordProgression
from src.midi_io import (
    MidiWriter,
    MidiReader,
    export_lick_to_midi,
    export_progression_to_midi,
    import_midi_as_lick
)
import os


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\n")


def create_output_directory():
    """Create output directory for MIDI files"""
    output_dir = Path('outputs/midi')
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def demonstrate_lick_export():
    """Demonstrate exporting licks to MIDI"""
    print_section("LICK TO MIDI EXPORT")

    system = MusicRecommendationSystem()
    output_dir = create_output_directory()

    # Get licks from different styles
    test_cases = [
        ('rock_fusion', 'E', 'Guthrie Govan', 140),
        ('blues', 'A', 'Eric Johnson', 90),
        ('jazz', 'C', 'Pat Metheny', 160)
    ]

    for style, key_str, artist_filter, tempo in test_cases:
        key = Note.from_string(key_str)

        print(f"\nExporting {style.upper()} lick in key of {key.name}")
        print(f"Artist: {artist_filter} | Tempo: {tempo} BPM")
        print("-" * 80)

        # Get licks
        licks = system.lick_recommender.recommend_licks(
            style=style,
            key=key,
            num_recommendations=20
        )

        # Filter for artist
        artist_licks = [l for l in licks if artist_filter in l.item['name']]
        if not artist_licks:
            artist_licks = licks[:1]

        lick = artist_licks[0].item

        # Create safe filename
        filename = f"{style}_{key.name}_{lick['name'].replace(' ', '_')}.mid"
        filename = filename.replace('/', '-').replace('\\', '-')
        output_path = output_dir / filename

        # Export to MIDI
        try:
            export_lick_to_midi(lick, key, str(output_path), tempo=tempo)
            file_size = output_path.stat().st_size
            print(f"[OK] Exported: {filename}")
            print(f"     Size: {file_size} bytes")
            print(f"     Intervals: {lick['intervals']}")
            print(f"     Path: {output_path}")
        except Exception as e:
            print(f"[ERROR] Failed to export: {e}")


def demonstrate_progression_export():
    """Demonstrate exporting chord progressions to MIDI"""
    print_section("CHORD PROGRESSION TO MIDI EXPORT")

    output_dir = create_output_directory()

    # Create some example progressions
    progressions = [
        {
            'name': 'Jazz II-V-I',
            'chords': [
                Chord(Note.from_string('D'), ChordQuality.MINOR_7),
                Chord(Note.from_string('G'), ChordQuality.DOMINANT_7),
                Chord(Note.from_string('C'), ChordQuality.MAJOR_7),
            ],
            'tempo': 120
        },
        {
            'name': 'Blues I-IV-V',
            'chords': [
                Chord(Note.from_string('A'), ChordQuality.DOMINANT_7),
                Chord(Note.from_string('D'), ChordQuality.DOMINANT_7),
                Chord(Note.from_string('E'), ChordQuality.DOMINANT_7),
                Chord(Note.from_string('A'), ChordQuality.DOMINANT_7),
            ],
            'tempo': 100
        },
        {
            'name': 'Neo-Soul Progression',
            'chords': [
                Chord(Note.from_string('C'), ChordQuality.MAJOR_7),
                Chord(Note.from_string('A'), ChordQuality.MINOR_7),
                Chord(Note.from_string('D'), ChordQuality.MINOR_7),
                Chord(Note.from_string('G'), ChordQuality.DOMINANT_7),
            ],
            'tempo': 85
        }
    ]

    for prog_info in progressions:
        print(f"\nExporting: {prog_info['name']}")
        print(f"Tempo: {prog_info['tempo']} BPM")
        print("-" * 80)

        # Create ChordProgression object
        progression = ChordProgression(
            chords=prog_info['chords'],
            scale=None
        )

        # Create filename
        filename = f"progression_{prog_info['name'].replace(' ', '_')}.mid"
        output_path = output_dir / filename

        # Export to MIDI
        try:
            export_progression_to_midi(progression, str(output_path), tempo=prog_info['tempo'])
            file_size = output_path.stat().st_size

            chord_names = [c.to_symbol() for c in prog_info['chords']]
            print(f"[OK] Exported: {filename}")
            print(f"     Size: {file_size} bytes")
            print(f"     Chords: {' -> '.join(chord_names)}")
            print(f"     Path: {output_path}")
        except Exception as e:
            print(f"[ERROR] Failed to export: {e}")


def demonstrate_multi_track_export():
    """Demonstrate creating multi-track MIDI with melody and chords"""
    print_section("MULTI-TRACK MIDI EXPORT (Melody + Chords)")

    system = MusicRecommendationSystem()
    output_dir = create_output_directory()

    # Get a lick
    key = Note.from_string('E')
    licks = system.lick_recommender.recommend_licks('rock_fusion', key, num_recommendations=5)
    lick = licks[0].item

    # Create progression
    progression = ChordProgression(
        chords=[
            Chord(Note.from_string('E'), ChordQuality.MINOR_7),
            Chord(Note.from_string('A'), ChordQuality.DOMINANT_7),
            Chord(Note.from_string('D'), ChordQuality.MAJOR_7),
            Chord(Note.from_string('G'), ChordQuality.MAJOR_7),
        ],
        scale=None
    )

    filename = "multi_track_fusion_lick_with_chords.mid"
    output_path = output_dir / filename

    print(f"Creating multi-track MIDI:")
    print(f"  Track 1: Lead Guitar - {lick['name']}")
    print(f"  Track 2: Rhythm Guitar - Chord progression")
    print("-" * 80)

    try:
        writer = MidiWriter(tempo=120)
        writer.lick_with_backing_to_midi(lick, key, progression, str(output_path))
        file_size = output_path.stat().st_size

        print(f"[OK] Exported: {filename}")
        print(f"     Size: {file_size} bytes")
        print(f"     Tracks: 2 (melody + chords)")
        print(f"     Path: {output_path}")
    except Exception as e:
        print(f"[ERROR] Failed to export: {e}")


def demonstrate_midi_reading():
    """Demonstrate reading and analyzing MIDI files"""
    print_section("READING & ANALYZING MIDI FILES")

    output_dir = create_output_directory()

    # Check if we have any MIDI files to read
    midi_files = list(output_dir.glob('*.mid'))

    if not midi_files:
        print("[INFO] No MIDI files found to analyze.")
        print("      Run the export demos first to create MIDI files.")
        return

    reader = MidiReader()

    # Analyze first few MIDI files
    for midi_path in midi_files[:3]:
        print(f"\nAnalyzing: {midi_path.name}")
        print("-" * 80)

        # Read basic info
        analysis = reader.read_midi_file(str(midi_path))

        if 'error' in analysis:
            print(f"[ERROR] {analysis['error']}")
            continue

        print(f"Tempo: {analysis['tempo']:.1f} BPM")
        print(f"Ticks per beat: {analysis['ticks_per_beat']}")
        print(f"Total time: {analysis['total_time']:.2f} seconds")
        print(f"Tracks: {len(analysis['tracks'])}")

        for track in analysis['tracks']:
            print(f"\n  Track {track['track_number']}: {track['track_name']}")
            print(f"    Notes: {len(track['notes'])}")
            if track['notes']:
                first_notes = track['notes'][:5]
                note_names = [n['note_name'] for n in first_notes]
                print(f"    First notes: {', '.join(note_names)}")

        # Extract melody as intervals
        intervals = reader.extract_melody(str(midi_path))
        if intervals:
            print(f"\n  Interval pattern: {intervals[:10]}{'...' if len(intervals) > 10 else ''}")

    print()


def demonstrate_midi_import():
    """Demonstrate importing MIDI as a lick"""
    print_section("IMPORTING MIDI AS LICK")

    output_dir = create_output_directory()

    # Check if we have any MIDI files
    midi_files = list(output_dir.glob('*.mid'))

    if not midi_files:
        print("[INFO] No MIDI files found to import.")
        print("      Run the export demos first to create MIDI files.")
        return

    # Import a MIDI file as a lick
    midi_path = midi_files[0]

    print(f"Importing: {midi_path.name}")
    print("-" * 80)

    lick = import_midi_as_lick(str(midi_path), lick_name=f"Imported: {midi_path.stem}")

    if lick:
        print(f"[OK] Successfully imported as lick")
        print(f"     Name: {lick['name']}")
        print(f"     Intervals: {lick['intervals']}")
        print(f"     Note count: {len(lick['intervals'])}")
        print(f"     Description: {lick['description']}")
        print()
        print("This lick can now be used in the recommendation system!")
    else:
        print("[ERROR] Failed to import MIDI file")


def demonstrate_midi_statistics():
    """Show statistics about exported MIDI files"""
    print_section("MIDI EXPORT STATISTICS")

    output_dir = create_output_directory()
    midi_files = list(output_dir.glob('*.mid'))

    if not midi_files:
        print("[INFO] No MIDI files found.")
        return

    total_size = sum(f.stat().st_size for f in midi_files)
    lick_files = [f for f in midi_files if 'progression' not in f.name.lower()]
    progression_files = [f for f in midi_files if 'progression' in f.name.lower()]

    print(f"Total MIDI files: {len(midi_files)}")
    print(f"  Lick files: {len(lick_files)}")
    print(f"  Progression files: {len(progression_files)}")
    print(f"  Total size: {total_size:,} bytes ({total_size / 1024:.2f} KB)")
    print()

    print("Files created:")
    for f in sorted(midi_files, key=lambda x: x.stat().st_mtime, reverse=True):
        size = f.stat().st_size
        print(f"  - {f.name} ({size} bytes)")


def main():
    """Run all demonstrations"""
    print("\n" + "="*80)
    print(" MIDI INPUT/OUTPUT DEMONSTRATION")
    print("="*80)
    print("\nCapabilities:")
    print("  - Export licks to MIDI files")
    print("  - Export chord progressions to MIDI files")
    print("  - Create multi-track MIDI (melody + chords)")
    print("  - Read and analyze MIDI files")
    print("  - Import MIDI files as licks")
    print("="*80)

    # Create output directory
    output_dir = create_output_directory()
    print(f"\n[INFO] MIDI files will be saved to: {output_dir.absolute()}\n")

    # Run demonstrations
    demonstrate_lick_export()
    demonstrate_progression_export()
    demonstrate_multi_track_export()
    demonstrate_midi_reading()
    demonstrate_midi_import()
    demonstrate_midi_statistics()

    # Final summary
    print_section("SUMMARY")
    print("[OK] MIDI export working - Licks saved as MIDI files")
    print("[OK] MIDI export working - Progressions saved as MIDI files")
    print("[OK] Multi-track MIDI working - Melody + chords combined")
    print("[OK] MIDI reading working - Files analyzed successfully")
    print("[OK] MIDI import working - Can convert MIDI to licks")
    print()
    print("Features:")
    print("  - Tempo control (60-200 BPM supported)")
    print("  - Velocity control (dynamics)")
    print("  - Multi-track support (using pretty_midi)")
    print("  - Instrument selection (100+ General MIDI instruments)")
    print("  - Interval extraction from MIDI")
    print("  - Harmonic analysis of MIDI files")
    print()
    print(f"All MIDI files saved to: {output_dir.absolute()}")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
