"""
Chord progression and harmonic function analysis.
Provides classes for working with chord progressions and analyzing harmonic relationships.
"""

from enum import Enum
from typing import List, Optional, Tuple
from dataclasses import dataclass
from .chords import Chord, chord_from_scale_degree
from .scales import Scale


class HarmonicFunction(Enum):
    """
    The three main harmonic functions in tonal music.
    """
    TONIC = "tonic"  # Stability, resolution (I, vi, iii in major)
    SUBDOMINANT = "subdominant"  # Pre-dominant, preparation (IV, ii in major)
    DOMINANT = "dominant"  # Tension, leading to tonic (V, vii° in major)


# Map scale degrees to harmonic functions (in major key)
MAJOR_KEY_FUNCTIONS = {
    1: HarmonicFunction.TONIC,
    2: HarmonicFunction.SUBDOMINANT,
    3: HarmonicFunction.TONIC,
    4: HarmonicFunction.SUBDOMINANT,
    5: HarmonicFunction.DOMINANT,
    6: HarmonicFunction.TONIC,
    7: HarmonicFunction.DOMINANT,
}


@dataclass
class ChordProgression:
    """
    Represents a chord progression in a specific key.

    Attributes:
        chords: List of chords in the progression
        scale: The scale/key of the progression
        roman_numerals: Optional roman numeral analysis
        style: Optional style/genre classification
    """
    chords: List[Chord]
    scale: Optional[Scale] = None
    roman_numerals: Optional[List[str]] = None
    style: Optional[str] = None

    def __post_init__(self):
        if self.scale and not self.roman_numerals:
            self.roman_numerals = self._analyze_roman_numerals()

    def _analyze_roman_numerals(self) -> List[str]:
        """
        Analyze the progression and generate Roman numeral notation.

        Returns:
            List of Roman numerals for each chord
        """
        if not self.scale:
            return []

        numerals = []
        for chord in self.chords:
            degree = self.scale.get_degree_of_note(chord.root)
            if degree is None:
                numerals.append("?")
                continue

            # Determine if chord is major, minor, diminished
            if chord.is_major():
                numeral = ["I", "II", "III", "IV", "V", "VI", "VII"][degree - 1]
            elif chord.is_minor():
                numeral = ["i", "ii", "iii", "iv", "v", "vi", "vii"][degree - 1]
            elif chord.is_diminished():
                numeral = ["i°", "ii°", "iii°", "iv°", "v°", "vi°", "vii°"][degree - 1]
            else:
                numeral = ["I", "II", "III", "IV", "V", "VI", "VII"][degree - 1]

            # Add 7 for seventh chords
            if len(chord.notes) >= 4:
                numeral += "7"

            numerals.append(numeral)

        return numerals

    @classmethod
    def from_roman_numerals(cls, numerals: List[str], scale: Scale) -> 'ChordProgression':
        """
        Create a chord progression from Roman numeral notation.

        Args:
            numerals: List of Roman numerals (e.g., ['I', 'V', 'vi', 'IV'])
            scale: The scale/key to use

        Returns:
            ChordProgression object
        """
        numeral_to_degree = {
            'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
            'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7,
        }

        chords = []
        for numeral in numerals:
            # Check if it's a seventh chord
            is_seventh = '7' in numeral
            clean_numeral = numeral.replace('7', '').replace('°', '')

            degree = numeral_to_degree.get(clean_numeral)
            if degree is None:
                raise ValueError(f"Invalid Roman numeral: {numeral}")

            chord = chord_from_scale_degree(scale, degree, seventh=is_seventh)
            chords.append(chord)

        return cls(chords, scale, numerals)

    @classmethod
    def from_degrees(cls, degrees: List[int], scale: Scale, sevenths: bool = False) -> 'ChordProgression':
        """
        Create a progression from scale degrees.

        Args:
            degrees: List of scale degrees (e.g., [1, 5, 6, 4])
            scale: The scale to use
            sevenths: Whether to use seventh chords

        Returns:
            ChordProgression object
        """
        chords = [chord_from_scale_degree(scale, d, seventh=sevenths) for d in degrees]
        return cls(chords, scale)

    def get_harmonic_functions(self) -> List[Optional[HarmonicFunction]]:
        """
        Analyze the harmonic function of each chord in the progression.

        Returns:
            List of HarmonicFunction values
        """
        if not self.scale:
            return [None] * len(self.chords)

        functions = []
        for chord in self.chords:
            degree = self.scale.get_degree_of_note(chord.root)
            if degree is None:
                functions.append(None)
            else:
                functions.append(MAJOR_KEY_FUNCTIONS.get(degree))

        return functions

    def transpose(self, semitones: int) -> 'ChordProgression':
        """
        Transpose the entire progression by a number of semitones.

        Args:
            semitones: Number of semitones to transpose

        Returns:
            New transposed progression
        """
        new_chords = []
        for chord in self.chords:
            new_root = chord.root.transpose(semitones)
            new_chord = Chord(new_root, chord.quality)
            new_chords.append(new_chord)

        new_scale = None
        if self.scale:
            new_scale_root = self.scale.root.transpose(semitones)
            new_scale = Scale(new_scale_root, self.scale.scale_type)

        return ChordProgression(new_chords, new_scale, self.roman_numerals)

    def to_key(self, new_scale: Scale) -> 'ChordProgression':
        """
        Transpose the progression to a new key while maintaining the same degree relationships.

        Args:
            new_scale: Target scale/key

        Returns:
            Progression in the new key
        """
        if not self.scale:
            raise ValueError("Cannot transpose progression without a defined scale")

        # Calculate semitone difference
        semitones = new_scale.root.pitch_class - self.scale.root.pitch_class
        return self.transpose(semitones)

    def get_cadence_type(self) -> Optional[str]:
        """
        Identify the type of cadence at the end of the progression.

        Returns:
            String describing the cadence type, or None
        """
        if len(self.chords) < 2:
            return None

        functions = self.get_harmonic_functions()
        if len(functions) < 2:
            return None

        penultimate = functions[-2]
        final = functions[-1]

        if penultimate == HarmonicFunction.DOMINANT and final == HarmonicFunction.TONIC:
            return "authentic cadence"
        elif penultimate == HarmonicFunction.SUBDOMINANT and final == HarmonicFunction.TONIC:
            return "plagal cadence"
        elif final == HarmonicFunction.DOMINANT:
            return "half cadence"
        elif penultimate == HarmonicFunction.DOMINANT and final != HarmonicFunction.TONIC:
            return "deceptive cadence"

        return None

    def to_dict(self) -> dict:
        """Convert progression to dictionary representation"""
        return {
            'chords': [chord.to_dict() for chord in self.chords],
            'scale': self.scale.to_dict() if self.scale else None,
            'roman_numerals': self.roman_numerals,
            'harmonic_functions': [f.value if f else None for f in self.get_harmonic_functions()],
            'cadence': self.get_cadence_type()
        }

    def __str__(self) -> str:
        chord_strs = [str(c) for c in self.chords]
        result = ' - '.join(chord_strs)

        if self.roman_numerals:
            roman_str = ' - '.join(self.roman_numerals)
            result += f"\n({roman_str})"

        if self.scale:
            result = f"Key of {self.scale.root}:\n{result}"

        return result

    def __repr__(self) -> str:
        return f"ChordProgression({[str(c) for c in self.chords]})"

    def __len__(self) -> int:
        return len(self.chords)

    def __getitem__(self, index: int) -> Chord:
        return self.chords[index]


