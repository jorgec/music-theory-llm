"""
Music Theory Recommendation System

Provides intelligent recommendations for:
- Chord progressions
- Melodies
- Licks and riffs

Focused on priority styles: neo soul, blues, progressive metal, rock fusion
"""

import torch
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import pickle
from collections import defaultdict

from .theory import ChordProgression, Chord, Scale, Note
from .models import MusicTheoryTransformer
from .models.melody_harmonization import MelodyGenerator
from .tokenizer import MusicTheoryTokenizer


@dataclass
class Recommendation:
    """A single recommendation with metadata"""
    item: object  # ChordProgression, melody tokens, or lick pattern
    score: float
    style: str
    explanation: str
    metadata: Dict = None


class ChordProgressionRecommender:
    """
    Recommend chord progressions based on style, key, and context

    Uses multiple strategies:
    1. Statistical analysis (transition probabilities)
    2. Neural embeddings (learned similarity)
    3. Rule-based filtering (music theory validation)
    """

    def __init__(self, data_dir: str = 'data/styles'):
        self.data_dir = Path(data_dir)
        self.progressions_by_style = {}
        self.transition_probs = {}

        # Load all style-specific progressions
        self._load_progressions()
        self._compute_transition_probabilities()

    def _load_progressions(self):
        """Load all style-specific progression datasets"""
        for style_file in self.data_dir.glob('*_progressions.pkl'):
            style = style_file.stem.replace('_progressions', '')

            with open(style_file, 'rb') as f:
                progressions = pickle.load(f)
                self.progressions_by_style[style] = progressions

    def _compute_transition_probabilities(self):
        """Compute chord transition probabilities for each style"""
        for style, progressions in self.progressions_by_style.items():
            transitions = defaultdict(lambda: defaultdict(int))

            for prog in progressions:
                for i in range(len(prog.chords) - 1):
                    chord1 = self._chord_to_key(prog.chords[i])
                    chord2 = self._chord_to_key(prog.chords[i + 1])
                    transitions[chord1][chord2] += 1

            # Normalize to probabilities
            for chord1 in transitions:
                total = sum(transitions[chord1].values())
                for chord2 in transitions[chord1]:
                    transitions[chord1][chord2] /= total

            self.transition_probs[style] = transitions

    def _chord_to_key(self, chord: Chord) -> str:
        """Convert chord to string key for transition tracking"""
        return f"{chord.root.name}_{chord.quality.name}"

    def recommend_progressions(
        self,
        style: str,
        key: Optional[Note] = None,
        num_recommendations: int = 5,
        min_similarity: float = 0.0
    ) -> List[Recommendation]:
        """
        Recommend chord progressions for a given style and key

        Args:
            style: Musical style (neo_soul, blues, progressive_metal, etc.)
            key: Optional key signature filter
            num_recommendations: Number of recommendations to return
            min_similarity: Minimum similarity score threshold

        Returns:
            List of Recommendation objects sorted by score
        """
        if style not in self.progressions_by_style:
            available = list(self.progressions_by_style.keys())
            raise ValueError(f"Style '{style}' not found. Available: {available}")

        progressions = self.progressions_by_style[style]

        # Filter by key if specified
        if key:
            progressions = [p for p in progressions
                          if p.scale and p.scale.root.name == key.name]

        recommendations = []

        for prog in progressions:
            # Calculate score based on multiple factors
            score = self._calculate_progression_score(prog, style)

            if score >= min_similarity:
                explanation = self._explain_progression(prog, style)

                recommendations.append(Recommendation(
                    item=prog,
                    score=score,
                    style=style,
                    explanation=explanation,
                    metadata={
                        'num_chords': len(prog.chords),
                        'key': prog.scale.root.name if prog.scale else None
                    }
                ))

        # Sort by score and return top N
        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations[:num_recommendations]

    def _calculate_progression_score(self, prog: ChordProgression, style: str) -> float:
        """
        Calculate a quality score for a progression

        Factors:
        - Transition probability (how typical for the style)
        - Variety (chord diversity)
        - Smoothness (voice leading quality)
        """
        score = 1.0

        # Transition probability score
        if style in self.transition_probs:
            transitions = self.transition_probs[style]
            transition_scores = []

            for i in range(len(prog.chords) - 1):
                chord1_key = self._chord_to_key(prog.chords[i])
                chord2_key = self._chord_to_key(prog.chords[i + 1])

                if chord1_key in transitions and chord2_key in transitions[chord1_key]:
                    transition_scores.append(transitions[chord1_key][chord2_key])
                else:
                    transition_scores.append(0.1)  # Rare transition

            if transition_scores:
                score *= np.mean(transition_scores) * 2  # Weight transitions

        # Variety score (more unique chords = better)
        unique_chords = len(set(self._chord_to_key(c) for c in prog.chords))
        variety_score = unique_chords / len(prog.chords)
        score *= (0.5 + variety_score * 0.5)

        return min(score, 1.0)

    def _explain_progression(self, prog: ChordProgression, style: str) -> str:
        """Generate human-readable explanation for why this progression is recommended"""
        chord_names = [c.to_symbol() for c in prog.chords]

        explanations = []

        # Style-specific explanations
        if style == 'neo_soul':
            if any('9' in str(c.quality.value) for c in prog.chords):
                explanations.append("Features extended chords typical of neo soul")
        elif style == 'blues':
            if any('7' in str(c.quality.value) for c in prog.chords):
                explanations.append("Uses dominant 7th chords characteristic of blues")
        elif style == 'progressive_metal':
            if prog.scale and any(hasattr(prog.scale, 'mode') for _ in [1]):
                explanations.append("Modal progression common in progressive metal")

        base_explanation = f"Progression: {' → '.join(chord_names[:4])}"
        if explanations:
            base_explanation += f" - {'; '.join(explanations)}"

        return base_explanation

    def recommend_next_chord(
        self,
        current_progression: List[Chord],
        style: str,
        top_k: int = 5
    ) -> List[Tuple[Chord, float, str]]:
        """
        Recommend next chord based on current progression

        Returns:
            List of (chord, probability, explanation) tuples
        """
        if not current_progression:
            return []

        last_chord_key = self._chord_to_key(current_progression[-1])

        if style not in self.transition_probs:
            return []

        transitions = self.transition_probs[style]

        if last_chord_key not in transitions:
            return []

        # Get top K most likely next chords
        next_chords = transitions[last_chord_key]
        sorted_chords = sorted(next_chords.items(), key=lambda x: x[1], reverse=True)[:top_k]

        recommendations = []
        for chord_key, prob in sorted_chords:
            # Parse chord_key back to chord (simplified)
            explanation = f"Common {style} transition ({prob*100:.1f}% probability)"
            recommendations.append((chord_key, prob, explanation))

        return recommendations


