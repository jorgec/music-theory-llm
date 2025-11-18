"""
Musical chord representations.
Provides classes for working with chords and chord qualities.
"""

from enum import Enum
from typing import List, Optional, Set
from dataclasses import dataclass
from .notes import Note, Interval


class ChordQuality(Enum):
    """
    Common chord qualities defined by their interval patterns from the root.
    Intervals are in semitones from the root.
    """
    # Triads
    MAJOR = [0, 4, 7]  # Root, major 3rd, perfect 5th
    MINOR = [0, 3, 7]  # Root, minor 3rd, perfect 5th
    DIMINISHED = [0, 3, 6]  # Root, minor 3rd, diminished 5th
    AUGMENTED = [0, 4, 8]  # Root, major 3rd, augmented 5th
    SUSPENDED_2 = [0, 2, 7]  # Root, major 2nd, perfect 5th
    SUSPENDED_4 = [0, 5, 7]  # Root, perfect 4th, perfect 5th

    # Seventh chords
    MAJOR_7 = [0, 4, 7, 11]  # Major triad + major 7th
    MINOR_7 = [0, 3, 7, 10]  # Minor triad + minor 7th
    DOMINANT_7 = [0, 4, 7, 10]  # Major triad + minor 7th
    DIMINISHED_7 = [0, 3, 6, 9]  # Diminished triad + diminished 7th
    HALF_DIMINISHED_7 = [0, 3, 6, 10]  # Diminished triad + minor 7th (m7b5)
    AUGMENTED_7 = [0, 4, 8, 10]  # Augmented triad + minor 7th
    MINOR_MAJOR_7 = [0, 3, 7, 11]  # Minor triad + major 7th

    # Extended chords (9ths)
    MAJOR_9 = [0, 4, 7, 11, 14]  # Maj7 + major 9th
    MINOR_9 = [0, 3, 7, 10, 14]  # Min7 + major 9th
    DOMINANT_9 = [0, 4, 7, 10, 14]  # Dom7 + major 9th
    DOMINANT_7_FLAT_9 = [0, 4, 7, 10, 13]  # Dom7 + flat 9th (blues/jazz)
    DOMINANT_7_SHARP_9 = [0, 4, 7, 10, 15]  # Dom7 + sharp 9th (Hendrix chord)

    # Extended chords (11ths)
    DOMINANT_11 = [0, 4, 7, 10, 14, 17]  # Dom7 + 9th + 11th
    MINOR_11 = [0, 3, 7, 10, 14, 17]  # Min7 + 9th + 11th
    MAJOR_11 = [0, 4, 7, 11, 14, 17]  # Maj7 + 9th + 11th

    # Extended chords (13ths)
    DOMINANT_13 = [0, 4, 7, 10, 14, 21]  # Dom7 + 9th + 13th (jazz)
    MINOR_13 = [0, 3, 7, 10, 14, 21]  # Min7 + 9th + 13th
    MAJOR_13 = [0, 4, 7, 11, 14, 21]  # Maj7 + 9th + 13th
    DOMINANT_7_FLAT_13 = [0, 4, 7, 10, 20]  # Dom7 + flat 13th

    # Altered chords (jazz)
    ALTERED = [0, 4, 10, 13, 15, 20]  # 7alt: 1-3-b7-b9-#9-b13
    DOMINANT_7_SHARP_11 = [0, 4, 7, 10, 18]  # Lydian dominant

    # Other common chords
    POWER_CHORD = [0, 7]  # Root + perfect 5th (no 3rd)
    MAJOR_6 = [0, 4, 7, 9]  # Major triad + major 6th
    MINOR_6 = [0, 3, 7, 9]  # Minor triad + major 6th
    MAJOR_6_9 = [0, 4, 7, 9, 14]  # Major 6 + 9th
    MINOR_6_9 = [0, 3, 7, 9, 14]  # Minor 6 + 9th (jazz)


