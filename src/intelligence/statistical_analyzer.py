"""
Statistical Analysis of Chord Progressions

Analyzes large datasets of progressions to learn common patterns,
transition probabilities, and stylistic characteristics.
"""

from typing import List, Dict, Optional, Tuple, Counter as CounterType
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import json
import pickle
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.theory import Chord, ChordProgression, Scale, Note
from src.theory.chords import ChordQuality


@dataclass
class ProgressionStatistics:
    """Statistics about chord progressions"""
    total_progressions: int = 0
    total_transitions: int = 0
    chord_frequency: Counter = field(default_factory=Counter)
    transition_frequency: Counter = field(default_factory=Counter)  # (chord1, chord2) -> count
    degree_transitions: Counter = field(default_factory=Counter)  # (degree1, degree2) -> count
    cadence_frequency: Counter = field(default_factory=Counter)
    common_patterns: List[Tuple[List[int], int]] = field(default_factory=list)  # (pattern, frequency)


class StatisticalProgressionAnalyzer:
    """
    Analyzes chord progressions statistically to learn common patterns.

    Can:
    - Build transition probability matrices
    - Identify common patterns
    - Predict likely next chords
    - Classify progression styles
    - Generate statistically likely progressions
    """

    def __init__(self):
        self.stats = ProgressionStatistics()
        self.transition_probs = {}  # Markov chain probabilities
        self.style_specific_stats = defaultdict(lambda: ProgressionStatistics())

    def analyze_dataset(
        self,
        progressions: List[ChordProgression],
        style: Optional[str] = None
    ):
        """
        Analyze a dataset of progressions to build statistics.

        Args:
            progressions: List of chord progressions to analyze
            style: Optional style label for style-specific analysis
        """
        target_stats = self.style_specific_stats[style] if style else self.stats

        for progression in progressions:
            target_stats.total_progressions += 1

            # Count individual chords
            for chord in progression.chords:
                chord_str = str(chord)
                target_stats.chord_frequency[chord_str] += 1

            # Count transitions
            for i in range(len(progression.chords) - 1):
                chord1_str = str(progression.chords[i])
                chord2_str = str(progression.chords[i + 1])

                target_stats.transition_frequency[(chord1_str, chord2_str)] += 1
                target_stats.total_transitions += 1

            # Count degree transitions (if scale is known)
            if progression.scale:
                degrees = []
                for chord in progression.chords:
                    degree = progression.scale.get_degree_of_note(chord.root)
                    if degree:
                        degrees.append(degree)

                for i in range(len(degrees) - 1):
                    target_stats.degree_transitions[(degrees[i], degrees[i + 1])] += 1

                # Store pattern if length 3-5
                if 3 <= len(degrees) <= 5:
                    pattern = tuple(degrees)
                    found = False
                    for i, (p, count) in enumerate(target_stats.common_patterns):
                        if p == list(pattern):
                            target_stats.common_patterns[i] = (p, count + 1)
                            found = True
                            break
                    if not found:
                        target_stats.common_patterns.append((list(pattern), 1))

            # Count cadences
            cadence = progression.get_cadence_type()
            if cadence:
                target_stats.cadence_frequency[cadence] += 1

        # Sort common patterns by frequency
        target_stats.common_patterns.sort(key=lambda x: x[1], reverse=True)

        # Build transition probability matrix
        self._build_transition_probabilities(style)

    def _build_transition_probabilities(self, style: Optional[str] = None):
        """Build Markov chain transition probabilities"""
        target_stats = self.style_specific_stats[style] if style else self.stats

        probs = defaultdict(dict)

        # Group by first chord
        chord_outgoing = defaultdict(Counter)
        for (chord1, chord2), count in target_stats.transition_frequency.items():
            chord_outgoing[chord1][chord2] = count

        # Normalize to probabilities
        for chord1, transitions in chord_outgoing.items():
            total = sum(transitions.values())
            for chord2, count in transitions.items():
                probs[chord1][chord2] = count / total

        if style:
            self.style_specific_stats[style].transition_probs = probs
        else:
            self.transition_probs = probs

    def predict_next_chord(
        self,
        current_chord: Chord,
        scale: Optional[Scale] = None,
        style: Optional[str] = None,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Predict most likely next chords based on statistics.

        Args:
            current_chord: Current chord
            scale: Optional scale context
            style: Optional style context
            top_k: Number of predictions to return

        Returns:
            List of (chord_name, probability) tuples
        """
        chord_str = str(current_chord)

        # Get relevant probability distribution
        if style and style in self.style_specific_stats:
            probs = self.style_specific_stats[style].transition_probs.get(chord_str, {})
        else:
            probs = self.transition_probs.get(chord_str, {})

        if not probs:
            # Fall back to degree-based prediction if we have scale
            if scale:
                return self._predict_by_degree(current_chord, scale, style, top_k)
            return []

        # Sort by probability and return top k
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        return sorted_probs[:top_k]

    def _predict_by_degree(
        self,
        current_chord: Chord,
        scale: Scale,
        style: Optional[str],
        top_k: int
    ) -> List[Tuple[str, float]]:
        """Predict next chord by scale degree transitions"""
        current_degree = scale.get_degree_of_note(current_chord.root)
        if not current_degree:
            return []

        # Get degree transition probabilities
        target_stats = self.style_specific_stats[style] if style else self.stats

        degree_probs = {}
        total = 0

        for (deg1, deg2), count in target_stats.degree_transitions.items():
            if deg1 == current_degree:
                degree_probs[deg2] = count
                total += count

        if total == 0:
            return []

        # Normalize and convert to chord predictions
        predictions = []
        for degree, count in sorted(degree_probs.items(), key=lambda x: x[1], reverse=True)[:top_k]:
            prob = count / total

            # Build chord from scale degree
            from src.theory import chord_from_scale_degree
            predicted_chord = chord_from_scale_degree(scale, degree, seventh=True)

            predictions.append((str(predicted_chord), prob))

        return predictions

    def get_common_patterns(
        self,
        style: Optional[str] = None,
        top_k: int = 10
    ) -> List[Tuple[List[int], int, float]]:
        """
        Get most common progression patterns.

        Returns:
            List of (pattern, count, frequency) tuples
        """
        target_stats = self.style_specific_stats[style] if style else self.stats

        results = []
        total_progs = max(1, target_stats.total_progressions)

        for pattern, count in target_stats.common_patterns[:top_k]:
            frequency = count / total_progs
            results.append((pattern, count, frequency))

        return results

    def analyze_progression_likelihood(
        self,
        progression: ChordProgression,
        style: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Analyze how likely/common a progression is based on learned statistics.

        Returns:
            Dict with likelihood score and analysis
        """
        if len(progression.chords) < 2:
            return {'likelihood_score': 50, 'analysis': 'Too short to analyze'}

        target_stats = self.style_specific_stats[style] if style else self.stats
        probs = self.style_specific_stats[style].transition_probs if style else self.transition_probs

        # Calculate transition probabilities
        transition_probs = []
        for i in range(len(progression.chords) - 1):
            chord1_str = str(progression.chords[i])
            chord2_str = str(progression.chords[i + 1])

            if chord1_str in probs and chord2_str in probs[chord1_str]:
                prob = probs[chord1_str][chord2_str]
                transition_probs.append(prob)
            else:
                transition_probs.append(0.01)  # Small prob for unseen transitions

        # Average probability (geometric mean for small numbers)
        if transition_probs:
            import math
            log_prob_sum = sum(math.log(max(p, 0.0001)) for p in transition_probs)
            avg_prob = math.exp(log_prob_sum / len(transition_probs))
            likelihood_score = min(100, avg_prob * 1000)  # Scale to 0-100
        else:
            likelihood_score = 50

        # Check if matches common patterns
        matches_pattern = False
        if progression.scale:
            degrees = [progression.scale.get_degree_of_note(c.root) for c in progression.chords]
            degrees = [d for d in degrees if d is not None]

            for pattern, count in target_stats.common_patterns[:20]:
                if self._pattern_matches(degrees, pattern):
                    matches_pattern = True
                    break

        analysis = {
            'likelihood_score': likelihood_score,
            'avg_transition_probability': sum(transition_probs) / len(transition_probs) if transition_probs else 0,
            'unusual_transitions': [
                f"{progression.chords[i]} → {progression.chords[i+1]}"
                for i, p in enumerate(transition_probs)
                if p < 0.05
            ],
            'matches_common_pattern': matches_pattern,
            'style': style or 'general',
            'interpretation': self._interpret_likelihood(likelihood_score, matches_pattern)
        }

        return analysis

    def _pattern_matches(self, degrees: List[int], pattern: List[int]) -> bool:
        """Check if degrees contain or match pattern"""
        if len(degrees) < len(pattern):
            return False

        for i in range(len(degrees) - len(pattern) + 1):
            if degrees[i:i+len(pattern)] == pattern:
                return True

        return False

    def _interpret_likelihood(self, score: float, matches_pattern: bool) -> str:
        """Interpret likelihood score"""
        if matches_pattern:
            return "Very common progression - follows established patterns"
        elif score >= 75:
            return "Common progression with high transition likelihood"
        elif score >= 50:
            return "Moderate likelihood - somewhat common"
        elif score >= 25:
            return "Uncommon but not unusual"
        else:
            return "Very uncommon progression - highly creative/experimental"

    def generate_likely_progression(
        self,
        start_chord: Chord,
        scale: Scale,
        length: int = 4,
        style: Optional[str] = None,
        temperature: float = 1.0
    ) -> ChordProgression:
        """
        Generate a statistically likely progression.

        Args:
            start_chord: Starting chord
            scale: Scale/key
            length: Number of chords to generate
            style: Optional style
            temperature: Randomness (0=deterministic, 1=normal, >1=more random)

        Returns:
            Generated chord progression
        """
        import random
        import math

        chords = [start_chord]
        current = start_chord

        for _ in range(length - 1):
            predictions = self.predict_next_chord(current, scale, style, top_k=10)

            if not predictions:
                # Fall back to simple diatonic progression
                current_degree = scale.get_degree_of_note(current.root)
                if current_degree:
                    next_degree = (current_degree % 7) + 1
                    from src.theory import chord_from_scale_degree
                    next_chord = chord_from_scale_degree(scale, next_degree)
                    chords.append(next_chord)
                    current = next_chord
                continue

            # Apply temperature to probabilities
            if temperature != 1.0:
                chord_names, probs = zip(*predictions)
                # Apply temperature and renormalize
                adjusted_probs = [math.pow(p, 1/temperature) for p in probs]
                total = sum(adjusted_probs)
                adjusted_probs = [p/total for p in adjusted_probs]
                predictions = list(zip(chord_names, adjusted_probs))

            # Sample from distribution
            chord_names, probs = zip(*predictions)
            chosen_name = random.choices(chord_names, weights=probs, k=1)[0]

            # Parse chosen chord
            from src.theory.chords import Chord as ChordClass
            next_chord = ChordClass.from_symbol(chosen_name)
            chords.append(next_chord)
            current = next_chord

        return ChordProgression(chords, scale)

    def save_statistics(self, filepath: str):
        """Save learned statistics to file"""
        data = {
            'stats': self.stats,
            'style_stats': dict(self.style_specific_stats),
            'transition_probs': self.transition_probs
        }

        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

    def load_statistics(self, filepath: str):
        """Load statistics from file"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        self.stats = data['stats']
        self.style_specific_stats = defaultdict(lambda: ProgressionStatistics(), data['style_stats'])
        self.transition_probs = data['transition_probs']

    def get_summary_report(self, style: Optional[str] = None) -> str:
        """Generate a summary report of learned statistics"""
        target_stats = self.style_specific_stats[style] if style else self.stats

        report = []
        report.append("=" * 60)
        report.append(f"STATISTICAL ANALYSIS REPORT{' - ' + style if style else ''}")
        report.append("=" * 60)
        report.append(f"\nTotal progressions analyzed: {target_stats.total_progressions}")
        report.append(f"Total chord transitions: {target_stats.total_transitions}")

        # Most common chords
        report.append("\nMost Common Chords:")
        for chord, count in target_stats.chord_frequency.most_common(10):
            freq = count / max(1, sum(target_stats.chord_frequency.values()))
            report.append(f"  {chord}: {count} ({freq*100:.1f}%)")

        # Most common transitions
        report.append("\nMost Common Transitions:")
        for (c1, c2), count in target_stats.transition_frequency.most_common(10):
            freq = count / max(1, target_stats.total_transitions)
            report.append(f"  {c1} → {c2}: {count} ({freq*100:.1f}%)")

        # Common patterns
        report.append("\nMost Common Patterns (by degree):")
        for pattern, count, freq in self.get_common_patterns(style, top_k=10):
            roman = ' - '.join(['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'][d-1] for d in pattern)
            report.append(f"  {roman}: {count} ({freq*100:.1f}%)")

        # Cadence types
        report.append("\nCadence Frequency:")
        for cadence, count in target_stats.cadence_frequency.most_common():
            freq = count / max(1, target_stats.total_progressions)
            report.append(f"  {cadence}: {count} ({freq*100:.1f}%)")

        report.append("=" * 60)

        return "\n".join(report)
