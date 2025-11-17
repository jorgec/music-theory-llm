"""
Basic Usage Examples for Music Theory ML Model

This script shows simple, practical examples of using the music theory library.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.theory import Note, Pitch, Chord, Scale, ChordProgression
from src.theory.progressions import get_common_progression
from src.tokenizer import MusicTheoryTokenizer


def example_notes_and_pitches():
    """Working with notes and pitches"""
    print("=" * 60)
    print("NOTES AND PITCHES")
    print("=" * 60)
    print()

    # Create notes
    c = Note.from_string('C')
    f_sharp = Note.from_string('F#')
    b_flat = Note.from_string('Bb')

    print(f"Notes: {c}, {f_sharp}, {b_flat}")

    # Transpose notes
    d = c.transpose(2)  # Up a major second
    print(f"{c} transposed up 2 semitones: {d}")

    # Calculate intervals
    interval = c.interval_to(f_sharp)
    print(f"Interval from {c} to {f_sharp}: {interval} semitones")

    # Create pitches (notes with octaves)
    middle_c = Pitch.from_string('C4')
    print(f"\nMiddle C: {middle_c} (MIDI: {middle_c.midi_number})")

    # Transpose pitches
    high_c = middle_c.transpose(12)
    print(f"Octave above: {high_c}")

    print()


def example_scales():
    """Working with scales"""
    print("=" * 60)
    print("SCALES")
    print("=" * 60)
    print()

    # Create major scale
    c_major = Scale.major(Note.from_string('C'))
    print(f"C Major Scale: {c_major}")

    # Access scale degrees
    print(f"5th degree: {c_major.degree(5)}")
    print(f"Scale contains D: {c_major.contains(Note.from_string('D'))}")
    print(f"Scale contains C#: {c_major.contains(Note.from_string('C#'))}")

    # Minor scale
    a_minor = Scale.minor(Note.from_string('A'))
    print(f"\nA Natural Minor: {a_minor}")

    # Harmonic minor
    a_harmonic = Scale.minor(Note.from_string('A'), harmonic=True)
    print(f"A Harmonic Minor: {a_harmonic}")

    # Relative and parallel scales
    relative_minor = c_major.relative_minor()
    print(f"\nRelative minor of C major: {relative_minor}")

    parallel_minor = c_major.parallel_minor()
    print(f"Parallel minor of C major: {parallel_minor}")

    print()


def example_chords():
    """Working with chords"""
    print("=" * 60)
    print("CHORDS")
    print("=" * 60)
    print()

    # Create chords from symbols
    c_major = Chord.from_symbol('C')
    d_minor = Chord.from_symbol('Dm')
    g7 = Chord.from_symbol('G7')
    fmaj7 = Chord.from_symbol('Fmaj7')

    print("Basic chords:")
    for chord in [c_major, d_minor, g7, fmaj7]:
        notes = ', '.join(str(n) for n in chord.notes)
        print(f"  {chord}: {notes}")

    # Chord properties
    print(f"\n{c_major} is major: {c_major.is_major()}")
    print(f"{d_minor} is minor: {d_minor.is_minor()}")
    print(f"{g7} contains F: {g7.contains(Note.from_string('F'))}")

    # Inversions
    c_first_inv = c_major.inversion(1)
    print(f"\n{c_major} first inversion: {c_first_inv} (bass: {c_first_inv.bass_note})")

    print()


def example_chord_progressions():
    """Working with chord progressions"""
    print("=" * 60)
    print("CHORD PROGRESSIONS")
    print("=" * 60)
    print()

    # Create from scale degrees
    c_major_scale = Scale.major(Note.from_string('C'))
    prog1 = ChordProgression.from_degrees([1, 4, 5, 1], c_major_scale)

    print("Progression from degrees [1, 4, 5, 1]:")
    print(prog1)
    print()

    # Common progressions
    pop_progression = get_common_progression('I-V-vi-IV', c_major_scale)
    print("Popular I-V-vi-IV progression:")
    print(pop_progression)
    print()

    # Analyze cadence
    print(f"Cadence type: {prog1.get_cadence_type()}")

    # Transpose progression
    d_major_scale = Scale.major(Note.from_string('D'))
    transposed = prog1.to_key(d_major_scale)
    print(f"\nTransposed to D major:")
    print(transposed)

    print()


def example_tokenization():
    """Working with the tokenizer"""
    print("=" * 60)
    print("TOKENIZATION")
    print("=" * 60)
    print()

    tokenizer = MusicTheoryTokenizer()
    print(f"Vocabulary size: {len(tokenizer)}")

    # Tokenize different objects
    note = Note.from_string('C')
    note_tokens = tokenizer.encode(note)
    print(f"\nNote '{note}' tokens: {note_tokens}")
    print(f"Decoded: {tokenizer.decode(note_tokens)}")

    chord = Chord.from_symbol('Dm7')
    chord_tokens = tokenizer.encode(chord)
    print(f"\nChord '{chord}' tokens: {chord_tokens}")
    print(f"Decoded: {tokenizer.decode(chord_tokens)}")

    scale = Scale.major(Note.from_string('G'))
    scale_tokens = tokenizer.encode(scale)
    print(f"\nScale '{scale.root} Major' tokens: {scale_tokens}")
    print(f"Decoded: {tokenizer.decode(scale_tokens)}")

    # Batch encoding
    chords = [
        Chord.from_symbol('C'),
        Chord.from_symbol('F'),
        Chord.from_symbol('G')
    ]

    batch = tokenizer.batch_encode(chords, padding=True)
    print(f"\nBatch encoding 3 chords:")
    print(f"Input IDs shape: {len(batch['input_ids'])} x {len(batch['input_ids'][0])}")
    print(f"First chord tokens: {batch['input_ids'][0]}")

    print()


def example_music_theory_queries():
    """Common music theory queries"""
    print("=" * 60)
    print("MUSIC THEORY QUERIES")
    print("=" * 60)
    print()

    # What notes are in this chord?
    chord = Chord.from_symbol('Cmaj7')
    print(f"Q: What notes are in {chord}?")
    print(f"A: {', '.join(str(n) for n in chord.notes)}")

    # What chords are in this key?
    scale = Scale.major(Note.from_string('G'))
    print(f"\nQ: What are the diatonic chords in {scale.root} major?")
    from src.theory import chord_from_scale_degree
    for i in range(1, 8):
        chord = chord_from_scale_degree(scale, i, seventh=True)
        print(f"   {i}. {chord}")

    # What scale contains these notes?
    notes = [Note.from_string(n) for n in ['D', 'E', 'F#', 'G', 'A']]
    d_major = Scale.major(Note.from_string('D'))
    contains_all = all(d_major.contains(n) for n in notes)
    print(f"\nQ: Does D major scale contain {', '.join(str(n) for n in notes)}?")
    print(f"A: {'Yes' if contains_all else 'No'}")

    # Transpose a progression
    print(f"\nQ: Transpose I-IV-V from C to E:")
    c_scale = Scale.major(Note.from_string('C'))
    prog_c = ChordProgression.from_degrees([1, 4, 5], c_scale)
    print(f"   In C: {' - '.join(str(c) for c in prog_c.chords)}")

    e_scale = Scale.major(Note.from_string('E'))
    prog_e = prog_c.to_key(e_scale)
    print(f"   In E: {' - '.join(str(c) for c in prog_e.chords)}")

    print()


if __name__ == '__main__':
    print("\n")
    print("█" * 60)
    print("  MUSIC THEORY ML MODEL - BASIC USAGE")
    print("█" * 60)
    print("\n")

    example_notes_and_pitches()
    example_scales()
    example_chords()
    example_chord_progressions()
    example_tokenization()
    example_music_theory_queries()

    print("=" * 60)
    print("✓ Basic usage examples completed!")
    print()
    print("Next steps:")
    print("  • Run melody_suggestions_demo.py for melody features")
    print("  • Run harmonic_analysis_demo.py for advanced harmony")
    print("  • Run train.py to train your own model")
    print("=" * 60)
    print()
