"""
Melody suggestion and analysis utilities.

Provides intelligent melodic continuation suggestions based on:
- Current harmonic context (chord progression)
- Melodic contour and direction
- Voice leading principles
- Tension and resolution patterns
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import random

from ..theory import Note, Pitch, Chord, ChordProgression, Interval


class MelodicDirection(Enum):
    """Direction of melodic motion"""
    ASCENDING = "ascending"
    DESCENDING = "descending"
    STATIC = "static"
    LEAPING = "leaping"


class TensionLevel(Enum):
    """Tension level of a melodic note"""
    LOW = "low"  # Chord tones
    MEDIUM = "medium"  # Scale tones
    HIGH = "high"  # Non-scale tones, approach notes


@dataclass
class MelodicOption:
    """
    Represents a melodic continuation option.

    Attributes:
        pitches: Sequence of pitches for this option
        description: Explanation of the melodic choice
        tension_trajectory: How tension evolves
        voice_leading_quality: Quality of voice leading (1-5)
    """
    pitches: List[Pitch]
    description: str
    tension_trajectory: str
    voice_leading_quality: int


class MelodySuggester:
    """
    Suggests melodic continuations given harmonic context.
    """

    def __init__(self):
        """Initialize the melody suggester"""
        pass

    def suggest_continuations(
        self,
        partial_melody: List[Pitch],
        progression: ChordProgression,
        current_chord_idx: int,
        num_suggestions: int = 4,
        num_notes: int = 4
    ) -> List[MelodicOption]:
        """
        Suggest melodic continuations.

        Args:
            partial_melody: The existing melody (list of pitches)
            progression: The chord progression
            current_chord_idx: Index of the current chord
            num_suggestions: Number of suggestions to generate (2-4)
            num_notes: Number of notes to continue the melody

        Returns:
            List of melodic options with explanations
        """
        if not partial_melody:
            # If no melody provided, start with chord tones
            return self._suggest_starting_melody(
                progression.chords[current_chord_idx],
                num_suggestions,
                num_notes
            )

        current_chord = progression.chords[current_chord_idx]
        last_pitch = partial_melody[-1]

        # Analyze current melodic context
        melodic_direction = self._analyze_direction(partial_melody[-min(3, len(partial_melody)):])
        contour = self._analyze_contour(partial_melody)

        suggestions = []

        # Strategy 1: Stepwise continuation (maintains tension)
        stepwise = self._generate_stepwise_continuation(
            last_pitch,
            current_chord,
            progression.scale,
            melodic_direction,
            num_notes
        )
        suggestions.append(stepwise)

        # Strategy 2: Leap with resolution (creates drama)
        leap_resolve = self._generate_leap_with_resolution(
            last_pitch,
            current_chord,
            progression.scale,
            melodic_direction,
            num_notes
        )
        suggestions.append(leap_resolve)

        # Strategy 3: Approach note pattern (tension-release)
        if num_notes >= 2:
            approach = self._generate_approach_pattern(
                last_pitch,
                current_chord,
                progression.scale,
                num_notes
            )
            suggestions.append(approach)

        # Strategy 4: Arpeggiated chord tones (stable, consonant)
        if num_suggestions >= 4:
            arpeggio = self._generate_arpeggio_pattern(
                last_pitch,
                current_chord,
                num_notes
            )
            suggestions.append(arpeggio)

        return suggestions[:num_suggestions]

    def _suggest_starting_melody(
        self,
        chord: Chord,
        num_suggestions: int,
        num_notes: int
    ) -> List[MelodicOption]:
        """Suggest starting melodies"""
        suggestions = []

        # Start on different chord tones in different octaves
        octaves = [4, 5]
        chord_tones = chord.notes[:3]  # Root, 3rd, 5th

        for i, (tone, octave) in enumerate(zip(chord_tones, octaves)):
            if i >= num_suggestions:
                break

            start_pitch = Pitch(tone, octave)
            pitches = [start_pitch]

            # Continue with stepwise motion
            for j in range(num_notes - 1):
                if j % 2 == 0:
                    next_pitch = pitches[-1].transpose(2)  # Whole step up
                else:
                    next_pitch = pitches[-1].transpose(-1)  # Half step down

                pitches.append(next_pitch)

            option = MelodicOption(
                pitches=pitches,
                description=f"Starts on {tone} ({['root', 'third', 'fifth'][i]}) with balanced stepwise motion",
                tension_trajectory="Moderate tension with periodic resolution",
                voice_leading_quality=4
            )
            suggestions.append(option)

        return suggestions

    def _analyze_direction(self, recent_pitches: List[Pitch]) -> MelodicDirection:
        """Analyze the direction of recent melodic motion"""
        if len(recent_pitches) < 2:
            return MelodicDirection.STATIC

        intervals = []
        for i in range(len(recent_pitches) - 1):
            interval = recent_pitches[i + 1].midi_number - recent_pitches[i].midi_number
            intervals.append(interval)

        avg_interval = sum(intervals) / len(intervals)

        if abs(avg_interval) > 4:
            return MelodicDirection.LEAPING
        elif avg_interval > 1:
            return MelodicDirection.ASCENDING
        elif avg_interval < -1:
            return MelodicDirection.DESCENDING
        else:
            return MelodicDirection.STATIC

    def _analyze_contour(self, melody: List[Pitch]) -> str:
        """Analyze overall melodic contour"""
        if len(melody) < 3:
            return "developing"

        # Simple contour analysis
        highest = max(p.midi_number for p in melody)
        lowest = min(p.midi_number for p in melody)
        current = melody[-1].midi_number

        if current == highest:
            return "at_peak"
        elif current == lowest:
            return "at_valley"
        elif current > (highest + lowest) / 2:
            return "upper_range"
        else:
            return "lower_range"

    def _generate_stepwise_continuation(
        self,
        last_pitch: Pitch,
        current_chord: Chord,
        scale: Optional[any],
        direction: MelodicDirection,
        num_notes: int
    ) -> MelodicOption:
        """Generate stepwise melodic continuation"""
        pitches = [last_pitch]

        # Alternate between steps up and down, favoring contrary motion
        steps = [2, -1, 2, 1, -2, 2] if direction == MelodicDirection.DESCENDING else [-2, 1, -2, -1, 2, -2]

        for i in range(num_notes):
            step = steps[i % len(steps)]
            next_pitch = pitches[-1].transpose(step)
            pitches.append(next_pitch)

        return MelodicOption(
            pitches=pitches[1:],  # Don't include the starting pitch
            description="Stepwise continuation with balanced motion, maintains current tension level",
            tension_trajectory="Steady tension with smooth voice leading",
            voice_leading_quality=5
        )

    def _generate_leap_with_resolution(
        self,
        last_pitch: Pitch,
        current_chord: Chord,
        scale: Optional[any],
        direction: MelodicDirection,
        num_notes: int
    ) -> MelodicOption:
        """Generate leap followed by stepwise resolution"""
        pitches = []

        # Make a leap (5th or 6th)
        leap_size = 7 if random.random() < 0.6 else 9  # Perfect 5th or Major 6th

        # Leap in opposite direction to recent motion for contrast
        if direction == MelodicDirection.ASCENDING:
            leap_size = -leap_size

        first_pitch = last_pitch.transpose(leap_size)
        pitches.append(first_pitch)

        # Resolve stepwise in opposite direction
        step_direction = -2 if leap_size > 0 else 2

        current_pitch = first_pitch
        for i in range(num_notes - 1):
            current_pitch = current_pitch.transpose(step_direction)
            pitches.append(current_pitch)
            # Alternate step sizes
            step_direction = -step_direction + (1 if step_direction > 0 else -1)

        return MelodicOption(
            pitches=pitches,
            description="Larger leap to create drama, followed by stepwise resolution",
            tension_trajectory="High tension from leap, resolving gradually",
            voice_leading_quality=4
        )

    def _generate_approach_pattern(
        self,
        last_pitch: Pitch,
        current_chord: Chord,
        scale: Optional[any],
        num_notes: int
    ) -> MelodicOption:
        """Generate approach note pattern (chromatic or diatonic approach)"""
        pitches = []

        # Find nearest chord tone above or below
        chord_pitch_classes = [n.pitch_class for n in current_chord.notes]

        # Search for nearest chord tone
        target_found = False
        target_pitch = None

        for offset in range(1, 12):
            test_pitch = last_pitch.transpose(offset)
            if test_pitch.note.pitch_class in chord_pitch_classes:
                target_pitch = test_pitch
                target_found = True
                break

        if not target_found:
            target_pitch = last_pitch.transpose(2)  # Default to whole step

        # Approach from below chromatically
        approach_pitch = target_pitch.transpose(-1)
        pitches.append(approach_pitch)
        pitches.append(target_pitch)

        # Continue from target
        for i in range(num_notes - 2):
            next_pitch = pitches[-1].transpose(2 if i % 2 == 0 else -1)
            pitches.append(next_pitch)

        return MelodicOption(
            pitches=pitches,
            description="Chromatic approach to chord tone, creating tension-release pattern",
            tension_trajectory="Building tension through approach, resolving to chord tone",
            voice_leading_quality=4
        )

    def _generate_arpeggio_pattern(
        self,
        last_pitch: Pitch,
        current_chord: Chord,
        num_notes: int
    ) -> MelodicOption:
        """Generate arpeggiated chord tone pattern"""
        pitches = []

        # Get chord tones
        chord_tones = current_chord.notes
        base_octave = last_pitch.octave

        # Create ascending then descending arpeggio
        for i in range(num_notes):
            tone_idx = i % len(chord_tones)
            octave_adjust = i // len(chord_tones)

            pitch = Pitch(chord_tones[tone_idx], base_octave + octave_adjust)
            pitches.append(pitch)

        return MelodicOption(
            pitches=pitches,
            description="Arpeggiated chord tones, stable and consonant, emphasizes harmony",
            tension_trajectory="Low tension, strong harmonic support",
            voice_leading_quality=3
        )

    def analyze_melody_harmony_fit(
        self,
        melody: List[Pitch],
        chord: Chord
    ) -> Dict[str, any]:
        """
        Analyze how well a melody fits with a chord.

        Returns:
            Dictionary with analysis including tension points, chord tones, etc.
        """
        analysis = {
            'chord_tones': [],
            'non_chord_tones': [],
            'tension_points': [],
            'avg_tension': 0.0
        }

        chord_pitch_classes = [n.pitch_class for n in chord.notes]
        tension_sum = 0

        for i, pitch in enumerate(melody):
            if pitch.note.pitch_class in chord_pitch_classes:
                analysis['chord_tones'].append((i, pitch))
                tension_sum += 0
            else:
                analysis['non_chord_tones'].append((i, pitch))
                analysis['tension_points'].append(i)
                tension_sum += 1

        analysis['avg_tension'] = tension_sum / len(melody) if melody else 0
        return analysis