class MelodyRecommender:
    """
    Recommend melodies that fit with chord progressions

    Uses the MelodyGenerator model trained on style-specific data
    """

    def __init__(self, model_path: Optional[str] = None):
        self.tokenizer = MusicTheoryTokenizer()
        self.model = None

        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path: str):
        """Load pre-trained melody generation model"""
        self.model = MelodyGenerator(
            vocab_size=len(self.tokenizer),
            d_model=256,
            num_layers=4
        )

        checkpoint = torch.load(model_path, map_location='cpu')
        self.model.load_state_dict(checkpoint)
        self.model.eval()

    def recommend_melodies(
        self,
        chord_progression: ChordProgression,
        num_variations: int = 5,
        temperature: float = 1.0
    ) -> List[Recommendation]:
        """
        Generate melody recommendations for a chord progression

        Args:
            chord_progression: The chord progression to harmonize
            num_variations: Number of different melodies to generate
            temperature: Sampling temperature (higher = more creative)

        Returns:
            List of melody recommendations
        """
        if not self.model:
            # Return rule-based melodies if no model loaded
            return self._rule_based_melodies(chord_progression, num_variations)

        recommendations = []

        # Encode progression
        chord_tokens = self.tokenizer.encode_progression(chord_progression)
        chord_tensor = torch.tensor([chord_tokens])

        for i in range(num_variations):
            # Generate melody
            melody_tokens = self.model.generate_melody(
                chord_tensor,
                temperature=temperature + (i * 0.1),  # Vary temperature
                max_length=32
            )

            score = 1.0 - (i * 0.1)  # First variations score higher

            recommendations.append(Recommendation(
                item=melody_tokens,
                score=score,
                style=chord_progression.style or 'unknown',
                explanation=f"Generated melody variation {i+1} (temp={temperature + i*0.1:.1f})",
                metadata={'tokens': melody_tokens}
            ))

        return recommendations

    def _rule_based_melodies(
        self,
        chord_progression: ChordProgression,
        num_variations: int
    ) -> List[Recommendation]:
        """Generate melodies using music theory rules (fallback when no model)"""
        recommendations = []

        for i in range(num_variations):
            # Simple approach: use chord tones and passing tones
            melody_notes = []

            for chord in chord_progression.chords:
                # Use chord tones as melody notes
                chord_tones = [chord.root]  # Simplified - would add 3rd, 5th, etc.
                melody_notes.extend(chord_tones)

            recommendations.append(Recommendation(
                item=melody_notes,
                score=0.7 - (i * 0.1),
                style=chord_progression.style or 'unknown',
                explanation=f"Rule-based melody using chord tones",
                metadata={'approach': 'rule_based'}
            ))

        return recommendations


