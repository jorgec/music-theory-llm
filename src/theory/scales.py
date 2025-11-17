"""
Musical scale representations.
Provides classes for working with scales and modes.
"""

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass
from .notes import Note, SHARP_NOTES


class ScaleType(Enum):
    """Common scale types defined by their interval patterns"""
    MAJOR = [2, 2, 1, 2, 2, 2, 1]  # W-W-H-W-W-W-H
    NATURAL_MINOR = [2, 1, 2, 2, 1, 2, 2]  # W-H-W-W-H-W-W
    HARMONIC_MINOR = [2, 1, 2, 2, 1, 3, 1]  # W-H-W-W-H-WH-H
    MELODIC_MINOR = [2, 1, 2, 2, 2, 2, 1]  # W-H-W-W-W-W-H

    # Modes (can be derived from major scale)
    IONIAN = [2, 2, 1, 2, 2, 2, 1]  # Same as major
    DORIAN = [2, 1, 2, 2, 2, 1, 2]
    PHRYGIAN = [1, 2, 2, 2, 1, 2, 2]
    LYDIAN = [2, 2, 2, 1, 2, 2, 1]
    MIXOLYDIAN = [2, 2, 1, 2, 2, 1, 2]
    AEOLIAN = [2, 1, 2, 2, 1, 2, 2]  # Same as natural minor
    LOCRIAN = [1, 2, 2, 1, 2, 2, 2]

    # Pentatonic scales
    MAJOR_PENTATONIC = [2, 2, 3, 2, 3]
    MINOR_PENTATONIC = [3, 2, 2, 3, 2]

    # Blues scale
    BLUES = [3, 2, 1, 1, 3, 2]

    # Whole tone
    WHOLE_TONE = [2, 2, 2, 2, 2, 2]

    # Chromatic
    CHROMATIC = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


class Mode(Enum):
    """The seven modes of the major scale"""
    IONIAN = 0  # Major scale
    DORIAN = 1
    PHRYGIAN = 2
    LYDIAN = 3
    MIXOLYDIAN = 4
    AEOLIAN = 5  # Natural minor
    LOCRIAN = 6


@dataclass
class Scale:
    """
    Represents a musical scale.

    Attributes:
        root: The root note of the scale
        scale_type: The type/pattern of the scale
        notes: List of notes in the scale
    """
    root: Note
    scale_type: ScaleType
    notes: Optional[List[Note]] = None

    def __post_init__(self):
        if self.notes is None:
            self.notes = self._generate_notes()

    def _generate_notes(self) -> List[Note]:
        """Generate all notes in the scale based on interval pattern"""
        intervals = self.scale_type.value
        notes = [self.root]
        current_pitch = self.root.pitch_class

        for interval in intervals[:-1]:  # Last interval brings us back to root
            current_pitch = (current_pitch + interval) % 12
            note = Note(current_pitch, prefer_sharp=self.root.prefer_sharp)
            notes.append(note)

        return notes

    @classmethod
    def major(cls, root: Note) -> 'Scale':
        """Create a major scale"""
        return cls(root, ScaleType.MAJOR)

    @classmethod
    def minor(cls, root: Note, harmonic: bool = False, melodic: bool = False) -> 'Scale':
        """Create a minor scale (natural, harmonic, or melodic)"""
        if harmonic:
            return cls(root, ScaleType.HARMONIC_MINOR)
        elif melodic:
            return cls(root, ScaleType.MELODIC_MINOR)
        else:
            return cls(root, ScaleType.NATURAL_MINOR)

    @classmethod
    def from_mode(cls, root: Note, mode: Mode) -> 'Scale':
        """Create a scale from a mode"""
        mode_to_scale = {
            Mode.IONIAN: ScaleType.IONIAN,
            Mode.DORIAN: ScaleType.DORIAN,
            Mode.PHRYGIAN: ScaleType.PHRYGIAN,
            Mode.LYDIAN: ScaleType.LYDIAN,
            Mode.MIXOLYDIAN: ScaleType.MIXOLYDIAN,
            Mode.AEOLIAN: ScaleType.AEOLIAN,
            Mode.LOCRIAN: ScaleType.LOCRIAN,
        }
        return cls(root, mode_to_scale[mode])

    def degree(self, degree: int) -> Note:
        """
        Get the note at a specific scale degree (1-indexed).

        Args:
            degree: Scale degree (1 = root, 2 = second, etc.)

        Returns:
            The note at that degree
        """
        if not 1 <= degree <= len(self.notes):
            # Allow degrees beyond the octave
            degree = ((degree - 1) % len(self.notes)) + 1

        return self.notes[degree - 1]

    def contains(self, note: Note) -> bool:
        """Check if a note is in the scale"""
        return any(n.pitch_class == note.pitch_class for n in self.notes)

    def get_degree_of_note(self, note: Note) -> Optional[int]:
        """Get the scale degree (1-indexed) of a note, or None if not in scale"""
        for i, scale_note in enumerate(self.notes, 1):
            if scale_note.pitch_class == note.pitch_class:
                return i
        return None

    def relative_minor(self) -> Optional['Scale']:
        """Get the relative minor scale (only for major scales)"""
        if self.scale_type == ScaleType.MAJOR:
            # Relative minor is the 6th degree
            minor_root = self.degree(6)
            return Scale.minor(minor_root)
        return None

    def relative_major(self) -> Optional['Scale']:
        """Get the relative major scale (only for natural minor scales)"""
        if self.scale_type == ScaleType.NATURAL_MINOR:
            # Relative major is the 3rd degree
            major_root = self.degree(3)
            return Scale.major(major_root)
        return None

    def parallel_minor(self) -> Optional['Scale']:
        """Get the parallel minor scale (same root)"""
        if self.scale_type == ScaleType.MAJOR:
            return Scale.minor(self.root)
        return None

    def parallel_major(self) -> Optional['Scale']:
        """Get the parallel major scale (same root)"""
        if self.scale_type in [ScaleType.NATURAL_MINOR, ScaleType.HARMONIC_MINOR, ScaleType.MELODIC_MINOR]:
            return Scale.major(self.root)
        return None

    def to_dict(self) -> dict:
        """Convert scale to dictionary representation"""
        return {
            'root': str(self.root),
            'type': self.scale_type.name,
            'notes': [str(n) for n in self.notes]
        }

    def __str__(self) -> str:
        note_names = ' '.join(str(n) for n in self.notes)
        return f"{self.root} {self.scale_type.name.replace('_', ' ').title()}: {note_names}"

    def __repr__(self) -> str:
        return f"Scale(root={self.root}, type={self.scale_type.name})"

    def __len__(self) -> int:
        return len(self.notes)

    def __getitem__(self, index: int) -> Note:
        """Access scale notes by index (0-indexed)"""
        return self.notes[index]


# Commonly used scales for quick reference
COMMON_SCALES = {
    'C_major': Scale.major(Note.from_string('C')),
    'G_major': Scale.major(Note.from_string('G')),
    'D_major': Scale.major(Note.from_string('D')),
    'A_major': Scale.major(Note.from_string('A')),
    'E_major': Scale.major(Note.from_string('E')),
    'B_major': Scale.major(Note.from_string('B')),
    'F_major': Scale.major(Note.from_string('F')),

    'A_minor': Scale.minor(Note.from_string('A')),
    'E_minor': Scale.minor(Note.from_string('E')),
    'B_minor': Scale.minor(Note.from_string('B')),
    'D_minor': Scale.minor(Note.from_string('D')),
    'G_minor': Scale.minor(Note.from_string('G')),
    'C_minor': Scale.minor(Note.from_string('C')),
}
