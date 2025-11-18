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
from .theory_explainer import MusicTheoryExplainer


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
        self.theory_explainer = MusicTheoryExplainer()

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
        if len(prog.chords) > 0:
            unique_chords = len(set(self._chord_to_key(c) for c in prog.chords))
            variety_score = unique_chords / len(prog.chords)
            score *= (0.5 + variety_score * 0.5)

        return min(score, 1.0)

    def _explain_progression(self, prog: ChordProgression, style: str) -> str:
        """Generate comprehensive music theory explanation for why this progression is recommended"""
        # Use the theory explainer for detailed analysis
        theory_explanation = self.theory_explainer.explain_progression(prog, style)
        return theory_explanation

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
        self.theory_explainer = MusicTheoryExplainer()

    def _build_lick_database(self) -> Dict[str, List[Dict]]:
        """Build database of style-specific licks"""
        licks = {
            'neo_soul': [
                {
                    'name': 'D\'Angelo Lick',
                    'intervals': [0, 2, 4, 5, 7, 5, 4, 2],  # Scale degrees
                    'rhythm': 'syncopated',
                    'description': 'Chromatic approach to chord tones with syncopation',
                    'techniques': ['syncopation', 'rhythmic displacement']
                },
                {
                    'name': 'Neo Soul Run',
                    'intervals': [0, 2, 3, 5, 7, 9, 11, 12],
                    'rhythm': 'flowing',
                    'description': 'Extended chord arpeggio with 9th and 11th',
                    'techniques': ['extended chords', 'smooth legato']
                },
                {
                    'name': 'Mateus Asato Chord Melody',
                    'intervals': [0, 4, 7, 11, 14, 11, 7, 4],  # maj9 arpeggio
                    'rhythm': 'ambient-textural',
                    'description': 'Asato\'s signature ambient chord melody with maj9 voicings',
                    'techniques': ['delay/reverb usage', 'volume swells', 'chord melody', 'maj9 voicings']
                },
                {
                    'name': 'Mateus Asato Pentatonic Extensions',
                    'intervals': [0, 2, 4, 7, 9, 11, 14, 16],
                    'rhythm': 'lyrical-spacious',
                    'description': 'Asato\'s extended pentatonic approach with added extensions',
                    'techniques': ['pentatonic extensions', 'tasteful bends', 'space/rests']
                },
                {
                    'name': 'Mateus Asato Dorian Vamp',
                    'intervals': [0, 2, 3, 5, 7, 10, 12, 14],
                    'rhythm': 'dorian-groove',
                    'description': 'Dorian mode phrase with characteristic Asato phrasing',
                    'techniques': ['dorian mode', 'rhythmic variety', 'clean tone']
                },
                {
                    'name': 'Lari Basilio Fusion Run',
                    'intervals': [0, 2, 4, 6, 7, 9, 11, 13, 14],
                    'rhythm': 'technical-fluid',
                    'description': 'Basilio\'s fluid technical runs combining jazz and soul',
                    'techniques': ['economy picking', 'string skipping', 'lydian mode']
                },
                {
                    'name': 'Lari Basilio Chord Stabs',
                    'intervals': [0, 4, 7, 11, 14, 18, 21],  # Extended voicings
                    'rhythm': 'rhythmic-percussive',
                    'description': 'Basilio\'s percussive chord stab approach with extensions',
                    'techniques': ['muted strumming', 'chord stabs', 'rhythmic precision']
                },
                {
                    'name': 'Lari Basilio Hybrid Picking Line',
                    'intervals': [0, 3, 5, 7, 10, 12, 15, 17],
                    'rhythm': 'hybrid-picking',
                    'description': 'Basilio\'s signature hybrid picking melodic lines',
                    'techniques': ['hybrid picking', 'dynamic control', 'articulation']
                },
                {
                    'name': 'Jack Gardiner Advanced Voicing Run',
                    'intervals': [0, 4, 7, 11, 14, 16, 19, 21],
                    'rhythm': 'sophisticated-melodic',
                    'description': 'Jack Gardiner\'s sophisticated chord voicing runs with jazz influence',
                    'techniques': ['advanced voicings', 'voice leading', 'jazz harmony', 'smooth legato']
                },
                {
                    'name': 'Jack Gardiner Pentatonic Sophistication',
                    'intervals': [0, 2, 4, 7, 9, 12, 14, 16, 19],
                    'rhythm': 'pentatonic-advanced',
                    'description': 'Gardiner\'s advanced pentatonic approach with extensions and chromatics',
                    'techniques': ['pentatonic mastery', 'chromatic embellishment', 'melodic development']
                },
                {
                    'name': 'Jack Gardiner Legato Flow',
                    'intervals': [0, 2, 4, 5, 7, 9, 11, 12, 14],
                    'rhythm': 'fluid-legato',
                    'description': 'Gardiner\'s smooth legato lines blending neo soul and fusion',
                    'techniques': ['legato technique', 'hammer-ons/pull-offs', 'fluid phrasing']
                },
                {
                    'name': 'Jack Gardiner Chord Melody Fusion',
                    'intervals': [0, 4, 7, 11, 14, 17, 21, 24],
                    'rhythm': 'chord-melody-jazz',
                    'description': 'Gardiner\'s jazz-influenced chord melody approach',
                    'techniques': ['chord melody', 'drop-2 voicings', 'jazz voicings', 'melodic continuity']
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
                {
                    'name': 'John Mayer Cascading Lick',
                    'intervals': [12, 10, 8, 7, 5, 3, 0, -2],
                    'rhythm': 'triplet-cascade',
                    'description': 'Signature Mayer cascading triplet run down the neck',
                    'techniques': ['triplet phrasing', 'position shifts', 'legato pull-offs']
                },
                {
                    'name': 'John Mayer Hendrix-Blues Hybrid',
                    'intervals': [0, 3, 5, 7, 8, 7, 5, 3],
                    'rhythm': 'soulful',
                    'description': 'Mayer-style blues with Hendrix influence, #5 interval',
                    'techniques': ['controlled feedback', 'thumb fretting', 'string bending']
                },
                {
                    'name': 'John Mayer Chord Melody Blues',
                    'intervals': [0, 7, 10, 14, 12, 10, 7, 5],  # Mixing chord tones with melody
                    'rhythm': 'rhythmic-stabs',
                    'description': 'Mayer signature mix of rhythm and lead in one phrase',
                    'techniques': ['hybrid picking', 'chord stabs', 'string damping']
                },
                {
                    'name': 'Josh Smith String Bending Run',
                    'intervals': [0, 3, 5, 5, 7, 8, 10, 10],  # Bend notes indicated by repeated values
                    'rhythm': 'smooth-sustained',
                    'description': 'Josh Smith signature controlled bends with perfect pitch',
                    'techniques': ['whole step bends', 'pre-bends', 'bend-and-release', 'sustain']
                },
                {
                    'name': 'Josh Smith Blues-Fusion Phrase',
                    'intervals': [0, 2, 3, 5, 7, 9, 10, 12],
                    'rhythm': 'jazz-blues-hybrid',
                    'description': 'Smith\'s blend of blues pentatonic with jazz chromaticism',
                    'techniques': ['finger vibrato', 'chromatic approach', 'clean articulation']
                },
                {
                    'name': 'Josh Smith Pentatonic Pivot',
                    'intervals': [0, 3, 5, 7, 10, 12, 10, 7, 5, 3],
                    'rhythm': 'pivoting',
                    'description': 'Pivoting around root note with pentatonic extensions',
                    'techniques': ['pivot note technique', 'dynamic control', 'fingerstyle blues']
                },
                {
                    'name': 'Eric Johnson Violin-Tone Bend',
                    'intervals': [0, 3, 5, 7, 8, 10, 12, 15],
                    'rhythm': 'lyrical-vocal',
                    'description': 'Eric Johnson signature violin-like sustained bends and tones',
                    'techniques': ['controlled bends', 'sustained notes', 'vocal-like phrasing', 'clean tone']
                },
                {
                    'name': 'Eric Johnson Pentatonic Cascades',
                    'intervals': [12, 10, 8, 7, 5, 3, 2, 0],
                    'rhythm': 'cascading-fluid',
                    'description': 'Johnson\'s cascading pentatonic runs down the neck',
                    'techniques': ['fluid legato', 'cascading runs', 'position shifts']
                },
                {
                    'name': 'Eric Johnson Chord-Melody Hybrid',
                    'intervals': [0, 4, 7, 10, 12, 16, 19, 22],
                    'rhythm': 'hybrid-melodic',
                    'description': 'Johnson\'s blend of chord tones and melodic lines',
                    'techniques': ['hybrid picking', 'chord tones', 'smooth transitions']
                },
                {
                    'name': 'Joe Bonamassa Power Blues Lick',
                    'intervals': [0, 3, 5, 7, 8, 10, 12, 15],
                    'rhythm': 'powerful-aggressive',
                    'description': 'Bonamassa\'s powerful blues-rock phrasing with authority',
                    'techniques': ['power bends', 'aggressive vibrato', 'high gain tone']
                },
                {
                    'name': 'Joe Bonamassa British Blues',
                    'intervals': [0, 3, 5, 6, 7, 10, 12, 15],
                    'rhythm': 'british-blues-rock',
                    'description': 'Bonamassa\'s British blues-rock influenced phrases (Clapton/Beck style)',
                    'techniques': ['woman tone', 'microtonal bends', 'sustain']
                },
                {
                    'name': 'Joe Bonamassa String Bending Masterclass',
                    'intervals': [0, 3, 5, 5, 7, 8, 8, 10, 12],  # Repeated = bends
                    'rhythm': 'expressive-dynamic',
                    'description': 'Bonamassa\'s masterful string bending with perfect intonation',
                    'techniques': ['precise bends', 'vibrato control', 'dynamics', 'phrasing']
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
                {
                    'name': 'Chick Corea Spanish Phrygian',
                    'intervals': [0, 1, 4, 5, 7, 8, 11, 12],
                    'rhythm': 'latin-jazz',
                    'description': 'Corea\'s Spanish-influenced Phrygian dominant phrase',
                    'techniques': ['staccato articulation', 'rhythmic displacement', 'latin feel']
                },
                {
                    'name': 'Chick Corea Crystal Silence',
                    'intervals': [0, 4, 7, 11, 14, 17, 21, 24],
                    'rhythm': 'ethereal',
                    'description': 'Corea\'s signature cascading arpeggios with extensions',
                    'techniques': ['arpeggio voicings', 'pedal point', 'cascading runs']
                },
                {
                    'name': 'Pat Metheny Wide Interval Jump',
                    'intervals': [0, 7, 12, 19, 16, 12, 7, 0],
                    'rhythm': 'melodic-lyrical',
                    'description': 'Metheny signature wide interval jumps with perfect voice leading',
                    'techniques': ['wide intervals', 'legato phrasing', 'sustain']
                },
                {
                    'name': 'Pat Metheny Bright Size Life',
                    'intervals': [0, 2, 4, 7, 9, 11, 14, 16],
                    'rhythm': 'bright-optimistic',
                    'description': 'Metheny\'s bright, optimistic major-based melodic lines',
                    'techniques': ['string-crossing', 'bright tone', 'clean articulation']
                },
                {
                    'name': 'Pat Metheny Modal Vamp',
                    'intervals': [0, 2, 5, 7, 10, 12, 10, 7, 5, 2],
                    'rhythm': 'modal-repetitive',
                    'description': 'Metheny\'s hypnotic modal vamps with subtle variations',
                    'techniques': ['modal playing', 'subtle dynamics', 'repetitive motifs']
                },
                {
                    'name': 'Allan Holdsworth Legato Run',
                    'intervals': [0, 4, 7, 11, 15, 18, 22, 25],
                    'rhythm': 'fluid-legato',
                    'description': 'Holdsworth\'s fluid legato lines across wide intervals',
                    'techniques': ['advanced legato', 'wide stretches', 'fluid phrasing']
                },
                {
                    'name': 'Allan Holdsworth SUS4 Voicing',
                    'intervals': [0, 5, 7, 12, 17, 19, 24],
                    'rhythm': 'suspended-ambiguous',
                    'description': 'Holdsworth\'s characteristic suspended and ambiguous harmonies',
                    'techniques': ['sus4 voicings', 'harmonic ambiguity', 'long phrases']
                },
                {
                    'name': 'Allan Holdsworth Chromatic Cascade',
                    'intervals': [0, 1, 2, 4, 5, 7, 8, 10, 11, 12],
                    'rhythm': 'chromatic-flowing',
                    'description': 'Holdsworth\'s signature chromatic approach with superimposed harmony',
                    'techniques': ['chromatic sequences', 'legato technique', 'advanced theory']
                },
            ],
            'progressive_metal': [
                {
                    'name': 'Lydian Shred',
                    'intervals': [0, 2, 4, 6, 7, 9, 11, 12],
                    'rhythm': 'fast',
                    'description': 'Lydian mode run with raised 4th',
                    'techniques': ['alternate picking', 'lydian mode']
                },
                {
                    'name': 'Phrygian Riff',
                    'intervals': [0, 1, 3, 5, 7, 8, 10, 12],
                    'rhythm': 'heavy',
                    'description': 'Phrygian dominant sound',
                    'techniques': ['palm muting', 'phrygian mode']
                },
                {
                    'name': 'Sweep Arpeggio',
                    'intervals': [0, 4, 7, 12, 16, 19],
                    'rhythm': 'sweeping',
                    'description': 'Extended arpeggio for sweep picking',
                    'techniques': ['sweep picking', 'economy motion']
                },
                {
                    'name': 'Intervals Polymetric Riff',
                    'intervals': [0, 2, 5, 7, 10, 12, 14, 17],
                    'rhythm': 'polymetric-djent',
                    'description': 'Intervals signature polymetric and polyrhythmic riffing',
                    'techniques': ['polymetric phrasing', 'tight palm muting', '7-string techniques']
                },
                {
                    'name': 'Intervals Harmonic Minor Shred',
                    'intervals': [0, 2, 3, 5, 7, 8, 11, 12],
                    'rhythm': 'neoclassical-shred',
                    'description': 'Intervals harmonic minor/Phrygian dominant runs',
                    'techniques': ['harmonic minor', 'string skipping', 'precision picking']
                },
                {
                    'name': 'Intervals Melodic Lead',
                    'intervals': [0, 4, 7, 11, 14, 16, 19, 21],
                    'rhythm': 'melodic-soaring',
                    'description': 'Intervals melodic lead lines with wide intervals',
                    'techniques': ['legato', 'wide intervals', 'sustain']
                },
                {
                    'name': 'Plini Hybrid Shred',
                    'intervals': [0, 2, 4, 6, 7, 9, 11, 14, 16],
                    'rhythm': 'technical-melodic',
                    'description': 'Plini\'s signature blend of technical playing with melody',
                    'techniques': ['hybrid picking', 'tapping', 'melodic phrasing']
                },
                {
                    'name': 'Plini Chord Voicing Lick',
                    'intervals': [0, 4, 7, 11, 14, 18, 21, 24],
                    'rhythm': 'chord-based-lead',
                    'description': 'Plini\'s sophisticated chord voicings in lead playing',
                    'techniques': ['chord voicings', 'clean articulation', 'jazz influence']
                },
                {
                    'name': 'Plini Cascading Tapping',
                    'intervals': [0, 5, 9, 12, 17, 21, 24, 28],
                    'rhythm': 'cascading-tap',
                    'description': 'Plini\'s signature cascading tapped arpeggios',
                    'techniques': ['two-hand tapping', 'cascading patterns', 'clean tone']
                },
                {
                    'name': 'I Built the Sky Ambient Tapping',
                    'intervals': [0, 7, 12, 16, 19, 24, 28, 31],
                    'rhythm': 'ambient-atmospheric',
                    'description': 'I Built the Sky\'s ethereal tapped arpeggios with delay and reverb',
                    'techniques': ['two-hand tapping', 'delay/reverb', 'clean tone', 'atmospheric']
                },
                {
                    'name': 'I Built the Sky Chord-Based Tapping',
                    'intervals': [0, 4, 7, 11, 14, 16, 19, 23],
                    'rhythm': 'chord-tap-melody',
                    'description': 'I Built the Sky\'s signature chord-based tapping patterns',
                    'techniques': ['chord tapping', 'right-hand melody', 'arpeggio voicings']
                },
                {
                    'name': 'I Built the Sky Wide Interval Melody',
                    'intervals': [0, 12, 7, 19, 4, 16, 11, 23],
                    'rhythm': 'melodic-wide-intervals',
                    'description': 'I Built the Sky\'s melodic lines with wide intervallic jumps',
                    'techniques': ['wide intervals', 'tapping', 'melodic construction', 'sustain']
                },
                {
                    'name': 'I Built the Sky Reverb Cascade',
                    'intervals': [0, 5, 9, 12, 17, 21, 24, 29, 33],
                    'rhythm': 'cascading-ambient',
                    'description': 'I Built the Sky\'s cascading patterns with heavy reverb/delay',
                    'techniques': ['cascading taps', 'delay trails', 'reverb wash', 'ambient']
                },
            ],
            'rock_fusion': [
                {
                    'name': 'Jazz-Rock Fusion Lick',
                    'intervals': [0, 2, 4, 6, 7, 6, 4, 2],
                    'rhythm': 'fusion',
                    'description': 'Mixolydian with chromatic approach',
                    'techniques': ['mixolydian mode', 'chromatic approach']
                },
                {
                    'name': 'Allan Holdsworth Style',
                    'intervals': [0, 3, 5, 7, 10, 12, 15],
                    'rhythm': 'legato',
                    'description': 'Wide interval jumps with legato',
                    'techniques': ['wide intervals', 'legato']
                },
                {
                    'name': 'Frank Gambale Sweep Economy',
                    'intervals': [0, 4, 7, 12, 16, 19, 24, 28],
                    'rhythm': 'sweep-economy',
                    'description': 'Gambale\'s signature sweep/economy picking technique across strings',
                    'techniques': ['sweep picking', 'economy picking', 'string crossing']
                },
                {
                    'name': 'Frank Gambale Superimposed Arpeggios',
                    'intervals': [0, 4, 8, 12, 16, 20, 24],  # Augmented arpeggio
                    'rhythm': 'superimposed',
                    'description': 'Gambale\'s superimposed arpeggio approach over chords',
                    'techniques': ['arpeggio superimposition', 'augmented arpeggios', 'advanced harmony']
                },
                {
                    'name': 'Frank Gambale Pentatonic Substitution',
                    'intervals': [0, 2, 4, 7, 9, 12, 14, 16],
                    'rhythm': 'pentatonic-advanced',
                    'description': 'Gambale\'s advanced pentatonic substitutions over complex changes',
                    'techniques': ['pentatonic substitutions', 'mode mixture', 'theory application']
                },
                {
                    'name': 'Greg Howe Legato Cascade',
                    'intervals': [0, 2, 4, 5, 7, 9, 11, 12, 14, 16],
                    'rhythm': 'fluid-legato',
                    'description': 'Greg Howe\'s signature fluid legato cascades with seamless phrasing',
                    'techniques': ['advanced legato', 'hammer-ons/pull-offs', 'smooth articulation', 'liquid phrasing']
                },
                {
                    'name': 'Greg Howe Two-Hand Tapping',
                    'intervals': [0, 5, 9, 12, 17, 21, 24, 29],
                    'rhythm': 'two-hand-tap',
                    'description': 'Howe\'s intricate two-hand tapping with wide intervallic leaps',
                    'techniques': ['two-hand tapping', 'wide intervals', 'right-hand tapping', 'symmetrical patterns']
                },
                {
                    'name': 'Greg Howe Chromatic Fusion',
                    'intervals': [0, 1, 2, 4, 5, 6, 7, 9, 10, 11, 12],
                    'rhythm': 'chromatic-technical',
                    'description': 'Howe\'s chromatic approach blending rock intensity with jazz sophistication',
                    'techniques': ['chromatic sequences', 'outside playing', 'tension/resolution']
                },
                {
                    'name': 'Greg Howe Sweep-Tap Hybrid',
                    'intervals': [0, 4, 7, 12, 16, 19, 24, 28, 31],
                    'rhythm': 'sweep-tap-hybrid',
                    'description': 'Howe\'s combination of sweep picking with tapped extensions',
                    'techniques': ['sweep picking', 'tapping', 'hybrid technique', 'arpeggio extensions']
                },
                {
                    'name': 'Greg Howe Modal Superimposition',
                    'intervals': [0, 2, 4, 6, 7, 9, 11, 13, 14],
                    'rhythm': 'modal-advanced',
                    'description': 'Howe\'s modal superimposition over chord changes',
                    'techniques': ['lydian mode', 'modal interchange', 'superimposition', 'harmonic sophistication']
                },
                {
                    'name': 'Greg Howe Intervallic Sequences',
                    'intervals': [0, 7, 2, 9, 4, 11, 7, 14],
                    'rhythm': 'intervallic-sequence',
                    'description': 'Howe\'s signature intervallic sequences creating wide melodic movement',
                    'techniques': ['interval skipping', 'sequence patterns', 'melodic development']
                },
                {
                    'name': 'Greg Howe Rock-Jazz Phrase',
                    'intervals': [0, 3, 5, 7, 10, 12, 15, 17],
                    'rhythm': 'rock-jazz-fusion',
                    'description': 'Howe\'s perfect blend of rock aggression with jazz vocabulary',
                    'techniques': ['blues-jazz fusion', 'aggressive vibrato', 'jazz phrasing', 'rock attitude']
                },
                {
                    'name': 'Guthrie Govan Modal Mastery',
                    'intervals': [0, 2, 4, 6, 7, 9, 11, 13, 14],
                    'rhythm': 'modal-sophisticated',
                    'description': 'Guthrie Govan\'s complete modal vocabulary across all modes',
                    'techniques': ['modal theory', 'lydian/dorian/phrygian', 'advanced theory', 'musical storytelling']
                },
                {
                    'name': 'Guthrie Govan Chromatic Lines',
                    'intervals': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    'rhythm': 'chromatic-fluid',
                    'description': 'Govan\'s signature chromatic approach with perfect voice leading',
                    'techniques': ['chromatic mastery', 'voice leading', 'tension/resolution', 'musical logic']
                },
                {
                    'name': 'Guthrie Govan Perfect Bends',
                    'intervals': [0, 3, 5, 5, 7, 8, 8, 10, 12],
                    'rhythm': 'expressive-vocal',
                    'description': 'Govan\'s perfectly controlled string bends with vocal-like expression',
                    'techniques': ['perfect pitch bends', 'microtonal control', 'vibrato mastery', 'expression']
                },
                {
                    'name': 'Guthrie Govan Hybrid Picking Mastery',
                    'intervals': [0, 4, 7, 9, 12, 16, 19, 21, 24],
                    'rhythm': 'hybrid-technical',
                    'description': 'Govan\'s flawless hybrid picking across all styles',
                    'techniques': ['hybrid picking excellence', 'pick + fingers', 'chicken picking', 'country fusion']
                },
                {
                    'name': 'Guthrie Govan Pentatonic Vocabulary',
                    'intervals': [0, 2, 4, 7, 9, 12, 14, 16, 19, 21],
                    'rhythm': 'pentatonic-masterclass',
                    'description': 'Govan\'s comprehensive pentatonic vocabulary with extensions',
                    'techniques': ['pentatonic mastery', 'extensions', 'superimposition', 'creative application']
                },
                {
                    'name': 'Guthrie Govan Arpeggio Sequences',
                    'intervals': [0, 4, 7, 12, 16, 19, 24, 28, 31],
                    'rhythm': 'arpeggio-technical',
                    'description': 'Govan\'s sophisticated arpeggio sequences with perfect technique',
                    'techniques': ['sweep picking', 'economy picking', 'legato arpeggios', 'technical precision']
                },
                {
                    'name': 'Guthrie Govan Altered Dominants',
                    'intervals': [0, 1, 3, 4, 6, 8, 10, 11, 12],
                    'rhythm': 'altered-jazz',
                    'description': 'Govan\'s jazz-influenced altered dominant phrases',
                    'techniques': ['altered scale', '7alt chords', 'jazz theory', 'outside playing']
                },
                {
                    'name': 'Guthrie Govan Country-Fusion',
                    'intervals': [0, 2, 4, 5, 7, 9, 11, 12],
                    'rhythm': 'country-fusion-blend',
                    'description': 'Govan\'s unique blend of country and fusion techniques',
                    'techniques': ['country licks', 'fusion vocabulary', 'hybrid picking', 'style blending']
                },
            ],
            'metalcore': [
                {
                    'name': 'Architects Breakdown Riff',
                    'intervals': [0, 0, 5, 5, 7, 7, 10, 10],  # Open string chugs
                    'rhythm': 'breakdown-syncopated',
                    'description': 'Architects signature breakdown with syncopated palm-muted chugs',
                    'techniques': ['palm muting', 'syncopation', 'drop tuning', 'breakdown']
                },
                {
                    'name': 'Architects Melodic Lead',
                    'intervals': [0, 3, 5, 8, 10, 12, 15, 17],
                    'rhythm': 'melodic-soaring',
                    'description': 'Architects melodic lead lines in minor key',
                    'techniques': ['melodic minor', 'sustain', 'emotional phrasing']
                },
                {
                    'name': 'Polaris Progressive Riff',
                    'intervals': [0, 2, 3, 5, 7, 10, 12, 14],
                    'rhythm': 'progressive-metalcore',
                    'description': 'Polaris blend of prog elements with metalcore aggression',
                    'techniques': ['odd-time signatures', 'complex rhythms', 'technical precision']
                },
                {
                    'name': 'Polaris Ambient Clean Section',
                    'intervals': [0, 4, 7, 11, 14, 17, 21],
                    'rhythm': 'ambient-clean',
                    'description': 'Polaris signature ambient clean passages with reverb',
                    'techniques': ['clean tone', 'reverb/delay', 'arpeggios', 'dynamics']
                },
                {
                    'name': 'Invent Animate Dissonant Chord',
                    'intervals': [0, 1, 5, 8, 11, 13, 17],  # Dissonant intervals
                    'rhythm': 'dissonant-atmospheric',
                    'description': 'Invent Animate signature dissonant chord voicings',
                    'techniques': ['dissonant harmony', 'suspended chords', 'atmospheric']
                },
                {
                    'name': 'Invent Animate Tapping Sequence',
                    'intervals': [0, 5, 8, 12, 17, 20, 24, 29],
                    'rhythm': 'ambient-tap',
                    'description': 'Invent Animate clean tapped sequences over atmospheric backing',
                    'techniques': ['two-hand tapping', 'clean tone', 'reverb usage']
                },
                {
                    'name': 'Modern Metalcore Djent Riff',
                    'intervals': [0, 0, 2, 2, 5, 5, 7, 7],
                    'rhythm': 'djent-polyrhythmic',
                    'description': 'Modern metalcore djent-style palm-muted syncopation',
                    'techniques': ['djent', 'polyrhythm', 'tight palm muting', '8-string guitar']
                },
            ],
            'soul': [
                {
                    'name': 'Motown Major 6th Lick',
                    'artist': 'Curtis Mayfield style',
                    'intervals': [0, 2, 3, 5, 7, 8, 9, 7, 5, 3, 2, 0],
                    'rhythm': '16ths',
                    'note_duration': 0.25,
                    'bpm': 95,
                    'description': 'Classic Motown soul lick emphasizing the major 6th. Features chromatic approach to the 6th (B via Bb) over Dm7. The 6th gives that characteristic soul sound. Chromatic passing tones create smooth voice leading back to the root.',
                    'chord_context': 'Dm7, Dm9',
                    'functional_harmony': 'ii chord in soul progression (ii-V-I or ii-V-IV)',
                    'target_notes': 'D (R), F (3rd), B (6th) - all on strong beats',
                    'techniques': ['chromatic approach', 'major 6th emphasis', 'smooth legato', 'vocal phrasing']
                },
                {
                    'name': 'Stax Double-Stop Soul Lick',
                    'artist': 'Steve Cropper / Booker T style',
                    'intervals': [0, 2, 4, 5, 7, 5, 4, 2, 1, 2, 4, 5, 7],
                    'rhythm': 'syncopated',
                    'note_duration': 0.25,
                    'bpm': 88,
                    'description': 'Stax-style soul lick with chromatic approach to the 3rd (E via Eb). Features typical Stax syncopation and double-stop phrasing. The chromatic descent (E-D-Db-D) creates tension and release. Works perfectly over C major or C7 in a I-IV soul groove.',
                    'chord_context': 'C, C7, Cmaj7',
                    'functional_harmony': 'I chord in soul/R&B progression',
                    'target_notes': 'C (R), E (3rd), G (5th)',
                    'techniques': ['double-stops', 'syncopation', 'chromatic descent', 'rhythmic displacement']
                },
                {
                    'name': 'Gospel Soul Run',
                    'artist': 'Al Green / Aretha Franklin style',
                    'intervals': [0, 1, 2, 4, 5, 7, 9, 10, 11, 12],
                    'rhythm': 'flowing',
                    'note_duration': 0.25,
                    'bpm': 72,
                    'description': 'Gospel-influenced soul run featuring multiple chromatic approaches. Chromatic motion from C to C# to D, then Bb to B. Creates emotional, church-like phrasing. Perfect for slow soul ballads or gospel-tinged R&B.',
                    'chord_context': 'C, Cmaj7, C6/9',
                    'functional_harmony': 'I chord resolution in gospel/soul cadence',
                    'target_notes': 'D (9th), E (3rd), B (7th)',
                    'techniques': ['chromatic approach', 'gospel phrasing', 'emotional bends', 'vibrato']
                },
                {
                    'name': 'Neo-Soul Chord Melody Fragment',
                    'artist': 'D\'Angelo / Erykah Badu style',
                    'intervals': [0, 4, 7, 11, 14, 13, 11, 9, 7, 6, 7, 4, 0],
                    'rhythm': 'laid-back',
                    'note_duration': 0.333,
                    'bpm': 78,
                    'description': 'Neo-soul chord melody line over Cmaj9. Emphasizes extensions (9th, 7th) with chromatic approach from 13th (A) down to 7th (B) via Bb. Features laid-back triplet feel characteristic of neo-soul. Chromatic descent from 7th to 5th via F# adds color.',
                    'chord_context': 'Cmaj9, Cmaj13',
                    'functional_harmony': 'Imaj9 in neo-soul progression',
                    'target_notes': 'B (7th), E (3rd), G (5th), D (9th)',
                    'techniques': ['chord melody', 'extensions', 'chromatic descent', 'triplet feel']
                },
            ],
            'funk': [
                {
                    'name': 'P-Funk Chromatic Slide Lick',
                    'artist': 'Eddie Hazel / George Clinton style',
                    'intervals': [0, 1, 2, 3, 5, 7, 8, 10, 12],
                    'rhythm': 'funky-16ths',
                    'note_duration': 0.25,
                    'bpm': 105,
                    'description': 'Classic P-Funk chromatic slide lick. Ascends chromatically from root through b2, 2, b3 before hitting the 4th. Creates funky, wah-wah-friendly texture. The chromatic climb (C-C#-D-Eb) adds grit and attitude typical of Parliament/Funkadelic style.',
                    'chord_context': 'C7, C9',
                    'functional_harmony': 'I7 in funk vamp',
                    'target_notes': 'C (R), F (4th), G (5th), C (octave)',
                    'techniques': ['chromatic slides', 'wah-wah', 'hammer-ons', 'funk rhythm']
                },
                {
                    'name': 'Tower of Power Style Horn Line',
                    'artist': 'Tower of Power horns',
                    'intervals': [0, 2, 4, 5, 7, 9, 11, 12, 11, 10, 9, 7],
                    'rhythm': 'tight-16ths',
                    'note_duration': 0.25,
                    'bpm': 112,
                    'description': 'Tower of Power-style horn line adapted for guitar. Ascending with chromatic approach (Bb) to the 7th (B), then chromatic descent back down. Tight, punchy phrasing with emphasis on rhythmic precision. Perfect for funk horn sections or single-note funk guitar.',
                    'chord_context': 'Cmaj7, C6/9',
                    'functional_harmony': 'Imaj7 in funk progression',
                    'target_notes': 'E (3rd), G (5th), B (7th), D (9th)',
                    'techniques': ['tight rhythm', 'chromatic approach', 'horn-style phrasing', 'staccato']
                },
                {
                    'name': 'Nile Rodgers Chromatic Funk Lick',
                    'artist': 'Nile Rodgers (Chic)',
                    'intervals': [0, 1, 2, 4, 5, 4, 2, 1, 0],
                    'rhythm': 'funky-16ths',
                    'note_duration': 0.25,
                    'bpm': 118,
                    'description': 'Nile Rodgers-style chromatic funk lick. Features chromatic motion between root and 3rd (C-C#-D-E-F-E-D-C#-C). Creates chicken-scratch funk vibe perfect for rhythm guitar. Chromatic embellishment of simple C major tonality.',
                    'chord_context': 'C, Csus2',
                    'functional_harmony': 'I chord funk vamp',
                    'target_notes': 'C (R), E (3rd) - emphasized on downbeats',
                    'techniques': ['chicken scratch', 'chromatic embellishment', 'muted strumming', 'tight rhythm']
                },
                {
                    'name': 'Modern Funk Chromatic Fill',
                    'artist': 'Vulfpeck / Cory Wong style',
                    'intervals': [7, 8, 9, 10, 12, 14, 15, 16, 14, 12, 10, 9, 7],
                    'rhythm': 'syncopated-16ths',
                    'note_duration': 0.25,
                    'bpm': 110,
                    'description': 'Modern funk chromatic fill starting from 5th (G). Chromatic ascent through Ab-A-Bb to root C, continues to D-Eb-E, then back down. Perfect for filling space between chord hits in modern funk. The chromatic motion adds sophistication to basic pentatonic framework.',
                    'chord_context': 'C7, C9, C13',
                    'functional_harmony': 'I7 or V7 in funk progression',
                    'target_notes': 'G (5th), C (R), E (3rd)',
                    'techniques': ['chromatic fills', 'syncopation', 'percussive muting', 'rhythmic displacement']
                },
            ],
            'pop_rock': [
                {
                    'name': '80s Power Ballad Lick',
                    'artist': 'Journey / Bon Jovi style',
                    'intervals': [0, 2, 4, 5, 7, 9, 11, 12, 11, 10, 9, 7, 5, 4, 2, 0],
                    'rhythm': 'legato',
                    'note_duration': 0.25,
                    'bpm': 82,
                    'description': '80s power ballad lick featuring chromatic passing tone (F/5) between E and G ascending, and chromatic descent (Bb) between B and A. Creates emotional, soaring quality typical of 80s arena rock. Perfect over I-V-vi-IV progression.',
                    'chord_context': 'C, G, Am, F (I-V-vi-IV)',
                    'functional_harmony': 'I chord in pop-rock progression',
                    'target_notes': 'C (R), E (3rd), G (5th), B (7th)',
                    'techniques': ['legato', 'chromatic passing tones', 'emotional bends', 'sustained notes']
                },
                {
                    'name': 'Van Halen Pop-Rock Run',
                    'artist': 'Eddie Van Halen (Jump, Panama era)',
                    'intervals': [0, 1, 2, 4, 7, 9, 12, 14, 13, 12, 9, 7, 4, 2, 1, 0],
                    'rhythm': 'fast-legato',
                    'note_duration': 0.125,
                    'bpm': 140,
                    'description': 'Eddie Van Halen-style pop-rock run combining pentatonic with chromatic approach tones. Features chromatic approach to 3rd (E via D#-D) and chromatic descent from 9th to root. Fast, flashy, but melodically accessible for pop-rock context.',
                    'chord_context': 'C, C major pentatonic',
                    'functional_harmony': 'I chord in pop-rock',
                    'target_notes': 'C (R), E (3rd), G (5th), D (9th)',
                    'techniques': ['tapping potential', 'legato', 'chromatic runs', 'flashy phrasing']
                },
                {
                    'name': 'The Edge Delay-Based Lick',
                    'artist': 'The Edge (U2)',
                    'intervals': [0, 4, 7, 11, 12, 11, 7, 4, 0],
                    'rhythm': 'delay-rhythm',
                    'note_duration': 0.5,
                    'bpm': 90,
                    'description': 'The Edge-style lick designed for dotted-eighth delay. Simple melodic content (Cmaj7 arpeggio) but creates complex texture with delay. No chromatic tones needed - the delay effect provides the sophistication. Works over atmospheric pop-rock progressions.',
                    'chord_context': 'Cmaj7, Cadd9',
                    'functional_harmony': 'I chord in ambient pop-rock',
                    'target_notes': 'C (R), E (3rd), G (5th), B (7th)',
                    'techniques': ['delay effects', 'arpeggios', 'ambient texture', 'minimal phrasing']
                },
                {
                    'name': 'Hair Metal Chromatic Shred',
                    'artist': 'Yngwie / Paul Gilbert pop-rock era',
                    'intervals': [0, 1, 2, 3, 4, 5, 7, 9, 11, 12, 11, 9, 7, 5, 4, 3, 2, 1, 0],
                    'rhythm': 'fast-alternate-picking',
                    'note_duration': 0.125,
                    'bpm': 145,
                    'description': 'Hair metal chromatic shred lick. Chromatic ascent from root through all semitones to 5th, then diatonic to octave, mirror descent. Flashy, technical, but resolves to safe pop-rock tonality. Perfect for 80s guitar hero solos over major chords.',
                    'chord_context': 'C major',
                    'functional_harmony': 'I chord shred section',
                    'target_notes': 'C (R), E (3rd), G (5th), C (octave)',
                    'techniques': ['alternate picking', 'chromatic runs', 'speed picking', 'sequential phrasing']
                },
            ],
            'pop': [
                {
                    'name': '90s Pop Radio Hook',
                    'artist': 'Backstreet Boys / NSYNC era',
                    'intervals': [0, 2, 4, 5, 7, 5, 4, 2, 1, 2, 0],
                    'rhythm': '16ths',
                    'note_duration': 0.25,
                    'bpm': 120,
                    'description': '90s pop hook featuring chromatic approach to 3rd (E via Eb). Ascending with chromatic passing tone (F) between E and G, descending with chromatic approach to root (C# to C). Catchy, memorable, perfect for chorus melodies.',
                    'chord_context': 'C, G, Am, F (I-V-vi-IV)',
                    'functional_harmony': 'I chord in pop progression',
                    'target_notes': 'C (R), E (3rd), G (5th) - all strong beats',
                    'techniques': ['memorable hook', 'chromatic passing tone', 'clean tone', 'compressed dynamics']
                },
                {
                    'name': '2000s R&B-Pop Lick',
                    'artist': 'Usher / Justin Timberlake era',
                    'intervals': [0, 2, 3, 4, 7, 9, 11, 12, 11, 10, 9, 7, 6, 7, 4, 3, 2, 0],
                    'rhythm': 'r&b-16ths',
                    'note_duration': 0.25,
                    'bpm': 98,
                    'description': '2000s R&B-influenced pop lick. Features chromatic approach to 3rd (E via D#-Eb), 6th emphasis (A via Bb-A), and chromatic fill around the 5th. Blends R&B sophistication with pop accessibility.',
                    'chord_context': 'Cmaj7, C6/9',
                    'functional_harmony': 'I chord in R&B-pop crossover',
                    'target_notes': 'E (3rd), A (6th), B (7th)',
                    'techniques': ['chromatic approach', 'R&B phrasing', 'syncopation', 'clean production']
                },
                {
                    'name': 'EDM-Pop Build Lick',
                    'artist': 'Calvin Harris / Zedd guitar style',
                    'intervals': [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24],
                    'rhythm': 'building',
                    'note_duration': 0.25,
                    'bpm': 128,
                    'description': 'EDM-pop build lick using pentatonic framework. Clean, repeatable pattern building energy toward drop. No chromatic tones - relies on repetition and production for impact. Perfect for pre-drop builds in electronic pop.',
                    'chord_context': 'C major pentatonic',
                    'functional_harmony': 'Build section before drop (I chord)',
                    'target_notes': 'C (R), E (3rd), G (5th) repeated at octaves',
                    'techniques': ['repetitive building', 'clean tone', 'production-oriented', 'pentatonic simplicity']
                },
                {
                    'name': 'Top 40 Radio-Friendly Solo',
                    'artist': 'Modern pop guitar (Maroon 5 style)',
                    'intervals': [0, 2, 4, 5, 7, 9, 11, 12, 11, 10, 9, 8, 7, 5, 4, 3, 2, 0],
                    'rhythm': '16ths',
                    'note_duration': 0.25,
                    'bpm': 115,
                    'description': 'Modern Top 40 guitar solo with just enough chromatic interest for sophistication while staying radio-friendly. Features chromatic descent from B (7th) through Bb-A-Ab to G (5th), and chromatic approach to 3rd (Eb-E). Melodic, not shreddy.',
                    'chord_context': 'C, Cmaj7',
                    'functional_harmony': 'I chord solo section',
                    'target_notes': 'C (R), E (3rd), G (5th), B (7th)',
                    'techniques': ['chromatic descent', 'melodic focus', 'radio-friendly', 'clean/compressed']
                },
            ],
            'rnb': [
                {
                    'name': 'Contemporary R&B Vocal-Style Run',
                    'artist': 'H.E.R. / Daniel Caesar style',
                    'intervals': [0, 1, 2, 4, 5, 7, 8, 9, 11, 12],
                    'rhythm': 'melismatic',
                    'note_duration': 0.25,
                    'bpm': 75,
                    'description': 'Contemporary R&B run mimicking vocal melismas. Chromatic approach to 3rd (C#-D-E) and to 7th (Ab-A-B). Creates smooth, vocal-like phrasing perfect for neo-soul/R&B guitar. Features laid-back timing and emotional delivery.',
                    'chord_context': 'Cmaj9, Cmaj13',
                    'functional_harmony': 'Imaj9 in R&B progression',
                    'target_notes': 'E (3rd), G (5th), B (7th), D (9th)',
                    'techniques': ['vocal-style phrasing', 'chromatic approach', 'melismatic runs', 'emotional delivery']
                },
                {
                    'name': 'Trap-Soul Guitar Lick',
                    'artist': 'Bryson Tiller / 6LACK style',
                    'intervals': [0, 2, 3, 5, 7, 8, 10, 12, 14, 13, 12, 10, 7, 5, 3, 2, 0],
                    'rhythm': 'trap-timing',
                    'note_duration': 0.333,
                    'bpm': 140,
                    'description': 'Trap-soul lick with minor pentatonic base + chromatic approaches. Features chromatic motion from 7th to octave (Bb-C-C#-C) creating modern R&B tension. Hi-hat-inspired timing with triplet subdivisions. Perfect for trap-influenced R&B productions.',
                    'chord_context': 'Cm7, Cm9',
                    'functional_harmony': 'i minor in trap-soul progression',
                    'target_notes': 'C (R), Eb (b3), G (5th), Bb (b7)',
                    'techniques': ['trap timing', 'chromatic approach', 'minor tonality', 'hi-hat rhythms']
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

            # Calculate score with decay, clamped to [0, 1] range
            score = max(0.0, min(1.0, 1.0 - (i * 0.15)))

            # Generate comprehensive theory explanation for this lick
            theory_explanation = self.theory_explainer.explain_lick(lick, key, style)

            # Combine basic description with theory explanation
            full_explanation = f"{lick['description']}\n\n{theory_explanation}"

            recommendations.append(Recommendation(
                item={
                    'name': lick['name'],
                    'intervals': lick['intervals'],
                    'transposed_notes': transposed,
                    'rhythm': lick['rhythm'],
                    'techniques': lick.get('techniques', [])
                },
                score=score,
                style=style,
                explanation=full_explanation,
                metadata={
                    'key': key.name,
                    'rhythm': lick['rhythm'],
                    'basic_description': lick['description'],
                    'theory_explanation': theory_explanation
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