class LickRecommender:
    """
    Recommend licks and riffs based on style and harmonic context

    Maintains a database of style-specific licks represented as interval patterns
    """

    def __init__(self):
        self.lick_database = self._build_lick_database()

    def _build_lick_database(self) -> Dict[str, List[Dict]]:
        """Build database of style-specific licks"""
        licks = {
            'neo_soul': [
                {
                    'name': 'D\'Angelo Lick',
                    'intervals': [0, 2, 4, 5, 7, 5, 4, 2],  # Scale degrees
                    'rhythm': 'syncopated',
                    'description': 'Chromatic approach to chord tones with syncopation'
                },
                {
                    'name': 'Neo Soul Run',
                    'intervals': [0, 2, 3, 5, 7, 9, 11, 12],
                    'rhythm': 'flowing',
                    'description': 'Extended chord arpeggio with 9th and 11th'
                },
            ],
            'blues': [
                {
                    'name': 'Classic Blues Box',
                    'intervals': [0, 3, 4, 5, 4, 3, 0],  # Minor pentatonic with blue note
                    'rhythm': 'swung',
                    'description': 'Blues box position 1 - pentatonic with bent blue note (b5)',
                    'techniques': ['bend on 4th (blue note)', 'vibrato']
                },
                {
                    'name': 'BB King Box',
                    'intervals': [0, 3, 0, 3, 5, 6, 5, 3],
                    'rhythm': 'swung',
                    'description': 'BB King signature box pattern with quick returns',
                    'techniques': ['quick hammer-ons', 'wide vibrato']
                },
                {
                    'name': 'Turnaround Lick',
                    'intervals': [7, 6, 5, 4, 3, 2, 1, 0],
                    'rhythm': 'descending',
                    'description': 'Chromatic descent for I-VI-ii-V turnarounds',
                    'techniques': ['chromatic run', 'swing eighth notes']
                },
                {
                    'name': 'Albert King Lick',
                    'intervals': [0, 3, 5, 3, 5, 7, 5, 3],
                    'rhythm': 'laid-back',
                    'description': 'Behind-the-beat phrasing in minor pentatonic',
                    'techniques': ['heavy bends', 'behind the beat']
                },
                {
                    'name': 'Stevie Ray Vaughan Lick',
                    'intervals': [5, 4, 3, 0, 3, 5, 7, 10],
                    'rhythm': 'aggressive',
                    'description': 'Texas blues with blue note and octave jump',
                    'techniques': ['aggressive bends', 'palm muting']
                },
                {
                    'name': 'Double Stop Blues',
                    'intervals': [0, 3, 0, 3, 5, 7, 5, 3],  # Play in 3rds
                    'rhythm': 'chunky',
                    'description': 'Double stop sixths - classic blues sound',
                    'techniques': ['double stops', 'rake']
                },
                {
                    'name': 'Slide Blues Lick',
                    'intervals': [0, 5, 7, 10, 12, 10, 7, 5],
                    'rhythm': 'smooth',
                    'description': 'Open position slide lick',
                    'techniques': ['slide', 'open tuning']
                },
                {
                    'name': 'Muddy Waters Lick',
                    'intervals': [0, 3, 4, 3, 0, 3, 5],
                    'rhythm': 'heavy-swung',
                    'description': 'Chicago blues with blue note emphasis',
                    'techniques': ['heavy vibrato', 'quarter bends']
                },
                {
                    'name': 'T-Bone Walker Lick',
                    'intervals': [7, 5, 3, 5, 7, 10, 12],
                    'rhythm': 'smooth-jazzy',
                    'description': 'Jazz-blues hybrid with 6th interval',
                    'techniques': ['smooth legato', 'light vibrato']
                },
                {
                    'name': 'Diminished Blues Run',
                    'intervals': [0, 3, 4, 6, 7, 9, 10, 12],
                    'rhythm': 'fast',
                    'description': 'Blues scale with passing diminished tones',
                    'techniques': ['hammer-ons', 'pull-offs']
                },
            ],
            'jazz': [
                {
                    'name': 'ii-V-I Bebop Lick',
                    'intervals': [0, 2, 4, 5, 7, 9, 11, 12],
                    'rhythm': 'bebop',
                    'description': 'Classic bebop line over ii-V-I with chromatic approach',
                    'techniques': ['chromatic approach tones', 'eighth note lines']
                },
                {
                    'name': 'Altered Scale Lick',
                    'intervals': [0, 1, 3, 4, 6, 8, 10, 12],
                    'rhythm': 'outside',
                    'description': 'Altered dominant scale for tension (7alt chord)',
                    'techniques': ['altered tones', 'outside playing']
                },
                {
                    'name': 'Wes Montgomery Octaves',
                    'intervals': [0, 12, 2, 14, 4, 16, 5, 17],  # Octaves
                    'rhythm': 'thumb-style',
                    'description': 'Parallel octaves in the style of Wes Montgomery',
                    'techniques': ['thumb picking', 'parallel octaves']
                },
                {
                    'name': 'Pat Martino Minor ii-V',
                    'intervals': [0, 2, 3, 5, 7, 8, 10, 12],
                    'rhythm': 'modal',
                    'description': 'Minor ii-V-i using dorian and harmonic minor',
                    'techniques': ['modal playing', 'position shifting']
                },
                {
                    'name': 'Diminished Arpeggio',
                    'intervals': [0, 3, 6, 9, 12, 15, 18, 21],
                    'rhythm': 'symmetrical',
                    'description': 'Diminished 7th arpeggio - cycles every minor 3rd',
                    'techniques': ['sweep picking', 'symmetrical fingering']
                },
                {
                    'name': 'Charlie Parker Blues',
                    'intervals': [0, 2, 4, 5, 7, 5, 4, 2],
                    'rhythm': 'bebop-swing',
                    'description': 'Bird blues with chromatic passing tones',
                    'techniques': ['fast alternate picking', 'swing phrasing']
                },
                {
                    'name': 'Grant Green Soul Jazz',
                    'intervals': [0, 3, 5, 7, 10, 12],
                    'rhythm': 'soul-jazz',
                    'description': 'Bluesy jazz with minor pentatonic',
                    'techniques': ['slight bends', 'funky rhythm']
                },
                {
                    'name': 'Joe Pass Walking Bass',
                    'intervals': [0, 4, 7, 11, 12, 16, 19, 23],  # Chord tones walking
                    'rhythm': 'walking',
                    'description': 'Walking bassline with chord melody',
                    'techniques': ['thumb bass', 'chord melody']
                },
                {
                    'name': 'Half-Diminished Lick',
                    'intervals': [0, 2, 3, 5, 6, 8, 10, 12],
                    'rhythm': 'locrian',
                    'description': 'Locrian mode over m7b5 chord',
                    'techniques': ['voice leading', 'modal approach']
                },
                {
                    'name': 'Lydian Dominant Run',
                    'intervals': [0, 2, 4, 6, 7, 9, 10, 12],
                    'rhythm': 'melodic-minor',
                    'description': 'Lydian dominant (melodic minor 4th mode) over 7#11',
                    'techniques': ['raised 4th', 'exotic sound']
                },
            ],
            'progressive_metal': [
                {
                    'name': 'Lydian Shred',
                    'intervals': [0, 2, 4, 6, 7, 9, 11, 12],
                    'rhythm': 'fast',
                    'description': 'Lydian mode run with raised 4th'
                },
                {
                    'name': 'Phrygian Riff',
                    'intervals': [0, 1, 3, 5, 7, 8, 10, 12],
                    'rhythm': 'heavy',
                    'description': 'Phrygian dominant sound'
                },
                {
                    'name': 'Sweep Arpeggio',
                    'intervals': [0, 4, 7, 12, 16, 19],
                    'rhythm': 'sweeping',
                    'description': 'Extended arpeggio for sweep picking'
                },
            ],
            'rock_fusion': [
                {
                    'name': 'Jazz-Rock Fusion Lick',
                    'intervals': [0, 2, 4, 6, 7, 6, 4, 2],
                    'rhythm': 'fusion',
                    'description': 'Mixolydian with chromatic approach'
                },
                {
                    'name': 'Allan Holdsworth Style',
                    'intervals': [0, 3, 5, 7, 10, 12, 15],
                    'rhythm': 'legato',
                    'description': 'Wide interval jumps with legato'
                },
            ],
        }

        return licks

    def recommend_licks(
        self,
        style: str,
        key: Note,
        chord_context: Optional[Chord] = None,
        num_recommendations: int = 5
    ) -> List[Recommendation]:
        """
        Recommend licks for a given style and harmonic context

        Args:
            style: Musical style
            key: Key signature
            chord_context: Current chord (optional, for context-aware suggestions)
            num_recommendations: Number of licks to recommend

        Returns:
            List of lick recommendations with transposed intervals
        """
        if style not in self.lick_database:
            return []

        licks = self.lick_database[style]
        recommendations = []

        for i, lick in enumerate(licks[:num_recommendations]):
            # Transpose intervals to the given key
            transposed = self._transpose_lick(lick['intervals'], key)

            score = 1.0 - (i * 0.15)

            recommendations.append(Recommendation(
                item={
                    'name': lick['name'],
                    'intervals': lick['intervals'],
                    'transposed_notes': transposed,
                    'rhythm': lick['rhythm']
                },
                score=score,
                style=style,
                explanation=lick['description'],
                metadata={
                    'key': key.name,
                    'rhythm': lick['rhythm']
                }
            ))

        return recommendations

    def _transpose_lick(self, intervals: List[int], key: Note) -> List[str]:
        """Transpose lick intervals to specific key"""
        # Simplified - would use actual scale transposition
        scale_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

        # Find key position
        try:
            key_idx = scale_notes.index(key.name)
        except ValueError:
            key_idx = 0

        transposed = []
        for interval in intervals:
            note_idx = (key_idx + interval) % len(scale_notes)
            octave = (key_idx + interval) // len(scale_notes)
            transposed.append(f"{scale_notes[note_idx]}{4 + octave}")

        return transposed