# Common chord progressions
COMMON_PROGRESSIONS = {
    'I-V-vi-IV': [1, 5, 6, 4],  # Very popular in pop music
    'I-IV-V': [1, 4, 5],  # Basic three-chord progression
    'ii-V-I': [2, 5, 1],  # Jazz turnaround
    'I-vi-IV-V': [1, 6, 4, 5],  # 50s progression
    'vi-IV-I-V': [6, 4, 1, 5],  # Alternative pop progression
    'I-V-vi-iii-IV-I-IV-V': [1, 5, 6, 3, 4, 1, 4, 5],  # Pachelbel's Canon
    'I-IV-I-V': [1, 4, 1, 5],  # Simple folk progression
    'i-VI-III-VII': [1, 6, 3, 7],  # Minor key progression (needs minor scale)
}


def get_common_progression(name: str, scale: Scale) -> ChordProgression:
    """
    Get a common chord progression by name in a specific key.

    Args:
        name: Name of the progression (e.g., 'I-V-vi-IV')
        scale: The scale/key to use

    Returns:
        ChordProgression object
    """
    if name not in COMMON_PROGRESSIONS:
        raise ValueError(f"Unknown progression: {name}")

    degrees = COMMON_PROGRESSIONS[name]
    return ChordProgression.from_degrees(degrees, scale)
