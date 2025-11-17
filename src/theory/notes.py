"""
Musical note and pitch representations.
Provides classes for working with notes, pitches, and intervals.
"""

from enum import Enum
from typing import Optional, Union
from dataclasses import dataclass


class NoteName(Enum):
    """Chromatic note names"""
    C = 0
    C_SHARP = 1
    D_FLAT = 1
    D = 2
    D_SHARP = 3
    E_FLAT = 3
    E = 4
    F = 5
    F_SHARP = 6
    G_FLAT = 6
    G = 7
    G_SHARP = 8
    A_FLAT = 8
    A = 9
    A_SHARP = 10
    B_FLAT = 10
    B = 11


# Mapping for natural notes
NATURAL_NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

# Sharp and flat representations
SHARP_NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
FLAT_NOTES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']


@dataclass
class Note:
    """
    Represents a musical note with pitch class (without octave).

    Attributes:
        pitch_class: Integer 0-11 representing chromatic pitch
        name: String representation (e.g., 'C', 'F#', 'Bb')
        prefer_sharp: Use sharp notation instead of flat
    """
    pitch_class: int
    name: Optional[str] = None
    prefer_sharp: bool = True

    def __post_init__(self):
        # Normalize pitch class to 0-11
        self.pitch_class = self.pitch_class % 12

        # Auto-generate name if not provided
        if self.name is None:
            if self.prefer_sharp:
                self.name = SHARP_NOTES[self.pitch_class]
            else:
                self.name = FLAT_NOTES[self.pitch_class]

    @classmethod
    def from_string(cls, note_str: str) -> 'Note':
        """
        Create a Note from string representation.

        Examples:
            Note.from_string('C') -> Note(0, 'C')
            Note.from_string('F#') -> Note(6, 'F#')
            Note.from_string('Bb') -> Note(10, 'Bb')
        """
        note_str = note_str.strip()

        # Parse base note
        base = note_str[0].upper()
        if base not in NATURAL_NOTES:
            raise ValueError(f"Invalid note: {note_str}")

        # Get base pitch class
        pitch_class = NATURAL_NOTES.index(base) * 2
        if base in ['E', 'B']:
            pitch_class -= 1
        if base >= 'C':
            pitch_class = pitch_class % 12

        # Handle accidentals
        if len(note_str) > 1:
            accidental = note_str[1:]
            if '#' in accidental or '♯' in accidental:
                pitch_class += accidental.count('#') + accidental.count('♯')
            elif 'b' in accidental or '♭' in accidental:
                pitch_class -= accidental.count('b') + accidental.count('♭')

        prefer_sharp = '#' in note_str or '♯' in note_str

        return cls(pitch_class, note_str, prefer_sharp)

    def transpose(self, semitones: int) -> 'Note':
        """Transpose note by given number of semitones"""
        new_pitch_class = (self.pitch_class + semitones) % 12
        return Note(new_pitch_class, prefer_sharp=self.prefer_sharp)

    def interval_to(self, other: 'Note') -> int:
        """Calculate interval in semitones to another note"""
        return (other.pitch_class - self.pitch_class) % 12

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Note('{self.name}', pc={self.pitch_class})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Note):
            return self.pitch_class == other.pitch_class
        return False

    def __hash__(self) -> int:
        return hash(self.pitch_class)


@dataclass
class Pitch:
    """
    Represents a musical pitch with specific octave.

    Attributes:
        note: The Note (pitch class)
        octave: Octave number (MIDI convention: C4 = middle C)
    """
    note: Note
    octave: int = 4

    @property
    def midi_number(self) -> int:
        """Convert to MIDI note number (0-127)"""
        return (self.octave + 1) * 12 + self.note.pitch_class

    @classmethod
    def from_midi(cls, midi_number: int, prefer_sharp: bool = True) -> 'Pitch':
        """Create Pitch from MIDI note number"""
        octave = (midi_number // 12) - 1
        pitch_class = midi_number % 12
        note = Note(pitch_class, prefer_sharp=prefer_sharp)
        return cls(note, octave)

    @classmethod
    def from_string(cls, pitch_str: str) -> 'Pitch':
        """
        Create Pitch from string like 'C4', 'F#5', 'Bb3'
        """
        # Split note name and octave
        import re
        match = re.match(r'([A-Ga-g][#b♯♭]*)([-\d]+)', pitch_str)
        if not match:
            raise ValueError(f"Invalid pitch string: {pitch_str}")

        note_str, octave_str = match.groups()
        note = Note.from_string(note_str)
        octave = int(octave_str)

        return cls(note, octave)

    def transpose(self, semitones: int) -> 'Pitch':
        """Transpose pitch by semitones, handling octave changes"""
        new_midi = self.midi_number + semitones
        return Pitch.from_midi(new_midi, self.note.prefer_sharp)

    def __str__(self) -> str:
        return f"{self.note}{self.octave}"

    def __repr__(self) -> str:
        return f"Pitch('{self.note}{self.octave}', midi={self.midi_number})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Pitch):
            return self.midi_number == other.midi_number
        return False

    def __lt__(self, other: 'Pitch') -> bool:
        return self.midi_number < other.midi_number

    def __hash__(self) -> int:
        return hash(self.midi_number)


class Interval:
    """
    Represents a musical interval.

    Attributes:
        semitones: Number of semitones in the interval
        name: Common name (e.g., 'perfect fifth', 'major third')
    """

    # Common interval names
    INTERVAL_NAMES = {
        0: 'unison',
        1: 'minor second',
        2: 'major second',
        3: 'minor third',
        4: 'major third',
        5: 'perfect fourth',
        6: 'tritone',
        7: 'perfect fifth',
        8: 'minor sixth',
        9: 'major sixth',
        10: 'minor seventh',
        11: 'major seventh',
        12: 'octave'
    }

    def __init__(self, semitones: int):
        self.semitones = semitones
        self.name = self.INTERVAL_NAMES.get(semitones % 12, f'{semitones} semitones')

    @classmethod
    def between(cls, note1: Union[Note, Pitch], note2: Union[Note, Pitch]) -> 'Interval':
        """Calculate interval between two notes or pitches"""
        if isinstance(note1, Pitch) and isinstance(note2, Pitch):
            semitones = note2.midi_number - note1.midi_number
        else:
            if isinstance(note1, Pitch):
                note1 = note1.note
            if isinstance(note2, Pitch):
                note2 = note2.note
            semitones = note1.interval_to(note2)

        return cls(semitones)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Interval({self.semitones}, '{self.name}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, Interval):
            return self.semitones == other.semitones
        return False