class MusicRecommendationSystem:
    """
    Unified recommendation system combining all recommenders

    Primary focus on: neo soul, blues, progressive metal, rock fusion
    """

    PRIORITY_STYLES = ['neo_soul', 'blues', 'progressive_metal', 'rock_fusion']

    def __init__(self, data_dir: str = 'data/styles', model_dir: Optional[str] = None):
        self.progression_recommender = ChordProgressionRecommender(data_dir)
        self.melody_recommender = MelodyRecommender(model_dir)
        self.lick_recommender = LickRecommender()

    def get_complete_recommendations(
        self,
        style: str,
        key: Optional[Note] = None,
        include_progressions: bool = True,
        include_melodies: bool = True,
        include_licks: bool = True
    ) -> Dict[str, List[Recommendation]]:
        """
        Get comprehensive recommendations including progressions, melodies, and licks

        Args:
            style: Musical style (prioritize neo_soul, blues, progressive_metal, rock_fusion)
            key: Optional key signature
            include_progressions: Whether to include progression recommendations
            include_melodies: Whether to include melody recommendations
            include_licks: Whether to include lick recommendations

        Returns:
            Dictionary with recommendation lists for each category
        """
        results = {}

        # Chord progressions
        if include_progressions:
            results['progressions'] = self.progression_recommender.recommend_progressions(
                style=style,
                key=key,
                num_recommendations=5
            )

        # Melodies (if we have a progression)
        if include_melodies and 'progressions' in results and results['progressions']:
            top_progression = results['progressions'][0].item
            results['melodies'] = self.melody_recommender.recommend_melodies(
                chord_progression=top_progression,
                num_variations=3
            )

        # Licks
        if include_licks and key:
            results['licks'] = self.lick_recommender.recommend_licks(
                style=style,
                key=key,
                num_recommendations=5
            )

        return results

    def get_priority_style_recommendations(
        self,
        key: Optional[Note] = None
    ) -> Dict[str, Dict[str, List[Recommendation]]]:
        """
        Get recommendations for all priority styles

        Returns:
            Nested dictionary: {style: {category: [recommendations]}}
        """
        all_recommendations = {}

        for style in self.PRIORITY_STYLES:
            all_recommendations[style] = self.get_complete_recommendations(
                style=style,
                key=key
            )

        return all_recommendations
