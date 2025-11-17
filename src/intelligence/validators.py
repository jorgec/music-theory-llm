"""
Music Theory Rule Validators

Validates musical constructs against established music theory rules and best practices.
Provides scoring and detailed feedback on rule violations.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.theory import Note, Pitch, Chord, ChordProgression, Scale, Interval


class RuleSeverity(Enum):
    """Severity level of rule violations"""
    INFO = "info"  # Stylistic suggestion
    WARNING = "warning"  # Not ideal but acceptable
    ERROR = "error"  # Clear rule violation


@dataclass
class RuleViolation:
    """Represents a music theory rule violation"""
    rule_name: str
    severity: RuleSeverity
    description: str
    location: str  # Where the violation occurs
    suggestion: Optional[str] = None
    score_penalty: float = 0.0  # How much this affects the score


@dataclass
class ValidationResult:
    """Result of validating a musical construct"""
    is_valid: bool
    score: float  # 0-100
    violations: List[RuleViolation] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    overall_feedback: str = ""

    def add_violation(self, violation: RuleViolation):
        """Add a violation and update validity"""
        self.violations.append(violation)
        if violation.severity == RuleSeverity.ERROR:
            self.is_valid = False
        self.score = max(0, self.score - violation.score_penalty)

    def add_strength(self, strength: str, bonus: float = 0):
        """Add a strength and bonus points"""
        self.strengths.append(strength)
        self.score = min(100, self.score + bonus)


class MusicTheoryValidator:
    """
    Validates music theory constructs against established rules.

    Checks for:
    - Voice leading rules (parallel 5ths/octaves, voice crossing)
    - Melodic rules (large leaps, range, contour)
    - Harmonic rules (chord progressions, cadences)
    - Counterpoint rules (species counterpoint)
    """

    def __init__(self, strictness: str = "moderate"):
        """
        Initialize validator.

        Args:
            strictness: "strict", "moderate", or "lenient"
        """
        self.strictness = strictness

        # Strictness affects penalty weights
        self.penalty_multiplier = {
            "strict": 1.5,
            "moderate": 1.0,
            "lenient": 0.5
        }[strictness]

    def validate_melody(
        self,
        melody: List[Pitch],
        scale: Optional[Scale] = None
    ) -> ValidationResult:
        """
        Validate a melody against melodic rules.

        Checks:
        - Melodic intervals (avoid augmented intervals, large leaps)
        - Range (reasonable vocal/instrumental range)
        - Contour (balanced motion, climax placement)
        - Scale conformity (if scale provided)
        """
        result = ValidationResult(is_valid=True, score=100.0)

        if len(melody) < 2:
            return result

        # Check melodic intervals
        for i in range(len(melody) - 1):
            interval_semitones = melody[i + 1].midi_number - melody[i].midi_number

            # Check for very large leaps (>octave)
            if abs(interval_semitones) > 12:
                result.add_violation(RuleViolation(
                    rule_name="melodic_leap_limit",
                    severity=RuleSeverity.ERROR if self.strictness == "strict" else RuleSeverity.WARNING,
                    description=f"Very large leap of {abs(interval_semitones)} semitones between {melody[i]} and {melody[i+1]}",
                    location=f"notes {i}-{i+1}",
                    suggestion="Consider breaking large leaps into smaller steps or use contrary motion after leap",
                    score_penalty=15.0 * self.penalty_multiplier
                ))

            # Check for augmented intervals (tritone leap = 6 semitones)
            elif abs(interval_semitones) == 6:
                result.add_violation(RuleViolation(
                    rule_name="tritone_leap",
                    severity=RuleSeverity.WARNING,
                    description=f"Tritone leap between {melody[i]} and {melody[i+1]}",
                    location=f"notes {i}-{i+1}",
                    suggestion="Tritone leaps can sound unstable; consider resolving by step in opposite direction",
                    score_penalty=8.0 * self.penalty_multiplier
                ))

            # Check for large leaps (>6 semitones) - should resolve by step in opposite direction
            elif abs(interval_semitones) > 6:
                if i < len(melody) - 2:
                    next_interval = melody[i + 2].midi_number - melody[i + 1].midi_number
                    # Check if resolves by step in opposite direction
                    if interval_semitones * next_interval > 0 or abs(next_interval) > 2:
                        result.add_violation(RuleViolation(
                            rule_name="leap_resolution",
                            severity=RuleSeverity.WARNING,
                            description=f"Large leap at note {i} not resolved by contrary stepwise motion",
                            location=f"notes {i}-{i+2}",
                            suggestion="After large leaps, resolve by step in the opposite direction",
                            score_penalty=5.0 * self.penalty_multiplier
                        ))

        # Check melodic range
        midi_numbers = [p.midi_number for p in melody]
        range_semitones = max(midi_numbers) - min(midi_numbers)

        if range_semitones > 24:  # More than 2 octaves
            result.add_violation(RuleViolation(
                rule_name="melodic_range",
                severity=RuleSeverity.WARNING,
                description=f"Wide melodic range of {range_semitones} semitones (2+ octaves)",
                location="overall",
                suggestion="Consider narrowing the range for better singability/playability",
                score_penalty=5.0 * self.penalty_multiplier
            ))
        elif range_semitones >= 12 and range_semitones <= 19:
            result.add_strength("Good melodic range (1-1.5 octaves)", bonus=5.0)

        # Check scale conformity
        if scale:
            non_scale_notes = []
            for i, pitch in enumerate(melody):
                if not scale.contains(pitch.note):
                    non_scale_notes.append((i, pitch))

            if non_scale_notes:
                if len(non_scale_notes) / len(melody) > 0.3:  # >30% non-scale notes
                    result.add_violation(RuleViolation(
                        rule_name="scale_conformity",
                        severity=RuleSeverity.WARNING,
                        description=f"{len(non_scale_notes)} notes outside of {scale.root} {scale.scale_type.name}",
                        location=f"notes: {[n[0] for n in non_scale_notes[:3]]}...",
                        suggestion="Consider using chromatic approaches or staying within the scale",
                        score_penalty=10.0 * self.penalty_multiplier
                    ))
                else:
                    result.add_strength(f"Good use of chromatic color ({len(non_scale_notes)} chromatic notes)", bonus=3.0)

        # Check for monotony (too many repeated notes)
        repeated_count = sum(1 for i in range(len(melody) - 1) if melody[i] == melody[i + 1])
        if repeated_count > len(melody) * 0.4:
            result.add_violation(RuleViolation(
                rule_name="melodic_interest",
                severity=RuleSeverity.INFO,
                description="Many repeated notes; melody may lack motion",
                location="overall",
                suggestion="Add more stepwise motion and varied rhythm",
                score_penalty=5.0 * self.penalty_multiplier
            ))

        # Check contour - should have clear shape
        if len(melody) >= 5:
            directions = []
            for i in range(len(melody) - 1):
                if melody[i + 1].midi_number > melody[i].midi_number:
                    directions.append(1)
                elif melody[i + 1].midi_number < melody[i].midi_number:
                    directions.append(-1)
                else:
                    directions.append(0)

            # Good contour has a mix of directions (not all ascending or descending)
            if all(d >= 0 for d in directions) or all(d <= 0 for d in directions):
                result.add_violation(RuleViolation(
                    rule_name="melodic_contour",
                    severity=RuleSeverity.INFO,
                    description="Melody moves continuously in one direction",
                    location="overall",
                    suggestion="Add contrary motion for more interesting contour",
                    score_penalty=3.0 * self.penalty_multiplier
                ))
            else:
                result.add_strength("Well-balanced melodic contour", bonus=5.0)

        result.overall_feedback = self._generate_melody_feedback(result)
        return result

    def validate_chord_progression(
        self,
        progression: ChordProgression
    ) -> ValidationResult:
        """
        Validate a chord progression.

        Checks:
        - Voice leading between chords
        - Harmonic function logic
        - Cadence appropriateness
        - Common progression patterns
        """
        result = ValidationResult(is_valid=True, score=100.0)

        if len(progression.chords) < 2:
            return result

        # Check voice leading between adjacent chords
        for i in range(len(progression.chords) - 1):
            chord1 = progression.chords[i]
            chord2 = progression.chords[i + 1]

            # Check for parallel fifths and octaves
            violation = self._check_parallel_motion(chord1, chord2)
            if violation:
                violation.location = f"chords {i+1}-{i+2} ({chord1} to {chord2})"
                result.add_violation(violation)

            # Check voice leading smoothness
            total_motion = self._calculate_voice_leading_motion(chord1, chord2)
            if total_motion > 15:  # Rough guideline
                result.add_violation(RuleViolation(
                    rule_name="voice_leading_smoothness",
                    severity=RuleSeverity.WARNING,
                    description=f"Large voice leading motion ({total_motion} semitones total)",
                    location=f"chords {i+1}-{i+2}",
                    suggestion="Try to keep common tones and move other voices by step",
                    score_penalty=5.0 * self.penalty_multiplier
                ))

        # Check harmonic function logic
        if progression.scale:
            functions = progression.get_harmonic_functions()
            for i in range(len(functions) - 1):
                if functions[i] and functions[i+1]:
                    # Check for logical function progression
                    if not self._is_logical_function_progression(functions[i], functions[i+1]):
                        result.add_violation(RuleViolation(
                            rule_name="harmonic_function_logic",
                            severity=RuleSeverity.INFO,
                            description=f"Unusual function progression: {functions[i].value} → {functions[i+1].value}",
                            location=f"chords {i+1}-{i+2}",
                            suggestion="Consider standard progressions like T-S-D-T or T-D-T",
                            score_penalty=3.0 * self.penalty_multiplier
                        ))

        # Check cadence
        cadence = progression.get_cadence_type()
        if cadence and "authentic" in cadence:
            result.add_strength("Strong authentic cadence provides clear resolution", bonus=8.0)
        elif cadence and "half" in cadence:
            result.add_strength("Half cadence creates effective pause", bonus=5.0)

        # Check for monotony (too many repeated chords)
        unique_chords = len(set(str(c) for c in progression.chords))
        if unique_chords < len(progression.chords) * 0.5:
            result.add_violation(RuleViolation(
                rule_name="harmonic_variety",
                severity=RuleSeverity.INFO,
                description="Limited harmonic variety (many repeated chords)",
                location="overall",
                suggestion="Add more chord variety or use passing chords",
                score_penalty=5.0 * self.penalty_multiplier
            ))

        result.overall_feedback = self._generate_progression_feedback(result, progression)
        return result

    def validate_voice_leading(
        self,
        chord1: Chord,
        chord2: Chord
    ) -> ValidationResult:
        """
        Validate voice leading between two chords.

        Checks:
        - Parallel 5ths and octaves
        - Voice crossing
        - Large leaps in individual voices
        """
        result = ValidationResult(is_valid=True, score=100.0)

        # Check for parallel fifths and octaves
        violation = self._check_parallel_motion(chord1, chord2)
        if violation:
            result.add_violation(violation)

        # Check total voice motion
        total_motion = self._calculate_voice_leading_motion(chord1, chord2)

        if total_motion <= 5:
            result.add_strength("Excellent voice leading - minimal motion", bonus=10.0)
        elif total_motion <= 10:
            result.add_strength("Good voice leading - smooth motion", bonus=5.0)
        elif total_motion > 20:
            result.add_violation(RuleViolation(
                rule_name="excessive_motion",
                severity=RuleSeverity.WARNING,
                description=f"Excessive total voice motion ({total_motion} semitones)",
                location="between chords",
                suggestion="Keep common tones and move voices by the smallest intervals",
                score_penalty=10.0 * self.penalty_multiplier
            ))

        # Check for common tones
        common_pcs = set(n.pitch_class for n in chord1.notes) & set(n.pitch_class for n in chord2.notes)
        if common_pcs:
            result.add_strength(f"{len(common_pcs)} common tone(s) maintained", bonus=5.0)

        result.overall_feedback = f"Voice leading score: {result.score:.1f}/100"
        return result

    def _check_parallel_motion(self, chord1: Chord, chord2: Chord) -> Optional[RuleViolation]:
        """Check for parallel fifths and octaves (simplified check)"""
        # This is a simplified check; full implementation would need voice assignments

        # For now, check if root motion is by fifth/octave and chords are same quality
        root_interval = (chord2.root.pitch_class - chord1.root.pitch_class) % 12

        if root_interval in [0, 7] and chord1.quality == chord2.quality:
            if self.strictness == "strict":
                return RuleViolation(
                    rule_name="parallel_motion",
                    severity=RuleSeverity.WARNING,
                    description="Potential parallel motion detected",
                    location="between chords",
                    suggestion="Avoid parallel perfect intervals in strict counterpoint",
                    score_penalty=8.0 * self.penalty_multiplier
                )

        return None

    def _calculate_voice_leading_motion(self, chord1: Chord, chord2: Chord) -> int:
        """Calculate total semitone motion in voice leading (simplified)"""
        # Find closest voice leading between chords
        total_motion = 0

        for note1 in chord1.notes:
            # Find closest note in chord2
            min_distance = min(
                abs(note2.pitch_class - note1.pitch_class)
                if abs(note2.pitch_class - note1.pitch_class) <= 6
                else 12 - abs(note2.pitch_class - note1.pitch_class)
                for note2 in chord2.notes
            )
            total_motion += min_distance

        return total_motion

    def _is_logical_function_progression(self, func1, func2) -> bool:
        """Check if harmonic function progression is logical"""
        from src.theory.progressions import HarmonicFunction

        # Common progressions
        logical_progressions = [
            (HarmonicFunction.TONIC, HarmonicFunction.SUBDOMINANT),
            (HarmonicFunction.TONIC, HarmonicFunction.DOMINANT),
            (HarmonicFunction.SUBDOMINANT, HarmonicFunction.DOMINANT),
            (HarmonicFunction.DOMINANT, HarmonicFunction.TONIC),
            (HarmonicFunction.TONIC, HarmonicFunction.TONIC),  # Tonic prolongation
        ]

        return (func1, func2) in logical_progressions

    def _generate_melody_feedback(self, result: ValidationResult) -> str:
        """Generate overall feedback for melody validation"""
        if result.score >= 90:
            return "Excellent melody with strong adherence to melodic principles!"
        elif result.score >= 75:
            return "Good melody with minor issues. Consider the suggestions for improvement."
        elif result.score >= 60:
            return "Acceptable melody but has several issues to address."
        else:
            return "Melody needs significant revision to improve melodic quality."

    def _generate_progression_feedback(self, result: ValidationResult, progression: ChordProgression) -> str:
        """Generate overall feedback for progression validation"""
        feedback = []

        if result.score >= 90:
            feedback.append("Excellent chord progression!")
        elif result.score >= 75:
            feedback.append("Good progression with room for refinement.")
        else:
            feedback.append("Progression could be improved.")

        if progression.get_cadence_type():
            feedback.append(f"Cadence: {progression.get_cadence_type()}.")

        return " ".join(feedback)


class ProgressionPatternValidator:
    """
    Validates chord progressions against common patterns and idioms.
    More lenient than strict rule validation - focuses on style and effectiveness.
    """

    def __init__(self):
        # Common effective progressions by style
        self.common_patterns = {
            'pop': [
                [1, 5, 6, 4],  # I-V-vi-IV
                [1, 6, 4, 5],  # I-vi-IV-V
                [6, 4, 1, 5],  # vi-IV-I-V
            ],
            'jazz': [
                [2, 5, 1],  # ii-V-I
                [1, 6, 2, 5],  # I-vi-ii-V
                [3, 6, 2, 5],  # iii-vi-ii-V (circle progression)
            ],
            'classical': [
                [1, 4, 5, 1],  # I-IV-V-I
                [1, 4, 2, 5, 1],  # I-IV-ii-V-I
            ]
        }

    def identify_pattern(self, progression: ChordProgression) -> Dict[str, any]:
        """
        Identify if progression matches common patterns.

        Returns dict with:
        - matched_patterns: List of matching pattern types
        - style_suggestions: Suggested styles based on pattern
        - effectiveness_score: How well it follows common patterns
        """
        if not progression.scale:
            return {'matched_patterns': [], 'style_suggestions': [], 'effectiveness_score': 50}

        degrees = []
        for chord in progression.chords:
            degree = progression.scale.get_degree_of_note(chord.root)
            if degree:
                degrees.append(degree)

        matched = []
        for style, patterns in self.common_patterns.items():
            for pattern in patterns:
                if self._matches_pattern(degrees, pattern):
                    matched.append(style)
                    break

        effectiveness = 100 if matched else 50

        return {
            'matched_patterns': list(set(matched)),
            'style_suggestions': list(set(matched)) if matched else ['experimental', 'modal'],
            'effectiveness_score': effectiveness,
            'is_common_pattern': len(matched) > 0
        }

    def _matches_pattern(self, degrees: List[int], pattern: List[int]) -> bool:
        """Check if degrees contain the pattern"""
        if len(degrees) < len(pattern):
            return False

        for i in range(len(degrees) - len(pattern) + 1):
            if degrees[i:i+len(pattern)] == pattern:
                return True

        return False