# Chord symbols mapping
CHORD_SYMBOLS = {
    ChordQuality.MAJOR: '',
    ChordQuality.MINOR: 'm',
    ChordQuality.DIMINISHED: 'dim',
    ChordQuality.AUGMENTED: 'aug',
    ChordQuality.SUSPENDED_2: 'sus2',
    ChordQuality.SUSPENDED_4: 'sus4',
    ChordQuality.MAJOR_7: 'maj7',
    ChordQuality.MINOR_7: 'm7',
    ChordQuality.DOMINANT_7: '7',
    ChordQuality.DIMINISHED_7: 'dim7',
    ChordQuality.HALF_DIMINISHED_7: 'm7b5',
    ChordQuality.AUGMENTED_7: 'aug7',
    ChordQuality.MINOR_MAJOR_7: 'mMaj7',
    # 9th chords
    ChordQuality.MAJOR_9: 'maj9',
    ChordQuality.MINOR_9: 'm9',
    ChordQuality.DOMINANT_9: '9',
    ChordQuality.DOMINANT_7_FLAT_9: '7b9',
    ChordQuality.DOMINANT_7_SHARP_9: '7#9',
    # 11th chords
    ChordQuality.DOMINANT_11: '11',
    ChordQuality.MINOR_11: 'm11',
    ChordQuality.MAJOR_11: 'maj11',
    # 13th chords
    ChordQuality.DOMINANT_13: '13',
    ChordQuality.MINOR_13: 'm13',
    ChordQuality.MAJOR_13: 'maj13',
    ChordQuality.DOMINANT_7_FLAT_13: '7b13',
    # Altered chords
    ChordQuality.ALTERED: '7alt',
    ChordQuality.DOMINANT_7_SHARP_11: '7#11',
    # Other
    ChordQuality.POWER_CHORD: '5',
    ChordQuality.MAJOR_6: '6',
    ChordQuality.MINOR_6: 'm6',
    ChordQuality.MAJOR_6_9: '6/9',
    ChordQuality.MINOR_6_9: 'm6/9',
}


@dataclass
class Chord:
    """
    Represents a musical chord.

    Attributes:
        root: The root note of the chord
        quality: The chord quality/type
        notes: List of notes in the chord
        bass_note: Optional bass note (for inversions or slash chords)
    """
    root: Note
    quality: ChordQuality
    notes: Optional[List[Note]] = None
    bass_note: Optional[Note] = None

    def __post_init__(self):
        if self.notes is None:
            self.notes = self._generate_notes()
        if self.bass_note is None:
            self.bass_note = self.root

    def _generate_notes(self) -> List[Note]:
        """Generate chord notes based on the quality's interval pattern"""
        intervals = self.quality.value
        notes = []

        for interval in intervals:
            note = self.root.transpose(interval)
            notes.append(note)

        return notes

    @classmethod
    def from_symbol(cls, symbol: str) -> 'Chord':
        """
        Parse a chord from standard chord symbol notation.

        Examples:
            'C' -> C major
            'Dm' -> D minor
            'G7' -> G dominant 7th
            'Fmaj7' -> F major 7th
            'Am7' -> A minor 7th
        """
        symbol = symbol.strip()

        # Extract root note (first 1-2 characters)
        if len(symbol) > 1 and symbol[1] in ['#', 'b', '♯', '♭']:
            root_str = symbol[:2]
            quality_str = symbol[2:]
        else:
            root_str = symbol[0]
            quality_str = symbol[1:]

        root = Note.from_string(root_str)

        # Map quality string to ChordQuality
        quality_map = {v: k for k, v in CHORD_SYMBOLS.items()}

        # Handle common variations
        quality_str_normalized = quality_str.lower()
        if quality_str_normalized == '' or quality_str_normalized == 'maj':
            quality = ChordQuality.MAJOR
        elif quality_str_normalized in ['min', 'm']:
            quality = ChordQuality.MINOR
        elif quality_str_normalized == '7':
            quality = ChordQuality.DOMINANT_7
        elif quality_str_normalized in ['maj7', 'major7', 'M7']:
            quality = ChordQuality.MAJOR_7
        elif quality_str_normalized in ['m7', 'min7', 'minor7']:
            quality = ChordQuality.MINOR_7
        elif quality_str_normalized in ['dim', 'o']:
            quality = ChordQuality.DIMINISHED
        elif quality_str_normalized in ['dim7', 'o7']:
            quality = ChordQuality.DIMINISHED_7
        elif quality_str_normalized in ['m7b5', 'ø7', 'half-dim', 'halfdiminished']:
            quality = ChordQuality.HALF_DIMINISHED_7
        elif quality_str_normalized in ['aug', '+']:
            quality = ChordQuality.AUGMENTED
        elif quality_str_normalized == 'sus2':
            quality = ChordQuality.SUSPENDED_2
        elif quality_str_normalized == 'sus4':
            quality = ChordQuality.SUSPENDED_4
        elif quality_str_normalized == '9':
            quality = ChordQuality.DOMINANT_9
        elif quality_str_normalized in ['maj9', 'M9']:
            quality = ChordQuality.MAJOR_9
        elif quality_str_normalized == 'm9':
            quality = ChordQuality.MINOR_9
        elif quality_str_normalized == '6':
            quality = ChordQuality.MAJOR_6
        elif quality_str_normalized == 'm6':
            quality = ChordQuality.MINOR_6
        elif quality_str_normalized == '5':
            quality = ChordQuality.POWER_CHORD
        else:
            raise ValueError(f"Unknown chord quality: {quality_str}")

        return cls(root, quality)

    def inversion(self, inversion_num: int) -> 'Chord':
        """
        Get a specific inversion of the chord.

        Args:
            inversion_num: 0 = root position, 1 = first inversion, 2 = second inversion, etc.

        Returns:
            New chord with updated bass note
        """
        if inversion_num >= len(self.notes):
            raise ValueError(f"Cannot create inversion {inversion_num} for {len(self.notes)}-note chord")

        new_chord = Chord(self.root, self.quality, self.notes.copy())
        new_chord.bass_note = self.notes[inversion_num]
        return new_chord

    def contains(self, note: Note) -> bool:
        """Check if a note is in the chord"""
        return any(n.pitch_class == note.pitch_class for n in self.notes)

    def get_intervals(self) -> List[Interval]:
        """Get all intervals from the root"""
        return [Interval(n.pitch_class - self.root.pitch_class) for n in self.notes]

    def is_major(self) -> bool:
        """Check if chord has major quality"""
        return self.quality in [
            ChordQuality.MAJOR,
            ChordQuality.MAJOR_7,
            ChordQuality.MAJOR_9,
            ChordQuality.MAJOR_6
        ]

    def is_minor(self) -> bool:
        """Check if chord has minor quality"""
        return self.quality in [
            ChordQuality.MINOR,
            ChordQuality.MINOR_7,
            ChordQuality.MINOR_9,
            ChordQuality.MINOR_6,
            ChordQuality.MINOR_MAJOR_7
        ]

    def is_diminished(self) -> bool:
        """Check if chord is diminished"""
        return self.quality in [ChordQuality.DIMINISHED, ChordQuality.DIMINISHED_7, ChordQuality.HALF_DIMINISHED_7]

    def is_augmented(self) -> bool:
        """Check if chord is augmented"""
        return self.quality in [ChordQuality.AUGMENTED, ChordQuality.AUGMENTED_7]

    def to_symbol(self) -> str:
        """Convert chord to standard symbol notation"""
        symbol = str(self.root)
        symbol += CHORD_SYMBOLS.get(self.quality, '')

        # Add slash notation if bass note is different
        if self.bass_note and self.bass_note.pitch_class != self.root.pitch_class:
            symbol += f"/{self.bass_note}"

        return symbol

    def to_dict(self) -> dict:
        """Convert chord to dictionary representation"""
        return {
            'root': str(self.root),
            'quality': self.quality.name,
            'symbol': self.to_symbol(),
            'notes': [str(n) for n in self.notes],
            'bass_note': str(self.bass_note)
        }

    def __str__(self) -> str:
        return self.to_symbol()

    def __repr__(self) -> str:
        return f"Chord('{self.to_symbol()}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, Chord):
            return (self.root == other.root and
                    self.quality == other.quality and
                    self.bass_note == other.bass_note)
        return False

    def __hash__(self) -> int:
        return hash((self.root, self.quality, self.bass_note))


