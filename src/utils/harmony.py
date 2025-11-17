"""
Advanced harmonic analysis and suggestion utilities.

Provides:
- Passing chord suggestions
- Secondary dominant analysis
- Tritone substitutions
- Modal interchange (borrowed chords)
- Chord extensions (9th, 11th, 13th)
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from ..theory import Note, Chord, ChordProgression, Scale, chord_from_scale_degree
from ..theory.chords import ChordQuality


@dataclass
class HarmonicSuggestion:
    """
    Represents a harmonic suggestion.

    Attributes:
        chord: The suggested chord
        position: Where to insert (between which chords)
        suggestion_type: Type of suggestion (passing, secondary dominant, etc.)
        description: Explanation of the harmonic function
        voice_leading_quality: Quality score (1-5)
    """
    chord: Chord
    position: Tuple[int, int]  # (after_index, before_index)
    suggestion_type: str
    description: str
    voice_leading_quality: int


class HarmonicAnalyzer:
    """
    Analyzes and suggests advanced harmonic concepts.
    """

    def __init__(self):
        """Initialize the harmonic analyzer"""
        pass

    def analyze_progression(
        self,
        progression: ChordProgression
    ) -> Dict[str, any]:
        """
        Comprehensive analysis of a chord progression.

        Returns:
            Dictionary with various analyses
        """
        analysis = {
            'key': str(progression.scale.root) if progression.scale else 'Unknown',
            'scale_type': progression.scale.scale_type.name if progression.scale else 'Unknown',
            'num_chords': len(progression.chords),
            'cadence_type': progression.get_cadence_type(),
            'roman_numerals': progression.roman_numerals,
            'harmonic_functions': [f.value if f else None for f in progression.get_harmonic_functions()],
            'suggestions': {
                'passing_chords': [],
                'secondary_dominants': [],
                'tritone_subs': [],
                'modal_interchange': [],
                'extensions': []
            }
        }

        # Generate all types of suggestions
        analysis['suggestions']['passing_chords'] = self.suggest_passing_chords(progression)
        analysis['suggestions']['secondary_dominants'] = self.suggest_secondary_dominants(progression)
        analysis['suggestions']['tritone_subs'] = self.suggest_tritone_substitutions(progression)
        analysis['suggestions']['modal_interchange'] = self.suggest_modal_interchange(progression)
        analysis['suggestions']['extensions'] = self.suggest_chord_extensions(progression)

        return analysis

    def suggest_passing_chords(
        self,
        progression: ChordProgression
    ) -> List[HarmonicSuggestion]:
        """
        Suggest passing chords between existing chords.

        Passing chords create smooth voice leading by filling in gaps.
        """
        suggestions = []

        for i in range(len(progression.chords) - 1):
            current_chord = progression.chords[i]
            next_chord = progression.chords[i + 1]

            # Calculate root movement
            root_interval = (next_chord.root.pitch_class - current_chord.root.pitch_class) % 12

            # Suggest passing chords for larger intervals
            if root_interval >= 3:
                # Chromatic passing chord
                passing_root = current_chord.root.transpose(root_interval // 2)

                # Use diminished 7th for chromatic passing
                passing_chord = Chord(passing_root, ChordQuality.DIMINISHED_7)

                suggestion = HarmonicSuggestion(
                    chord=passing_chord,
                    position=(i, i + 1),
                    suggestion_type='passing_chord',
                    description=f"Diminished passing chord between {current_chord} and {next_chord}, "
                                f"creates smooth chromatic voice leading",
                    voice_leading_quality=4
                )
                suggestions.append(suggestion)

            # Diatonic passing chord
            if progression.scale and root_interval > 2:
                # Find diatonic chord between current and next
                current_degree = progression.scale.get_degree_of_note(current_chord.root)
                next_degree = progression.scale.get_degree_of_note(next_chord.root)

                if current_degree and next_degree and abs(next_degree - current_degree) > 1:
                    middle_degree = (current_degree + next_degree) // 2
                    if 1 <= middle_degree <= 7:
                        passing_chord = chord_from_scale_degree(progression.scale, middle_degree, seventh=True)

                        suggestion = HarmonicSuggestion(
                            chord=passing_chord,
                            position=(i, i + 1),
                            suggestion_type='passing_chord',
                            description=f"Diatonic passing chord (scale degree {middle_degree}) "
                                        f"between {current_chord} and {next_chord}",
                            voice_leading_quality=4
                        )
                        suggestions.append(suggestion)

        return suggestions

    def suggest_secondary_dominants(
        self,
        progression: ChordProgression
    ) -> List[HarmonicSuggestion]:
        """
        Suggest secondary dominants (V/x chords).

        Secondary dominants temporarily tonicize a target chord.
        """
        suggestions = []

        if not progression.scale:
            return suggestions

        for i, chord in enumerate(progression.chords):
            # Find the V7 chord that would resolve to this chord
            # Secondary dominant is a 7th chord built a perfect 5th above target
            dominant_root = chord.root.transpose(-7)  # Down a 5th = up a 4th

            # Build dominant 7th chord
            secondary_dominant = Chord(dominant_root, ChordQuality.DOMINANT_7)

            # Check if this is NOT the actual V chord in the key
            if dominant_root.pitch_class != progression.scale.degree(5).pitch_class:
                position = (i - 1, i) if i > 0 else (i, i + 1)

                # Get the scale degree being tonicized
                target_degree = progression.scale.get_degree_of_note(chord.root)
                if target_degree:
                    suggestion = HarmonicSuggestion(
                        chord=secondary_dominant,
                        position=position,
                        suggestion_type='secondary_dominant',
                        description=f"{secondary_dominant} functions as V7/{target_degree} "
                                    f"(secondary dominant of {chord}), creates temporary tonicization",
                        voice_leading_quality=5
                    )
                    suggestions.append(suggestion)

        return suggestions

    def suggest_tritone_substitutions(
        self,
        progression: ChordProgression
    ) -> List[HarmonicSuggestion]:
        """
        Suggest tritone substitutions for dominant chords.

        A tritone sub replaces a V7 chord with a dominant 7th chord
        a tritone (6 semitones) away.
        """
        suggestions = []

        for i, chord in enumerate(progression.chords):
            # Check if this is a dominant 7th chord
            if chord.quality == ChordQuality.DOMINANT_7:
                # Tritone sub root is a tritone away
                tritone_root = chord.root.transpose(6)
                tritone_sub = Chord(tritone_root, ChordQuality.DOMINANT_7)

                suggestion = HarmonicSuggestion(
                    chord=tritone_sub,
                    position=(i, i),  # Replaces the chord at position i
                    suggestion_type='tritone_substitution',
                    description=f"Replace {chord} with {tritone_sub} (tritone substitution), "
                                f"shares the same tritone interval, creates chromatic bass motion",
                    voice_leading_quality=4
                )
                suggestions.append(suggestion)

        return suggestions

    def suggest_modal_interchange(
        self,
        progression: ChordProgression
    ) -> List[HarmonicSuggestion]:
        """
        Suggest borrowed chords from parallel minor/major.

        Modal interchange adds color by borrowing chords from the parallel mode.
        """
        suggestions = []

        if not progression.scale:
            return suggestions

        # Common borrowed chords in major keys from parallel minor
        if progression.scale.scale_type.name == 'MAJOR':
            borrowed_chords_info = [
                (4, ChordQuality.MINOR, "iv", "borrowed from parallel minor, common in rock/pop"),
                (6, ChordQuality.MAJOR, "bVI", "borrowed from parallel minor, adds dark color"),
                (7, ChordQuality.MAJOR, "bVII", "borrowed from mixolydian/minor, very common in rock"),
                (2, ChordQuality.DIMINISHED_7, "ii°7", "borrowed from harmonic minor, strong pull to I"),
            ]

            for degree, quality, symbol, description in borrowed_chords_info:
                # Adjust root for flat chords
                if 'b' in symbol:
                    root = progression.scale.root.transpose((degree - 1) * 2 - 1)
                else:
                    root = progression.scale.degree(degree)

                borrowed_chord = Chord(root, quality)

                # Suggest inserting at various positions
                for i in range(len(progression.chords)):
                    suggestion = HarmonicSuggestion(
                        chord=borrowed_chord,
                        position=(i, i + 1) if i < len(progression.chords) - 1 else (i - 1, i),
                        suggestion_type='modal_interchange',
                        description=f"{borrowed_chord} ({symbol}): {description}",
                        voice_leading_quality=4
                    )
                    suggestions.append(suggestion)

        # Borrowed chords in minor keys from parallel major
        elif 'MINOR' in progression.scale.scale_type.name:
            borrowed_chords_info = [
                (4, ChordQuality.MAJOR, "IV", "borrowed from parallel major, brightens the sound"),
                (1, ChordQuality.MAJOR, "I", "borrowed from parallel major (Picardy third)"),
                (7, ChordQuality.DIMINISHED, "vii°", "borrowed from major, leading tone function"),
            ]

            for degree, quality, symbol, description in borrowed_chords_info:
                root = progression.scale.degree(degree)
                borrowed_chord = Chord(root, quality)

                for i in range(len(progression.chords)):
                    suggestion = HarmonicSuggestion(
                        chord=borrowed_chord,
                        position=(i, i + 1) if i < len(progression.chords) - 1 else (i - 1, i),
                        suggestion_type='modal_interchange',
                        description=f"{borrowed_chord} ({symbol}): {description}",
                        voice_leading_quality=3
                    )
                    suggestions.append(suggestion)

        return suggestions

    def suggest_chord_extensions(
        self,
        progression: ChordProgression
    ) -> List[Dict[str, any]]:
        """
        Suggest chord extensions (9th, 11th, 13th) for each chord.

        Extensions add color and sophistication to basic chords.
        """
        suggestions = []

        for i, chord in enumerate(progression.chords):
            chord_suggestions = {
                'original_chord': str(chord),
                'position': i,
                'extensions': []
            }

            # Major chords can have various extensions
            if chord.is_major():
                chord_suggestions['extensions'].append({
                    'extension': 'add9',
                    'description': f"Add major 9th ({chord.root.transpose(14)}) for open, airy sound",
                    'intervals': [0, 4, 7, 14]
                })

                chord_suggestions['extensions'].append({
                    'extension': 'maj7',
                    'description': f"Add major 7th for sophisticated, jazzy color",
                    'intervals': [0, 4, 7, 11]
                })

                chord_suggestions['extensions'].append({
                    'extension': 'maj9',
                    'description': f"Add major 7th and 9th for rich, lush sound",
                    'intervals': [0, 4, 7, 11, 14]
                })

                chord_suggestions['extensions'].append({
                    'extension': '6/9',
                    'description': f"Add 6th and 9th for bright, sweet sound (common in jazz)",
                    'intervals': [0, 4, 7, 9, 14]
                })

            # Minor chords
            elif chord.is_minor():
                chord_suggestions['extensions'].append({
                    'extension': 'add9',
                    'description': f"Add major 9th for dreamy quality",
                    'intervals': [0, 3, 7, 14]
                })

                chord_suggestions['extensions'].append({
                    'extension': 'm7',
                    'description': f"Add minor 7th for smooth, jazzy sound",
                    'intervals': [0, 3, 7, 10]
                })

                chord_suggestions['extensions'].append({
                    'extension': 'm9',
                    'description': f"Add minor 7th and major 9th for sophisticated color",
                    'intervals': [0, 3, 7, 10, 14]
                })

                chord_suggestions['extensions'].append({
                    'extension': 'm11',
                    'description': f"Add 9th and 11th for very lush, complex sound",
                    'intervals': [0, 3, 7, 10, 14, 17]
                })

            # Dominant chords
            elif chord.quality == ChordQuality.DOMINANT_7:
                chord_suggestions['extensions'].append({
                    'extension': '9',
                    'description': f"Add major 9th for richer dominant sound",
                    'intervals': [0, 4, 7, 10, 14]
                })

                chord_suggestions['extensions'].append({
                    'extension': '7#9',
                    'description': f"Add sharp 9 for 'Hendrix chord' sound, bluesy and tense",
                    'intervals': [0, 4, 7, 10, 15]
                })

                chord_suggestions['extensions'].append({
                    'extension': '13',
                    'description': f"Add 13th (major 6th) for sophisticated dominant color",
                    'intervals': [0, 4, 7, 10, 21]
                })

                chord_suggestions['extensions'].append({
                    'extension': '7b9',
                    'description': f"Add flat 9 for altered, tense dominant sound",
                    'intervals': [0, 4, 7, 10, 13]
                })

            if chord_suggestions['extensions']:
                suggestions.append(chord_suggestions)

        return suggestions

    def analyze_voice_leading(
        self,
        chord1: Chord,
        chord2: Chord
    ) -> Dict[str, any]:
        """
        Analyze voice leading between two chords.

        Returns:
            Dictionary with voice leading analysis
        """
        analysis = {
            'total_motion': 0,
            'smooth': True,
            'common_tones': [],
            'voice_movements': []
        }

        # Find common tones
        chord1_pcs = set(n.pitch_class for n in chord1.notes)
        chord2_pcs = set(n.pitch_class for n in chord2.notes)
        common_pcs = chord1_pcs & chord2_pcs

        analysis['common_tones'] = [Note(pc) for pc in common_pcs]

        # Calculate voice movements (simplified - assumes closest voicing)
        for note1 in chord1.notes:
            # Find closest note in chord2
            min_distance = 12
            closest_note = None

            for note2 in chord2.notes:
                distance = abs(note2.pitch_class - note1.pitch_class)
                if distance > 6:
                    distance = 12 - distance

                if distance < min_distance:
                    min_distance = distance
                    closest_note = note2

            if closest_note:
                analysis['voice_movements'].append({
                    'from': str(note1),
                    'to': str(closest_note),
                    'distance': min_distance
                })
                analysis['total_motion'] += min_distance

        # Voice leading is smooth if average motion is < 2 semitones
        avg_motion = analysis['total_motion'] / len(chord1.notes) if chord1.notes else 0
        analysis['smooth'] = avg_motion <= 2.5
        analysis['avg_motion'] = avg_motion

        return analysis
