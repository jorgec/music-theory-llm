"""
Intelligent Evaluator and Ranking System

Ranks and scores musical suggestions based on multiple criteria:
- Music theory correctness
- Voice leading quality
- Stylistic appropriateness
- User preferences/history
- Context awareness
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.theory import Chord, ChordProgression, Scale, Pitch
from src.utils import MelodySuggester, HarmonicAnalyzer
from .validators import MusicTheoryValidator, ValidationResult, ProgressionPatternValidator


class RankingCriterion(Enum):
    """Criteria for ranking suggestions"""
    THEORY_CORRECTNESS = "theory_correctness"
    VOICE_LEADING = "voice_leading"
    STYLISTIC_FIT = "stylistic_fit"
    HARMONIC_INTEREST = "harmonic_interest"
    MELODIC_QUALITY = "melodic_quality"
    COMPLEXITY = "complexity"
    CREATIVITY = "creativity"


@dataclass
class SuggestionRanking:
    """
    Ranked suggestion with detailed scoring.
    """
    suggestion: Any  # The actual suggestion (chord, melody, etc.)
    overall_score: float  # 0-100
    criterion_scores: Dict[str, float] = field(default_factory=dict)
    explanation: str = ""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    confidence: float = 1.0  # How confident the model is (0-1)

    def __lt__(self, other):
        """For sorting by score"""
        return self.overall_score < other.overall_score


class IntelligentEvaluator:
    """
    Evaluates and ranks musical suggestions intelligently.

    Uses multiple evaluation strategies:
    1. Rule-based validation
    2. Pattern matching
    3. Statistical likelihood
    4. Style conformance
    5. User preference learning
    """

    def __init__(
        self,
        strictness: str = "moderate",
        style_preference: Optional[str] = None,
        user_history: Optional[Dict] = None
    ):
        """
        Initialize evaluator.

        Args:
            strictness: "strict", "moderate", or "lenient"
            style_preference: Preferred style ("jazz", "classical", "pop", etc.)
            user_history: Dictionary of user preferences and past choices
        """
        self.validator = MusicTheoryValidator(strictness)
        self.pattern_validator = ProgressionPatternValidator()
        self.style_preference = style_preference
        self.user_history = user_history or {}

        # Weights for different criteria (can be adjusted)
        self.criterion_weights = {
            RankingCriterion.THEORY_CORRECTNESS: 0.25,
            RankingCriterion.VOICE_LEADING: 0.20,
            RankingCriterion.STYLISTIC_FIT: 0.15,
            RankingCriterion.HARMONIC_INTEREST: 0.15,
            RankingCriterion.MELODIC_QUALITY: 0.15,
            RankingCriterion.CREATIVITY: 0.10,
        }

    def rank_melody_suggestions(
        self,
        suggestions: List[Any],  # MelodicOption objects
        context: Dict[str, Any]
    ) -> List[SuggestionRanking]:
        """
        Rank melody suggestions.

        Args:
            suggestions: List of melody suggestions
            context: Dict with 'progression', 'current_chord_idx', 'scale', etc.

        Returns:
            List of SuggestionRanking objects, sorted by score
        """
        rankings = []

        for suggestion in suggestions:
            scores = {}

            # 1. Music theory correctness
            scale = context.get('scale')
            validation = self.validator.validate_melody(suggestion.pitches, scale)
            scores[RankingCriterion.THEORY_CORRECTNESS.value] = validation.score

            # 2. Voice leading quality (already provided)
            scores[RankingCriterion.VOICE_LEADING.value] = (
                suggestion.voice_leading_quality * 20.0
            )

            # 3. Melodic quality - based on contour and interest
            melodic_score = self._evaluate_melodic_interest(suggestion.pitches)
            scores[RankingCriterion.MELODIC_QUALITY.value] = melodic_score

            # 4. Harmonic fit
            if 'current_chord' in context:
                suggester = MelodySuggester()
                harmony_analysis = suggester.analyze_melody_harmony_fit(
                    suggestion.pitches,
                    context['current_chord']
                )
                # Lower tension = better fit (for most contexts)
                harmonic_score = 100 * (1 - harmony_analysis['avg_tension'])
                scores[RankingCriterion.HARMONIC_INTEREST.value] = harmonic_score

            # 5. Stylistic fit
            if self.style_preference:
                style_score = self._evaluate_style_fit(
                    suggestion.pitches,
                    self.style_preference
                )
                scores[RankingCriterion.STYLISTIC_FIT.value] = style_score

            # 6. Creativity - reward unique approaches
            creativity_score = self._evaluate_creativity(suggestion.description)
            scores[RankingCriterion.CREATIVITY.value] = creativity_score

            # Calculate weighted overall score
            overall = sum(
                scores.get(criterion.value, 50) * weight
                for criterion, weight in self.criterion_weights.items()
            )

            # Generate explanation
            explanation = self._generate_melody_explanation(
                suggestion, scores, validation
            )

            ranking = SuggestionRanking(
                suggestion=suggestion,
                overall_score=overall,
                criterion_scores=scores,
                explanation=explanation,
                strengths=[s for s in validation.strengths],
                weaknesses=[v.description for v in validation.violations],
                confidence=0.85  # Could be model-based
            )

            rankings.append(ranking)

        # Sort by score (highest first)
        rankings.sort(reverse=True)

        return rankings

    def rank_harmonic_suggestions(
        self,
        suggestions: List[Any],  # HarmonicSuggestion objects
        context: Dict[str, Any]
    ) -> List[SuggestionRanking]:
        """
        Rank harmonic suggestions (chords, progressions).

        Args:
            suggestions: List of harmonic suggestions
            context: Dict with current progression, scale, etc.

        Returns:
            Sorted list of SuggestionRanking objects
        """
        rankings = []

        for suggestion in suggestions:
            scores = {}

            # 1. Voice leading quality
            if 'current_chord' in context:
                vl_validation = self.validator.validate_voice_leading(
                    context['current_chord'],
                    suggestion.chord
                )
                scores[RankingCriterion.VOICE_LEADING.value] = vl_validation.score
            else:
                scores[RankingCriterion.VOICE_LEADING.value] = (
                    suggestion.voice_leading_quality * 20.0
                )

            # 2. Theory correctness
            scores[RankingCriterion.THEORY_CORRECTNESS.value] = 85.0  # Default high

            # 3. Harmonic interest
            interest_score = self._evaluate_harmonic_interest(
                suggestion.chord,
                context.get('progression')
            )
            scores[RankingCriterion.HARMONIC_INTEREST.value] = interest_score

            # 4. Stylistic appropriateness
            style_score = self._evaluate_chord_style_fit(
                suggestion.suggestion_type,
                self.style_preference
            )
            scores[RankingCriterion.STYLISTIC_FIT.value] = style_score

            # 5. Complexity/sophistication
            complexity_score = self._evaluate_harmonic_complexity(suggestion.chord)
            scores[RankingCriterion.COMPLEXITY.value] = complexity_score

            # Calculate weighted score
            overall = sum(
                scores.get(criterion.value, 50) * weight
                for criterion, weight in self.criterion_weights.items()
            )

            explanation = self._generate_harmonic_explanation(suggestion, scores)

            ranking = SuggestionRanking(
                suggestion=suggestion,
                overall_score=overall,
                criterion_scores=scores,
                explanation=explanation,
                strengths=[suggestion.description],
                confidence=0.80
            )

            rankings.append(ranking)

        rankings.sort(reverse=True)
        return rankings

    def evaluate_progression(
        self,
        progression: ChordProgression,
        detailed: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation of a chord progression.

        Returns:
            Dict with scores, analysis, and improvement suggestions
        """
        # 1. Rule validation
        validation = self.validator.validate_chord_progression(progression)

        # 2. Pattern recognition
        pattern_analysis = self.pattern_validator.identify_pattern(progression)

        # 3. Functional analysis
        functions = progression.get_harmonic_functions()
        cadence = progression.get_cadence_type()

        # 4. Statistical analysis (if we have training data)
        # TODO: Add statistical likelihood scoring

        evaluation = {
            'overall_score': validation.score,
            'theory_score': validation.score,
            'pattern_match': pattern_analysis['matched_patterns'],
            'style_suggestions': pattern_analysis['style_suggestions'],
            'effectiveness': pattern_analysis['effectiveness_score'],
            'violations': [
                {
                    'rule': v.rule_name,
                    'severity': v.severity.value,
                    'description': v.description,
                    'suggestion': v.suggestion
                }
                for v in validation.violations
            ],
            'strengths': validation.strengths,
            'cadence': cadence,
            'harmonic_functions': [f.value if f else None for f in functions],
            'feedback': validation.overall_feedback
        }

        if detailed:
            # Add improvement suggestions
            evaluation['improvements'] = self._generate_progression_improvements(
                progression, validation, pattern_analysis
            )

        return evaluation

    def _evaluate_melodic_interest(self, melody: List[Pitch]) -> float:
        """
        Evaluate how interesting/compelling a melody is.

        Considers:
        - Contour variety
        - Rhythm (if we had that data)
        - Balance of steps vs leaps
        - Climax placement
        """
        if len(melody) < 3:
            return 50.0

        score = 50.0

        # Check contour variety
        directions = []
        for i in range(len(melody) - 1):
            if melody[i + 1].midi_number > melody[i].midi_number:
                directions.append(1)
            elif melody[i + 1].midi_number < melody[i].midi_number:
                directions.append(-1)
            else:
                directions.append(0)

        # Good melodies have directional changes
        direction_changes = sum(
            1 for i in range(len(directions) - 1)
            if directions[i] != directions[i + 1] and directions[i] != 0
        )

        change_ratio = direction_changes / max(1, len(directions) - 1)
        score += change_ratio * 30  # Up to +30 for good contour

        # Check for balance of steps vs leaps
        steps = sum(
            1 for i in range(len(melody) - 1)
            if abs(melody[i + 1].midi_number - melody[i].midi_number) <= 2
        )
        step_ratio = steps / max(1, len(melody) - 1)

        # Good melodies are ~60-80% stepwise
        if 0.6 <= step_ratio <= 0.8:
            score += 20
        elif 0.5 <= step_ratio <= 0.9:
            score += 10

        return min(100, score)

    def _evaluate_style_fit(self, melody: List[Pitch], style: str) -> float:
        """Evaluate how well melody fits a style"""
        # This is simplified; real implementation would use learned style models

        style_characteristics = {
            'classical': {'step_ratio': (0.7, 0.85), 'range': (12, 19)},
            'jazz': {'step_ratio': (0.5, 0.7), 'range': (12, 24)},
            'pop': {'step_ratio': (0.65, 0.8), 'range': (10, 17)},
            'folk': {'step_ratio': (0.75, 0.9), 'range': (10, 15)},
        }

        if style not in style_characteristics:
            return 70.0  # Neutral score

        chars = style_characteristics[style]
        score = 50.0

        # Check step ratio
        if len(melody) > 1:
            steps = sum(
                1 for i in range(len(melody) - 1)
                if abs(melody[i + 1].midi_number - melody[i].midi_number) <= 2
            )
            step_ratio = steps / (len(melody) - 1)

            if chars['step_ratio'][0] <= step_ratio <= chars['step_ratio'][1]:
                score += 25

        # Check range
        midi_nums = [p.midi_number for p in melody]
        range_semi = max(midi_nums) - min(midi_nums)

        if chars['range'][0] <= range_semi <= chars['range'][1]:
            score += 25

        return score

    def _evaluate_creativity(self, description: str) -> float:
        """Evaluate creativity based on approach type"""
        creativity_keywords = {
            'leap': 70,
            'chromatic': 75,
            'approach': 80,
            'drama': 75,
            'contrary': 70,
            'stepwise': 50,  # Less creative but solid
            'arpeggio': 60,
        }

        score = 50.0
        for keyword, bonus in creativity_keywords.items():
            if keyword in description.lower():
                score = max(score, bonus)

        return score

    def _evaluate_harmonic_interest(
        self,
        chord: Chord,
        progression: Optional[ChordProgression]
    ) -> float:
        """Evaluate how interesting a chord is in context"""
        score = 60.0  # Base score

        # Extended chords are more interesting
        if len(chord.notes) >= 4:
            score += 15
        if len(chord.notes) >= 5:
            score += 10

        # Altered chords are interesting
        if chord.is_diminished() or chord.is_augmented():
            score += 10

        # Check for variety in progression
        if progression:
            # If this chord is different from recent chords, it's interesting
            chord_str = str(chord)
            recent_chords = [str(c) for c in progression.chords[-3:]]
            if chord_str not in recent_chords:
                score += 15

        return min(100, score)

    def _evaluate_chord_style_fit(
        self,
        suggestion_type: str,
        style: Optional[str]
    ) -> float:
        """Evaluate how well a harmonic suggestion fits a style"""
        if not style:
            return 70.0

        style_appropriateness = {
            'jazz': {
                'secondary_dominant': 90,
                'tritone_substitution': 95,
                'modal_interchange': 85,
                'passing_chord': 80,
            },
            'classical': {
                'secondary_dominant': 85,
                'passing_chord': 90,
                'modal_interchange': 70,
                'tritone_substitution': 50,
            },
            'pop': {
                'modal_interchange': 85,
                'passing_chord': 75,
                'secondary_dominant': 70,
                'tritone_substitution': 60,
            }
        }

        if style in style_appropriateness:
            return style_appropriateness[style].get(suggestion_type, 70.0)

        return 70.0

    def _evaluate_harmonic_complexity(self, chord: Chord) -> float:
        """Evaluate harmonic complexity/sophistication"""
        complexity = 40.0

        # More notes = more complex
        complexity += len(chord.notes) * 10

        # Seventh chords and beyond are sophisticated
        if len(chord.notes) >= 4:
            complexity += 20

        # Altered chords are complex
        if chord.is_diminished():
            complexity += 15
        if chord.is_augmented():
            complexity += 15

        return min(100, complexity)

    def _generate_melody_explanation(
        self,
        suggestion: Any,
        scores: Dict[str, float],
        validation: ValidationResult
    ) -> str:
        """Generate human-readable explanation of ranking"""
        parts = []

        # Overall assessment
        if scores.get(RankingCriterion.THEORY_CORRECTNESS.value, 0) >= 85:
            parts.append("Strong melodic construction")

        if scores.get(RankingCriterion.VOICE_LEADING.value, 0) >= 80:
            parts.append("excellent voice leading")

        if scores.get(RankingCriterion.MELODIC_QUALITY.value, 0) >= 80:
            parts.append("compelling contour")

        # Add the original description
        parts.append(suggestion.description.lower())

        explanation = ". ".join(parts[:2]) if parts else "Good melodic option"

        return explanation.capitalize()

    def _generate_harmonic_explanation(
        self,
        suggestion: Any,
        scores: Dict[str, float]
    ) -> str:
        """Generate explanation for harmonic suggestion ranking"""
        parts = [suggestion.description]

        if scores.get(RankingCriterion.VOICE_LEADING.value, 0) >= 85:
            parts.append("Smooth voice leading.")

        if scores.get(RankingCriterion.COMPLEXITY.value, 0) >= 75:
            parts.append("Sophisticated harmonic choice.")

        return " ".join(parts)

    def _generate_progression_improvements(
        self,
        progression: ChordProgression,
        validation: ValidationResult,
        pattern_analysis: Dict
    ) -> List[Dict[str, str]]:
        """Generate specific improvement suggestions"""
        improvements = []

        # Based on violations
        for violation in validation.violations:
            if violation.suggestion:
                improvements.append({
                    'issue': violation.description,
                    'suggestion': violation.suggestion,
                    'priority': violation.severity.value
                })

        # Based on pattern matching
        if not pattern_analysis['is_common_pattern']:
            improvements.append({
                'issue': 'Progression does not follow common patterns',
                'suggestion': f"Consider patterns common in {', '.join(pattern_analysis['style_suggestions'][:2])} music",
                'priority': 'info'
            })

        # Suggest enhancements
        if validation.score >= 75:
            improvements.append({
                'issue': 'Good progression - ready for enhancement',
                'suggestion': 'Consider adding passing chords, extensions, or secondary dominants',
                'priority': 'info'
            })

        return improvements