# Common chord progressions as Roman numeral analysis
ROMAN_NUMERALS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']


def chord_from_scale_degree(scale, degree: int, seventh: bool = False) -> Chord:
    """
    Build a chord from a scale degree.

    Args:
        scale: The scale to use
        degree: Scale degree (1-7)
        seventh: Whether to build a seventh chord

    Returns:
        The diatonic chord built on that degree
    """
    from .scales import Scale, ScaleType

    root = scale.degree(degree)

    # For major scales, use standard diatonic chord qualities
    if scale.scale_type == ScaleType.MAJOR:
        major_degrees = [1, 4, 5]
        minor_degrees = [2, 3, 6]
        diminished_degrees = [7]

        if degree in major_degrees:
            quality = ChordQuality.MAJOR_7 if seventh else ChordQuality.MAJOR
        elif degree in minor_degrees:
            quality = ChordQuality.MINOR_7 if seventh else ChordQuality.MINOR
        elif degree in diminished_degrees:
            quality = ChordQuality.HALF_DIMINISHED_7 if seventh else ChordQuality.DIMINISHED
        else:
            quality = ChordQuality.MAJOR

    # For minor scales
    elif scale.scale_type == ScaleType.NATURAL_MINOR:
        major_degrees = [3, 6, 7]
        minor_degrees = [1, 4, 5]
        diminished_degrees = [2]

        if degree in major_degrees:
            quality = ChordQuality.MAJOR_7 if seventh else ChordQuality.MAJOR
        elif degree in minor_degrees:
            quality = ChordQuality.MINOR_7 if seventh else ChordQuality.MINOR
        elif degree in diminished_degrees:
            quality = ChordQuality.HALF_DIMINISHED_7 if seventh else ChordQuality.DIMINISHED
        else:
            quality = ChordQuality.MINOR

    else:
        # Default to major for unknown scales
        quality = ChordQuality.MAJOR_7 if seventh else ChordQuality.MAJOR

    return Chord(root, quality)
