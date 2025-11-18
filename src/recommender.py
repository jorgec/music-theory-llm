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
                {
                    'name': 'Stacked Extensions Chord Melody',
                    'artist': 'Cory Wong / Tom Misch style',
                    'intervals': [0, 4, 7, 11, 14, 16, 19, 21, 23, 24, 21, 19, 17, 16, 14, 11, 9, 7, 4, 0],  # Stacked 9-11-13
                    'rhythm': 'neo-soul-chordal',
                    'note_duration': 0.333,
                    'bpm': 82,
                    'description': 'Sophisticated neo-soul chord melody featuring stacked extensions up to 13th. Ascends through Cmaj13 voicing: root-3rd-5th-7th-9th-11th-13th. Each extension adds harmonic color. Descending phrase uses chromatic voice leading through extensions. Creates lush, jazzy neo-soul texture. Essential vocabulary for contemporary soul guitar.',
                    'chord_context': 'Cmaj13, Cmaj9#11 (Imaj13 with all extensions)',
                    'functional_harmony': 'Imaj13 in neo-soul progression with complete upper structure',
                    'target_notes': 'B (7th), D (9th), F (11th), A (13th) - stacked extensions',
                    'techniques': ['chord melody', 'stacked extensions', 'upper structure voicings', 'chromatic voice leading', 'neo-soul harmony']
                },
                {
                    'name': 'Dorian Vamp with Chromatic Passing Tones',
                    'artist': 'Robert Glasper / Chris Dave style',
                    'intervals': [0, 2, 3, 4, 5, 7, 9, 10, 11, 12, 14, 15, 17, 16, 14, 12, 10, 9, 7, 5, 3, 2, 0],  # Dorian + chromatic
                    'rhythm': 'neo-soul-groove',
                    'note_duration': 0.25,
                    'bpm': 75,
                    'description': 'Hypnotic Dorian mode vamp with extensive chromatic passing tones. Features characteristic Dorian b7 and major 6th intervals with chromatic fills between scale degrees. Ascending: adds chromatic tones C#, Eb creating smooth voice leading. Descending: chromatic approach to each target note. Creates sophisticated modal neo-soul texture.',
                    'chord_context': 'Dm9, Dm11 (ii Dorian mode)',
                    'functional_harmony': 'ii Dorian vamp in neo-soul context',
                    'target_notes': 'D (R), F (b3), A (5th), C (b7), E (9th), G (11th)',
                    'techniques': ['dorian mode', 'chromatic passing tones', 'modal vamp', 'voice leading', 'neo-soul groove']
                },
                {
                    'name': 'Sus4 to Major Resolution with Extensions',
                    'artist': 'D\'Angelo / Isaiah Sharkey style',
                    'intervals': [0, 5, 7, 12, 14, 17, 16, 14, 11, 9, 7, 6, 7, 4, 0],  # Sus4 → maj resolution
                    'rhythm': 'neo-soul-resolution',
                    'note_duration': 0.25,
                    'bpm': 68,
                    'description': 'Characteristic neo-soul sus4 to major resolution with chromatic voice leading. Starts on sus4 chord tones (R-4th-5th) ascending to 11th extension. Resolution features chromatic descent from 11th through #9 and 9th before landing on maj3rd. Creates signature neo-soul tension-resolution sound.',
                    'chord_context': 'Csus4 → Cmaj9 (suspended resolution)',
                    'functional_harmony': 'Isus4 → Imaj9 (characteristic neo-soul resolution)',
                    'target_notes': 'F (4th sus), E (3rd resolution), B (7th), D (9th), F# (#9 chromatic)',
                    'techniques': ['sus4 chords', 'suspension resolution', 'chromatic voice leading', 'extended harmony', 'neo-soul phrasing']
                },
                {
                    'name': 'Altered Pentatonic with b6 and #9',
                    'artist': 'Steve Lacy / Anderson .Paak guitarist style',
                    'intervals': [0, 2, 3, 4, 5, 7, 8, 9, 11, 12, 14, 15, 17, 19, 20, 19, 17, 15, 14, 12, 10, 9, 7, 5, 3, 0],  # Altered pent
                    'rhythm': 'neo-soul-syncopated',
                    'note_duration': 0.25,
                    'bpm': 85,
                    'description': 'Modern altered pentatonic approach with b6 and #9 intervals. Combines minor pentatonic base with chromatic additions creating contemporary neo-soul sound. Features b6 (Ab) and #9 (Eb) intervals characteristic of R&B-influenced neo-soul. Extensive chromatic passing tones add sophistication. Ascending and descending with direction changes.',
                    'chord_context': 'Cm9, Cm11, Cm7#9 (i minor neo-soul)',
                    'functional_harmony': 'i minor with altered extensions in neo-soul context',
                    'target_notes': 'C (R), Eb (b3), G (5th), Bb (b7), D# (#9), Ab (b6)',
                    'techniques': ['altered pentatonic', 'b6 interval', '#9 extension', 'chromatic fills', 'neo-soul vocabulary']
                },
                {
                    'name': 'Quartal Voicing Arpeggio Run',
                    'artist': 'Thundercat / Louis Cole style',
                    'intervals': [0, 5, 10, 15, 17, 22, 24, 29, 31, 34, 36, 34, 31, 29, 27, 24, 22, 20, 17, 15, 10, 5, 0],  # Quartal voicings
                    'rhythm': 'neo-soul-modern',
                    'note_duration': 0.125,
                    'bpm': 90,
                    'description': 'Modern quartal voicing arpeggio featuring stacked 4ths. Builds Fmaj13#11 voicing in 4ths: C-F-Bb-E-A. Creates open, modern neo-soul/fusion sound. Ascending runs through quartal stacks spanning three octaves. Descending features chromatic passing tones between quartal chord tones. Contemporary harmony for progressive neo-soul.',
                    'chord_context': 'Fmaj13#11 (IVmaj13#11 quartal voicing)',
                    'functional_harmony': 'IVmaj13#11 with quartal voicing structure',
                    'target_notes': 'C (5th), F (R), Bb (4th/11th), E (maj7), A (3rd)',
                    'techniques': ['quartal harmony', 'stacked 4ths', 'modern voicings', 'three-octave range', 'contemporary neo-soul']
                },
                {
                    'name': 'Gospel Run with Sus-to-Major Resolution',
                    'artist': 'Kirk Franklin / PJ Morton guitar style',
                    'intervals': [0, 1, 2, 4, 5, 7, 9, 10, 11, 12, 14, 15, 16, 17, 14, 12, 10, 9, 7, 5, 4, 2, 0],  # Gospel chromatic
                    'rhythm': 'gospel-emotional',
                    'note_duration': 0.25,
                    'bpm': 70,
                    'description': 'Emotional gospel-influenced neo-soul run with extensive chromatic motion. Features multiple chromatic approaches to maj3rd, 5th, 7th, and 9th. Ascending phrase builds tension through chromatic passing tones before reaching 11th extension. Descending creates release through voice leading. Characteristic of gospel-tinged neo-soul ballads.',
                    'chord_context': 'Cmaj9, C6/9, Cmaj13 (I major with gospel influence)',
                    'functional_harmony': 'Imaj9/Imaj13 gospel resolution in neo-soul context',
                    'target_notes': 'E (3rd), G (5th), B (7th), D (9th), F (11th) - all with chromatic approaches',
                    'techniques': ['gospel phrasing', 'chromatic runs', 'emotional delivery', 'suspension resolution', 'neo-soul ballad']
                },
                {
                    'name': 'Pentatonic-Lydian Hybrid with #11',
                    'artist': 'Nate Smith / Mark Lettieri style',
                    'intervals': [0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 18, 19, 21, 23, 24, 23, 21, 18, 16, 14, 12, 11, 9, 7, 6, 4, 2, 0],  # Pent-Lydian
                    'rhythm': 'neo-soul-fusion',
                    'note_duration': 0.25,
                    'bpm': 95,
                    'description': 'Sophisticated hybrid of pentatonic and Lydian mode featuring #11 (F#). Combines major pentatonic framework with Lydian #4 creating bright, contemporary sound. Ascending emphasizes #11 interval before reaching extensions. Descending uses chromatic voice leading. Perfect for neo-soul and fusion contexts requiring sophistication.',
                    'chord_context': 'Cmaj9#11 (Imaj9 with Lydian #11)',
                    'functional_harmony': 'Imaj9#11 Lydian mode in neo-soul-fusion',
                    'target_notes': 'E (3rd), F# (#11), B (7th), D (9th), A (13th)',
                    'techniques': ['lydian mode', '#11 interval', 'pentatonic hybrid', 'bright sound', 'fusion vocabulary']
                },
                {
                    'name': 'Chromatic Chord Melody Cascade',
                    'artist': 'FKJ / Tom Misch style',
                    'intervals': [0, 4, 7, 11, 14, 13, 12, 11, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0],  # Chromatic cascade
                    'rhythm': 'neo-soul-intimate',
                    'note_duration': 0.333,
                    'bpm': 72,
                    'description': 'Intimate neo-soul chord melody featuring chromatic descending cascade. Starts on Cmaj9 chord tones ascending to 9th. Descending phrase moves chromatically through every semitone from 9th back to root. Creates lush, sophisticated texture characteristic of bedroom neo-soul. Each chromatic note implies different harmonic color.',
                    'chord_context': 'Cmaj9 → Cmaj9/B → Cmaj9/Bb → Cmaj9/A (chromatic bass motion)',
                    'functional_harmony': 'Imaj9 with chromatic bass line descent',
                    'target_notes': 'E (3rd), B (7th), D (9th), with chromatic bass motion',
                    'techniques': ['chord melody', 'chromatic descent', 'bass line motion', 'bedroom neo-soul', 'intimate phrasing']
                },
                {
                    'name': 'Modal Interchange Dorian-Mixolydian',
                    'artist': 'Robert Glasper Experiment style',
                    'intervals': [0, 2, 3, 5, 7, 9, 10, 12, 14, 16, 17, 19, 21, 22, 24, 22, 21, 19, 17, 14, 12, 10, 7, 5, 3, 0],  # Modal interchange
                    'rhythm': 'neo-soul-modal',
                    'note_duration': 0.25,
                    'bpm': 78,
                    'description': 'Advanced modal interchange line shifting between Dorian and Mixolydian modes. First half emphasizes Dorian b7 and b3 over Dm9. Second half shifts to D Mixolydian implying D7#9 with maj3rd and b7. Chromatic passing tones smooth the modal shift. Demonstrates sophisticated neo-soul harmonic vocabulary.',
                    'chord_context': 'Dm9 → D7#9 (Dorian → Mixolydian modal shift)',
                    'functional_harmony': 'ii Dorian → V7 Mixolydian (modal interchange)',
                    'target_notes': 'F (b3 Dorian), F# (maj3 Mixolydian), C (b7 both modes), E (9th)',
                    'techniques': ['modal interchange', 'dorian mode', 'mixolydian mode', 'chromatic transitions', 'advanced harmony']
                },
                {
                    'name': 'Neo-Soul Tritone Sub Approach',
                    'artist': 'Hiatus Kaiyote / Jordan Rakei style',
                    'intervals': [0, 1, 3, 4, 6, 7, 9, 11, 12, 13, 14, 16, 18, 19, 21, 23, 24],  # Tritone sub
                    'rhythm': 'neo-soul-sophisticated',
                    'note_duration': 0.25,
                    'bpm': 68,
                    'description': 'Sophisticated neo-soul line using tritone substitution harmony. Over Dm9, implies Ab9 (tritone sub of D7) creating outside harmonic color. Features altered scale intervals (b9, #9, #11) before resolving to Cmaj9. Chromatic voice leading throughout. Advanced reharmonization technique for progressive neo-soul.',
                    'chord_context': 'Dm9 (implying Ab9 tritone sub) → Cmaj9',
                    'functional_harmony': 'ii (with bVI9 tritone sub) → Imaj9',
                    'target_notes': 'Ab (tritone), Db (b5), Gb (b9 of D7), Cb (b13)',
                    'techniques': ['tritone substitution', 'altered harmony', 'reharmonization', 'chromatic voice leading', 'progressive neo-soul']
                },
                {
                    'name': 'Pedal Point Upper Extension Line',
                    'artist': 'Snarky Puppy / Cory Henry style',
                    'intervals': [0, 7, 11, 14, 17, 21, 0, 7, 10, 14, 16, 19, 0, 7, 9, 12, 16, 19, 0, 7, 11, 14, 17, 21],  # Pedal + extensions
                    'rhythm': 'neo-soul-pedal',
                    'note_duration': 0.5,
                    'bpm': 85,
                    'description': 'Modern pedal point technique with moving upper extensions. Root (C) stays constant while upper voice moves through different chord qualities: maj7-9-11-13, then min7-9-11, then maj9, returning to maj13. Creates shifting harmonic colors over static bass. Characteristic of modern neo-soul and gospel-jazz fusion.',
                    'chord_context': 'C pedal with Cmaj13 → Cm11 → Cmaj9 → Cmaj13 upper structure movement',
                    'functional_harmony': 'I pedal with moving upper structure chords',
                    'target_notes': 'Root pedal (C) constant, upper voice: B-D-F-A (7-9-11-13 moving)',
                    'techniques': ['pedal point', 'upper structure movement', 'chord quality shifts', 'modern neo-soul', 'gospel-jazz']
                },
                {
                    'name': 'Parallel 4ths Contemporary Run',
                    'artist': 'Jacob Collier / Louis Cole style',
                    'intervals': [0, 5, 2, 7, 4, 9, 7, 12, 9, 14, 12, 17, 14, 19, 17, 22, 19, 24, 22, 17, 14, 12, 9, 7, 4, 2, 0],  # Parallel 4ths
                    'rhythm': 'neo-soul-contemporary',
                    'note_duration': 0.125,
                    'bpm': 100,
                    'description': 'Ultra-contemporary parallel 4ths run creating modern neo-soul texture. Each note paired with its perfect 4th above, ascending through two octaves. Creates open, ambiguous harmony characteristic of progressive neo-soul. Descending phrase mirrors ascending with chromatic passing 4ths. Sophisticated vocabulary for contemporary contexts.',
                    'chord_context': 'Open quartal harmony (no specific chord, implying Cmaj9sus4)',
                    'functional_harmony': 'Quartal harmony texture in progressive neo-soul',
                    'target_notes': 'Perfect 4th intervals throughout: C-F, D-G, E-A, G-C, A-D, B-E',
                    'techniques': ['parallel 4ths', 'quartal harmony', 'contemporary texture', 'ambiguous tonality', 'progressive neo-soul']
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
                {
                    'name': 'Bebop Blues Turnaround with Enclosure',
                    'artist': 'Charlie Christian / Wes Montgomery style',
                    'intervals': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],  # Chromatic ascent
                    'rhythm': 'bebop-swing',
                    'note_duration': 0.25,
                    'bpm': 140,
                    'description': 'Advanced bebop blues turnaround featuring chromatic enclosure and guide tone line. Chromatic ascent from root to octave creates tension that resolves to I chord. Uses bebop approach with chromatic passing tones targeting 3rd (E) and 7th (B) of resolution chord. Essential vocabulary for playing through I-VI-ii-V-I changes.',
                    'chord_context': 'A7 → F#7 → Bm7 → E7 → Amaj7 (I-VI-ii-V-I turnaround)',
                    'functional_harmony': 'Complete turnaround progression in A with chromatic voice leading',
                    'target_notes': 'C# (3rd of A), E (5th), G# (7th), B (9th)',
                    'techniques': ['bebop scale', 'chromatic enclosure', 'guide tones', 'swing eighths', 'turnaround changes']
                },
                {
                    'name': 'Blues-Jazz Altered Dominant Line',
                    'artist': 'Larry Carlton / Robben Ford style',
                    'intervals': [0, 1, 3, 4, 6, 8, 9, 10, 11, 12, 14, 13, 12],  # Altered scale with chromatic
                    'rhythm': 'jazz-blues-fusion',
                    'note_duration': 0.25,
                    'bpm': 120,
                    'description': 'Sophisticated blues-jazz line over altered dominant (A7alt). Features b9, #9, and #11 intervals with chromatic approach tones. Ascending line emphasizes altered extensions before resolving chromatically to octave then 9th. Combines bebop chromaticism with blues vocabulary. Perfect for jazz-blues contexts.',
                    'chord_context': 'A7alt (A7b9#9#11), resolving to Dmaj7',
                    'functional_harmony': 'V7alt → Imaj7 in D major (blues-jazz resolution)',
                    'target_notes': 'C# (3rd), Eb (b5/#11), F# (13th), Bb (b9)',
                    'techniques': ['altered scale', 'chromatic approach', 'bebop phrasing', 'outside playing', 'tension-resolution']
                },
                {
                    'name': 'Minor Blues with 9th and 11th Extensions',
                    'artist': 'John Scofield / Mike Stern style',
                    'intervals': [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 14, 12, 10, 7, 5, 3, 2, 0],  # Minor with extensions
                    'rhythm': 'fusion-16ths',
                    'note_duration': 0.25,
                    'bpm': 110,
                    'description': 'Advanced minor blues line featuring 9th, 11th extensions with chromatic approaches. Ascends through Am pentatonic adding chromatic passing tones (Ab, Eb) before hitting extensions. Descending phrase uses chromatic voice leading back to root. Demonstrates sophisticated minor blues vocabulary beyond basic pentatonic.',
                    'chord_context': 'Am9, Am11 (i minor blues with extensions)',
                    'functional_harmony': 'i9/i11 in minor blues progression',
                    'target_notes': 'A (R), C (b3), E (5th), G (b7), B (9th), D (11th)',
                    'techniques': ['minor blues', 'extensions', 'chromatic approach', 'bebop vocabulary', 'direction changes']
                },
                {
                    'name': 'Blues Diminished Scale Run',
                    'artist': 'Pat Martino / George Benson style',
                    'intervals': [0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18],  # Whole-half diminished
                    'rhythm': 'fast-bebop',
                    'note_duration': 0.125,
                    'bpm': 160,
                    'description': 'Lightning-fast diminished scale run over dominant 7th chord. Uses whole-half diminished scale (C-C#-Eb-E-F#-G-A-Bb-C) with chromatic connections. Features symmetrical fingering patterns characteristic of diminished scales. Creates outside tension over A7 before resolving. Advanced vocabulary for bebop and jazz-blues.',
                    'chord_context': 'A7b9, Adim7 (dominant with diminished extensions)',
                    'functional_harmony': 'V7b9 with diminished superimposition',
                    'target_notes': 'C# (3rd), Eb (b5), G (b7), Bb (b9)',
                    'techniques': ['diminished scale', 'whole-half diminished', 'bebop runs', 'symmetrical patterns', 'fast alternate picking']
                },
                {
                    'name': 'Mixolydian Blues Hybrid with 13th',
                    'artist': 'Robben Ford / Scott Henderson style',
                    'intervals': [0, 2, 4, 5, 7, 9, 10, 11, 12, 14, 16, 17, 21, 19, 17, 14, 12],  # Mixolydian + blues
                    'rhythm': 'blues-fusion',
                    'note_duration': 0.25,
                    'bpm': 100,
                    'description': 'Sophisticated hybrid of Mixolydian mode and blues scale featuring 13th extension. Starts with Mixolydian intervals adding chromatic blue notes (Eb, Bb chromatic approaches). Ascends to 13th (F#) which is characteristic Mixolydian/#11 sound. Descending phrase emphasizes guide tones. Perfect for blues-fusion and jazz-rock.',
                    'chord_context': 'A9, A13 (dominant with 9th and 13th extensions)',
                    'functional_harmony': 'I9/I13 in blues-fusion context',
                    'target_notes': 'C# (3rd), G (b7), B (9th), F# (13th)',
                    'techniques': ['mixolydian mode', 'blues scale fusion', '13th extension', 'guide tone targeting', 'hybrid vocabulary']
                },
                {
                    'name': 'Advanced Double-Stop Blues Line',
                    'artist': 'Freddie King / Albert Collins style',
                    'intervals': [0, 1, 2, 3, 4, 5, 7, 9, 10, 11, 12, 14, 13, 12, 10, 7, 5, 3, 0],  # Chromatic double-stops
                    'rhythm': 'shuffle-double-stops',
                    'note_duration': 0.333,
                    'bpm': 85,
                    'description': 'Advanced double-stop blues line with extensive chromatic motion. Features chromatic ascent through tritone (C-C#-D-D#-E-F) before resolving to 5th (G). Descending phrase uses chromatic voice leading through 9th and 13th back to root. Double-stops should be played in 3rds or 6ths for authentic blues sound.',
                    'chord_context': 'A7, A9, A13 (I7 blues with double-stops)',
                    'functional_harmony': 'I7 blues shuffle with chromatic embellishment',
                    'target_notes': 'A (R), C# (3rd), E (5th), G (b7), B (9th), D (11th), F# (13th)',
                    'techniques': ['double-stops', 'chromatic motion', 'shuffle feel', 'parallel 6ths', 'tritone resolution']
                },
                {
                    'name': 'Bebop ii-V-I in Blues Context',
                    'artist': 'Grant Green / Kenny Burrell style',
                    'intervals': [0, 2, 3, 5, 7, 8, 9, 10, 11, 12, 14, 16, 17, 19, 21, 22, 24],  # ii-V-I line
                    'rhythm': 'bebop-walking',
                    'note_duration': 0.25,
                    'bpm': 130,
                    'description': 'Classic bebop ii-V-I line adapted for blues. Over Bm7: emphasizes 3rd and 7th guide tones with chromatic approach. Over E7: uses bebop dominant scale with chromatic passing tone between 7th and root. Over Amaj9: resolves to extensions (9th, 11th, 13th). Essential vocabulary for jazz-blues and playing the changes.',
                    'chord_context': 'Bm7 → E7 → Amaj9 (ii-V-I in A major)',
                    'functional_harmony': 'Complete ii-V-I progression with bebop chromaticism',
                    'target_notes': 'D (3rd of Bm7), A (7th of Bm7), G# (3rd of E7), D (7th of E7), C# (3rd of Amaj9)',
                    'techniques': ['bebop scale', 'ii-V-I', 'guide tones', 'chromatic approach', 'chord changes', 'voice leading']
                },
                {
                    'name': 'Bebop Enclosure Blues Lick',
                    'artist': 'Charlie Parker blues vocabulary',
                    'intervals': [0, 1, 2, 4, 3, 5, 6, 7, 9, 8, 10, 11, 12, 14, 13, 15, 14, 12],  # Multiple enclosures
                    'rhythm': 'bebop-enclosure',
                    'note_duration': 0.25,
                    'bpm': 150,
                    'description': 'Advanced bebop enclosure technique over blues changes. Features multiple chromatic enclosures: surrounds 3rd (E via D-F-E), 5th (G via F#-Ab-G), and octave (A via G#-Bb-A). Each target note approached from above and below chromatically. Creates sophisticated melodic tension. Essential bebop vocabulary for blues and jazz.',
                    'chord_context': 'A7, A9 (I7 blues with bebop approach)',
                    'functional_harmony': 'I7 blues with bebop enclosure technique',
                    'target_notes': 'E (5th), G (b7), A (R), B (9th) - all with chromatic enclosures',
                    'techniques': ['bebop enclosure', 'chromatic approach from above and below', 'target note resolution', 'bebop articulation']
                },
                {
                    'name': 'Blues Tritone Substitution Line',
                    'artist': 'Joe Pass / Herb Ellis style',
                    'intervals': [0, 2, 4, 6, 7, 9, 11, 13, 14, 15, 16, 18, 19, 21, 22, 24],  # Tritone sub approach
                    'rhythm': 'jazz-blues-sophisticated',
                    'note_duration': 0.25,
                    'bpm': 110,
                    'description': 'Sophisticated blues line using tritone substitution. Over A7, implies Eb7 (tritone sub of A7) creating outside sound. Ascends through Eb major scale with chromatic passing tones before resolving to D chord. Features lydian #11 sound and chromatic voice leading. Advanced harmonic concept for jazz-blues.',
                    'chord_context': 'A7 (implying Eb7 tritone sub) → Dmaj7',
                    'functional_harmony': 'bII7 → I (tritone substitution in blues)',
                    'target_notes': 'G (maj3 of Eb7 = b7 of A7), Bb (5th of Eb7 = b9 of A7), Db (7th of Eb7 = #9 of A7)',
                    'techniques': ['tritone substitution', 'lydian dominant', 'chromatic voice leading', 'outside playing', 'reharmonization']
                },
                {
                    'name': 'Extended Pentatonic Blues-Rock Line',
                    'artist': 'Derek Trucks / Warren Haynes style',
                    'intervals': [0, 2, 3, 5, 7, 9, 10, 12, 14, 15, 17, 19, 21, 22, 24, 26, 24, 22, 19, 17, 14, 12],  # Extended pent
                    'rhythm': 'blues-rock-melodic',
                    'note_duration': 0.25,
                    'bpm': 95,
                    'description': 'Extended pentatonic blues-rock line spanning two octaves with chromatic embellishments. Starts with minor pentatonic adding chromatic approaches to 5th (Bb-B), 7th (G-Ab-G), and 9th (Eb-E). Reaches high extensions (9th, 11th, 13th two octaves up) before cascading descent. Combines blues-rock and jazz vocabulary.',
                    'chord_context': 'Am7, Am9, Am11 (i minor blues-rock)',
                    'functional_harmony': 'i minor blues-rock with extended range',
                    'target_notes': 'A (R), C (b3), E (5th), G (b7), B (9th), D (11th), F# (13th - mixolydian)',
                    'techniques': ['extended pentatonic', 'two-octave range', 'chromatic embellishment', 'cascading descent', 'wide interval jumps']
                },
                {
                    'name': 'Dominant 7#9 Hendrix Chord Lick',
                    'artist': 'Jimi Hendrix / Stevie Ray Vaughan style',
                    'intervals': [0, 1, 3, 4, 7, 8, 10, 11, 12, 13, 15, 14, 12, 10, 7, 4, 3, 1, 0],  # 7#9 chord tones
                    'rhythm': 'hendrix-blues-rock',
                    'note_duration': 0.25,
                    'bpm': 88,
                    'description': 'Signature Hendrix 7#9 chord lick with chromatic approaches. Features #9 (C/Bb#) interval creating Hendrix chord sound. Chromatic motion from b9 to #9 (Bb-B-C) adds bluesy tension. Ascending phrase emphasizes #9 before chromatic descent resolves to root. Essential vocabulary for blues-rock and R&B.',
                    'chord_context': 'A7#9 (Hendrix chord: A-C#-E-G-C)',
                    'functional_harmony': 'I7#9 Hendrix chord in blues-rock context',
                    'target_notes': 'A (R), C# (3rd), G (b7), Bb (b9), C (##9/#9)',
                    'techniques': ['7#9 chord', 'Hendrix chord', 'chromatic approach', 'blues-rock vocabulary', 'R&B influence']
                },
                {
                    'name': 'Jazz-Blues Walking Bass Chord Melody',
                    'artist': 'Joe Pass / Wes Montgomery style',
                    'intervals': [0, 2, 4, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24, 26, 28, 29, 31, 33, 36],  # Walking bass chord melody
                    'rhythm': 'walking-bass-melody',
                    'note_duration': 0.5,
                    'bpm': 100,
                    'description': 'Advanced jazz-blues chord melody line with walking bass movement. Combines bass line (root movement through changes) with melodic upper voice featuring extensions. Each chord tone voiced with 9th, 11th, or 13th above. Creates full harmonic texture in single-note line. Essential vocabulary for solo jazz-blues guitar.',
                    'chord_context': 'A9 → D9 → A9 → E9 (I-IV-I-V blues changes)',
                    'functional_harmony': 'Complete 12-bar blues changes with walking bass approach',
                    'target_notes': 'Walking roots: A → D → A → E, with 9ths, 11ths, 13ths voiced above',
                    'techniques': ['walking bass', 'chord melody', 'voice leading', 'extended chords', 'chord-scale relationships']
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
                {
                    'name': 'Coltrane Changes Giant Steps Pattern',
                    'artist': 'John Coltrane style',
                    'intervals': [0, 4, 7, 11, 14, 16, 18, 21, 23, 25, 27, 30, 32, 34, 36, 32, 30, 27, 25, 23, 21, 18, 16, 14, 11, 7, 4, 0],  # Coltrane changes
                    'rhythm': 'coltrane-changes',
                    'note_duration': 0.125,
                    'bpm': 180,
                    'description': 'Advanced Coltrane changes line navigating Giant Steps progression. Features rapid key center modulation through major 3rds: C-E-Ab-C. Each key center outlined with maj7 arpeggio before chromatic connection to next center. Demonstrates Coltrane\'s approach to navigating complex harmonic movement. Advanced bebop-post-bop vocabulary.',
                    'chord_context': 'Cmaj7 → Emaj7 → Abmaj7 → Cmaj7 (Coltrane changes in major 3rds)',
                    'functional_harmony': 'Major 3rd modulation cycle (Coltrane changes)',
                    'target_notes': 'Each maj7 arpeggio: C-E-G-B, E-G#-B-D#, Ab-C-Eb-G, C-E-G-B',
                    'techniques': ['coltrane changes', 'giant steps', 'rapid modulation', 'major 3rd cycles', 'post-bop vocabulary']
                },
                {
                    'name': 'Shorter Modal Jazz with Ambiguous Tonality',
                    'artist': 'Wayne Shorter style',
                    'intervals': [0, 1, 3, 5, 6, 8, 10, 11, 12, 14, 15, 17, 18, 20, 22, 23, 24, 22, 20, 18, 15, 14, 12, 10, 8, 6, 5, 3, 1, 0],  # Modal ambiguity
                    'rhythm': 'shorter-modal',
                    'note_duration': 0.25,
                    'bpm': 140,
                    'description': 'Wayne Shorter signature modal line with ambiguous tonality. Combines multiple modes (Dorian, Locrian, Phrygian) creating harmonic ambiguity. Features chromatic voice leading between modal areas. Creates Shorter\'s characteristic mysterious, questing sound. Advanced modal jazz vocabulary with intervallic leaps.',
                    'chord_context': 'Modal ambiguity: Cm7 (Dorian) → C° (Locrian) implications',
                    'functional_harmony': 'Modal jazz with intentional harmonic ambiguity',
                    'target_notes': 'Multiple modal implications through chromatic voice leading',
                    'techniques': ['modal jazz', 'ambiguous tonality', 'multiple modes', 'chromatic connections', 'intervallic leaps']
                },
                {
                    'name': 'Hancock Altered Dominant with Tritone Sub',
                    'artist': 'Herbie Hancock style',
                    'intervals': [0, 1, 3, 4, 6, 8, 9, 10, 11, 12, 13, 14, 16, 18, 19, 21, 22, 24, 22, 21, 19, 18, 16, 14, 12, 10, 8, 6, 4, 3, 1, 0],  # Altered + tritone
                    'rhythm': 'hancock-altered',
                    'note_duration': 0.25,
                    'bpm': 135,
                    'description': 'Herbie Hancock sophisticated altered dominant line with tritone substitution implications. Features complete altered scale (melodic minor 7th mode) with chromatic enclosures. Implies both C7alt and Gb7 (tritone sub) simultaneously. Ascending emphasizes all altered tensions (b9, #9, #11, b13) before chromatic descent.',
                    'chord_context': 'C7alt / Gb7 (altered dominant with tritone sub implications)',
                    'functional_harmony': 'V7alt with tritone substitution ambiguity',
                    'target_notes': 'Db (b9), D# (#9), F# (#11), Ab (b13), Bb (b7)',
                    'techniques': ['altered scale', 'tritone substitution', 'chromatic enclosures', 'reharmonization', 'modern jazz']
                },
                {
                    'name': 'Metheny Wide Interval Lyrical Line',
                    'artist': 'Pat Metheny style',
                    'intervals': [0, 7, 12, 19, 24, 28, 31, 36, 40, 43, 48, 43, 40, 36, 31, 28, 24, 19, 16, 12, 7, 0],  # Wide intervals
                    'rhythm': 'metheny-lyrical',
                    'note_duration': 0.5,
                    'bpm': 100,
                    'description': 'Pat Metheny signature wide interval lyrical line spanning four octaves. Features perfect 5ths, octaves, and extended voicings creating open, singing quality. Each interval leap carefully voice-led despite wide spacing. Creates Metheny\'s characteristic optimistic, soaring sound. Requires exceptional legato and sustain control.',
                    'chord_context': 'Cmaj9, Cmaj13 (open voicings across range)',
                    'functional_harmony': 'Imaj9/Imaj13 with wide interval voice leading',
                    'target_notes': 'Perfect 5ths and octaves: C-G, G-C, C-G across four octaves',
                    'techniques': ['wide intervals', 'lyrical phrasing', 'perfect legato', 'sustained notes', 'voice leading across octaves']
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
                {
                    'name': 'Abasi Thumping with Extended Intervals',
                    'artist': 'Tosin Abasi (Animals as Leaders) style',
                    'intervals': [0, 5, 12, 17, 19, 24, 29, 31, 36, 41, 43, 48, 43, 41, 36, 31, 29, 24, 19, 17, 12, 5, 0],  # Wide thumping
                    'rhythm': 'abasi-thumping',
                    'note_duration': 0.125,
                    'bpm': 100,
                    'description': 'Tosin Abasi signature thumping technique combining tapped harmonics and thumb slaps. Features perfect 5ths and octaves across wide range spanning four octaves. Thumping creates percussive attacks while maintaining melodic content. Requires extended-range 8-string guitar. Creates Abasi\'s signature ambient yet aggressive texture.',
                    'chord_context': 'Open quartal voicings (C-G-C-G pattern across octaves)',
                    'functional_harmony': 'Quartal harmony with wide spacing (progressive metal texture)',
                    'target_notes': 'Perfect 5ths (C-G) across four octaves with thumped harmonics',
                    'techniques': ['thumping', 'tapped harmonics', 'wide intervals', '8-string guitar', 'percussive attacks']
                },
                {
                    'name': 'Plini Ambient Multi-Octave Tapping',
                    'artist': 'Plini style',
                    'intervals': [0, 7, 12, 16, 19, 24, 28, 31, 36, 40, 43, 48, 43, 40, 36, 31, 28, 24, 19, 16, 12, 7, 0],  # Tapping cascade
                    'rhythm': 'plini-ambient-tap',
                    'note_duration': 0.125,
                    'bpm': 90,
                    'description': 'Plini signature ambient tapping cascade spanning four octaves. Features maj7 and 9th intervals tapped with extensive delay and reverb. Creates cascading waterfall effect characteristic of Plini\'s sound. Ascending emphasizes extensions (7th, 9th, 11th) before apex. Requires clean tone with ambient effects.',
                    'chord_context': 'Cmaj9, Cmaj13 (ambient progressive voicings)',
                    'functional_harmony': 'Imaj9/Imaj13 with ambient texture',
                    'target_notes': 'G (5th), B (7th), D (9th), F (11th), A (13th) - cascading',
                    'techniques': ['two-hand tapping', 'ambient effects', 'delay/reverb', 'cascade patterns', 'melodic tapping']
                },
                {
                    'name': 'Intervals Polymetric Djent Pattern',
                    'artist': 'Intervals (Aaron Marshall) style',
                    'intervals': [0, 2, 5, 7, 10, 12, 14, 17, 19, 22, 24, 26, 29, 31, 34, 36, 34, 31, 29, 26, 24, 22, 19, 17, 14, 12, 10, 7, 5, 2, 0],  # Polymetric
                    'rhythm': 'polymetric-djent',
                    'note_duration': 0.125,
                    'bpm': 145,
                    'description': 'Intervals signature polymetric djent pattern in 7/8 over 4/4 feel. Features tight palm-muted riffing with melodic intervals (2nds, 4ths, 5ths) creating rhythmic displacement. Combines technical precision with melodic sensibility. Ascending phrase builds tension through polymetric phrasing before aggressive descent.',
                    'chord_context': 'C5, C power chord with extensions (prog-djent)',
                    'functional_harmony': 'I power chord with polymetric rhythmic concept',
                    'target_notes': 'C (R), D (9th), F (4th), G (5th), Bb (b7) - polymetric accents',
                    'techniques': ['polymetric', 'djent', '7-string technique', 'tight palm muting', 'rhythmic displacement']
                },
                {
                    'name': 'Periphery Lydian Dominant Shred',
                    'artist': 'Periphery (Misha Mansoor / Mark Holcomb) style',
                    'intervals': [0, 2, 4, 6, 7, 9, 10, 12, 14, 16, 18, 19, 21, 22, 24, 26, 28, 30, 31, 33, 34, 36],  # Lydian dominant
                    'rhythm': 'periphery-shred',
                    'note_duration': 0.0625,
                    'bpm': 155,
                    'description': 'Periphery-style lydian dominant shred line featuring #11 and chromatic approach tones. Combines speed with harmonic sophistication: lydian #4 over dominant chord creates bright yet aggressive sound. Chromatic passing tones add fluidity. Ascending through three octaves with #11 emphasized. Characteristic djent-prog vocabulary.',
                    'chord_context': 'C7#11 (lydian dominant / melodic minor 4th mode)',
                    'functional_harmony': 'V7#11 lydian dominant in progressive context',
                    'target_notes': 'E (3rd), F# (#11), Bb (b7), D (9th)',
                    'techniques': ['lydian dominant', '#11 interval', 'speed picking', 'chromatic fluidity', 'djent-prog hybrid']
                },
                {
                    'name': 'Meshuggah Polyrhythmic Mechanized Riff',
                    'artist': 'Meshuggah style',
                    'intervals': [0, 0, 2, 2, 5, 5, 7, 7, 10, 10, 12, 12, 14, 14, 17, 17, 19, 19, 22, 22, 24, 24],  # Mechanized
                    'rhythm': 'meshuggah-polyrhythm',
                    'note_duration': 0.125,
                    'bpm': 80,  # Feels much faster due to polyrhythm
                    'description': 'Meshuggah-style mechanized polyrhythmic riff in 23/16 over 4/4. Features repeated staccato notes creating machine-like precision. Intervals ascend in minor 3rds (C-Eb-F#-A) through two octaves. Extreme rhythmic complexity with mechanical execution. Demonstrates Meshuggah\'s approach to polyrhythmic riff construction.',
                    'chord_context': 'C5, C diminished implications (polyrhythmic riff)',
                    'functional_harmony': 'Polyrhythmic riff over static harmony',
                    'target_notes': 'C (R), Eb (b3), F# (#4/b5), A (6th) - mechanized pattern',
                    'techniques': ['extreme polyrhythm', 'machine precision', 'staccato palm muting', '8-string djent', 'rhythmic complexity']
                },
                {
                    'name': 'Gojira Harmonic Minor Death Riff',
                    'artist': 'Gojira (Joe Duplantier) style',
                    'intervals': [0, 2, 3, 5, 7, 8, 11, 12, 14, 15, 17, 19, 20, 23, 24, 23, 20, 19, 17, 15, 14, 12, 11, 8, 7, 5, 3, 2, 0],  # Harmonic minor
                    'rhythm': 'gojira-brutal',
                    'note_duration': 0.125,
                    'bpm': 140,
                    'description': 'Gojira-style harmonic minor brutality featuring characteristic raised 7th. Combines death metal aggression with progressive harmonic sophistication. Features harmonic minor scale (C-D-Eb-F-G-Ab-B) with chromatic passing tones. Ascending emphasizes augmented 2nd interval (Ab-B) before brutal descent. Heavy palm-muted execution.',
                    'chord_context': 'Cm(maj7), Cm with harmonic minor implications',
                    'functional_harmony': 'i harmonic minor in progressive death metal',
                    'target_notes': 'C (R), Eb (b3), Ab (b6), B (maj7) - harmonic minor characteristic tones',
                    'techniques': ['harmonic minor', 'death metal brutality', 'palm muting', 'augmented 2nd interval', 'progressive death']
                },
                {
                    'name': 'Petrucci Neoclassical Harmonic Minor Sweep',
                    'artist': 'John Petrucci (Dream Theater) style',
                    'intervals': [0, 2, 3, 5, 7, 8, 11, 12, 14, 15, 17, 19, 20, 23, 24, 26, 27, 29, 31, 32, 35, 36, 35, 32, 31, 29, 27, 26, 24, 23, 20, 19, 17, 15, 14, 12, 11, 8, 7, 5, 3, 2, 0],  # Neoclassical
                    'rhythm': 'petrucci-neoclassical',
                    'note_duration': 0.0625,
                    'bpm': 165,
                    'description': 'Petrucci signature neoclassical harmonic minor sweep through three octaves. Features classical-influenced harmonic minor scale (Yngwie-meets-prog-metal) with sweep-picked arpeggios at each octave. Ascending emphasizes harmonic minor intervals before reaching three-octave apex. Descending mirrors with perfect symmetry. Technical progressive mastery.',
                    'chord_context': 'Cm(maj7), C harmonic minor scale with classical voicings',
                    'functional_harmony': 'i harmonic minor neoclassical in prog-metal context',
                    'target_notes': 'C (R), Eb (b3), G (5th), B (maj7), Ab (b6) - neoclassical emphasis',
                    'techniques': ['neoclassical', 'sweep picking', 'harmonic minor', 'three-octave range', 'symmetrical phrasing']
                },
                {
                    'name': 'Sithu Aye Melodic Progressive Line',
                    'artist': 'Sithu Aye style',
                    'intervals': [0, 4, 7, 11, 14, 16, 19, 21, 23, 24, 28, 31, 33, 35, 36, 33, 31, 28, 24, 21, 19, 16, 14, 11, 7, 4, 0],  # Melodic prog
                    'rhythm': 'melodic-prog-metal',
                    'note_duration': 0.125,
                    'bpm': 130,
                    'description': 'Sithu Aye melodic progressive line featuring maj7 and 9th intervals with uplifting quality. Combines djent rhythmic precision with optimistic melodic content. Features cascading maj7 arpeggios through three octaves with ambient feel. Ascending emphasizes bright extensions before melodic descent. Modern melodic progressive metal vocabulary.',
                    'chord_context': 'Cmaj9, Cmaj13 (melodic progressive metal)',
                    'functional_harmony': 'Imaj9/Imaj13 with uplifting melodic character',
                    'target_notes': 'E (3rd), B (7th), D (9th), F (11th), A (13th) - bright, melodic',
                    'techniques': ['melodic prog', 'bright voicings', 'cascading arpeggios', 'ambient meets heavy', 'modern progressive']
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
                {
                    'name': 'Holdsworth Legato with b9 and #11',
                    'artist': 'Allan Holdsworth style',
                    'intervals': [0, 1, 3, 5, 6, 8, 10, 12, 13, 15, 17, 18, 20, 22, 24, 22, 20, 17, 15, 13, 12, 10, 8, 6, 3, 1, 0],  # Altered fusion
                    'rhythm': 'fluid-legato-fusion',
                    'note_duration': 0.125,
                    'bpm': 160,
                    'description': 'Advanced Holdsworth-style legato line featuring altered intervals b9, #9, #11. Fluid legato technique with chromatic voice leading through altered dominant scale. Wide stretches and unconventional fingerings create Holdsworth\'s signature liquid sound. Ascending emphasizes altered tensions before chromatic descent resolves. Essential advanced fusion vocabulary.',
                    'chord_context': 'C7alt (C7b9#9#11), Cmin/maj7 (altered dominant to tonic minor)',
                    'functional_harmony': 'V7alt with complete altered scale (melodic minor 7th mode)',
                    'target_notes': 'Db (b9), D# (#9), F# (#11), Bb (b7)',
                    'techniques': ['advanced legato', 'wide stretches', 'altered dominant scale', 'chromatic voice leading', 'Holdsworth phrasing']
                },
                {
                    'name': 'Gambale Extended Arpeggio Sweep',
                    'artist': 'Frank Gambale style',
                    'intervals': [0, 4, 7, 11, 14, 16, 19, 21, 23, 24, 28, 31, 33, 35, 36, 33, 31, 28, 24, 21, 19, 16, 14, 11, 7, 4, 0],  # Extended sweep
                    'rhythm': 'economy-sweep-fusion',
                    'note_duration': 0.0625,
                    'bpm': 140,
                    'description': 'Lightning-fast economy/sweep picking through extended Cmaj13 arpeggio spanning three octaves. Features Gambale\'s signature economy motion with extensions (7th, 9th, 11th, 13th) voiced across strings. Ascending sweep emphasizes each extension before three-octave apex. Descending mirrors with economy picking efficiency. Technical fusion masterclass.',
                    'chord_context': 'Cmaj13, Cmaj9#11 (Imaj13 extended arpeggio)',
                    'functional_harmony': 'Imaj13 with complete upper structure (7-9-11-13)',
                    'target_notes': 'B (7th), D (9th), F (11th), A (13th) - all swept across three octaves',
                    'techniques': ['economy picking', 'sweep picking', 'three-octave arpeggios', 'extended voicings', 'speed technique']
                },
                {
                    'name': 'Howe Lydian-Locrian Superimposition',
                    'artist': 'Greg Howe style',
                    'intervals': [0, 2, 4, 6, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],  # Modal superimposition
                    'rhythm': 'fusion-superimposition',
                    'note_duration': 0.125,
                    'bpm': 145,
                    'description': 'Advanced modal superimposition technique: Lydian mode over major chord transitioning to Locrian over diminished. Features #11 (Lydian) transitioning to chromatically ascending Locrian intervals. Creates inside-outside harmonic tension characteristic of Howe\'s vocabulary. Chromatic bridge connects modal areas.',
                    'chord_context': 'Cmaj7#11 → C°7 (Lydian → Locrian superimposition)',
                    'functional_harmony': 'I Lydian → I diminished (modal reharmonization)',
                    'target_notes': 'F# (#11 Lydian), Gb (b5 Locrian), Db (b9), Ab (b6)',
                    'techniques': ['modal superimposition', 'lydian mode', 'locrian mode', 'chromatic transitions', 'outside playing']
                },
                {
                    'name': 'Govan Complete Chromatic Voice Leading',
                    'artist': 'Guthrie Govan style',
                    'intervals': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0],  # Complete chromatic
                    'rhythm': 'govan-chromatic-fusion',
                    'note_duration': 0.0625,
                    'bpm': 130,
                    'description': 'Govan\'s masterful complete chromatic voice leading through two octaves. Every semitone touched ascending and descending with perfect evenness and articulation. Creates maximum chromatic tension before resolution. Demonstrates Govan\'s approach to chromatic vocabulary as melodic tool rather than technical exercise. Requires impeccable technique and musicality.',
                    'chord_context': 'C chromatic (implies C7alt → Cmaj7 tension-resolution)',
                    'functional_harmony': 'Complete chromatic scale as tension device',
                    'target_notes': 'All 12 chromatic notes emphasized equally with resolution to C',
                    'techniques': ['complete chromaticism', 'perfect articulation', 'chromatic voice leading', 'musical tension', 'technical mastery']
                },
                {
                    'name': 'Lane Pentatonic Sequences with Chromatic Insertions',
                    'artist': 'Shawn Lane style',
                    'intervals': [0, 2, 4, 5, 7, 9, 11, 12, 14, 13, 12, 10, 9, 11, 7, 8, 7, 5, 4, 6, 2, 3, 2, 0],  # Pentatonic sequences + chromatic
                    'rhythm': 'lane-technical-fusion',
                    'note_duration': 0.0625,
                    'bpm': 180,
                    'description': 'Lightning-fast Shawn Lane-style pentatonic sequences with chromatic insertions. Features sequential patterns with chromatic neighbor tones between pentatonic notes. Creates Lane\'s signature combination of speed and melodic content. Chromatic insertions add sophistication to otherwise simple pentatonic framework. Extreme technical demands.',
                    'chord_context': 'C major pentatonic with chromatic embellishments',
                    'functional_harmony': 'I major pentatonic with chromatic sophistication',
                    'target_notes': 'C (R), E (3rd), G (5th) - pentatonic framework with chromatic neighbors',
                    'techniques': ['extreme speed', 'pentatonic sequences', 'chromatic insertions', 'sequential patterns', 'technical virtuosity']
                },
                {
                    'name': 'Krantz Angular Intervallic Approach',
                    'artist': 'Wayne Krantz style',
                    'intervals': [0, 7, 1, 9, 3, 11, 5, 14, 8, 17, 10, 19, 12, 21, 15, 24, 18, 22, 14, 17, 10, 12, 5, 7, 0],  # Wide intervals
                    'rhythm': 'krantz-angular-fusion',
                    'note_duration': 0.125,
                    'bpm': 110,
                    'description': 'Wayne Krantz\'s angular intervallic approach featuring wide, unexpected leaps. Combines perfect 5ths, major 7ths, and chromatic intervals in non-traditional sequences. Creates jagged, unpredictable melodic contour characteristic of Krantz. Challenging conventional melodic motion while maintaining harmonic coherence. Advanced modern fusion vocabulary.',
                    'chord_context': 'Cmaj9, C7alt (ambiguous tonality with wide intervals)',
                    'functional_harmony': 'Modal/tonal ambiguity with intervallic focus',
                    'target_notes': 'Wide intervallic relationships: 5ths, 7ths, 9ths, 11ths - non-sequential',
                    'techniques': ['wide intervals', 'angular melody', 'intervallic approach', 'modern fusion', 'unpredictable phrasing']
                },
                {
                    'name': 'Henderson Blues-Fusion with Altered Extensions',
                    'artist': 'Scott Henderson style',
                    'intervals': [0, 1, 3, 4, 6, 7, 9, 10, 11, 12, 14, 15, 17, 18, 19, 21, 22, 24, 22, 21, 19, 17, 14, 12, 10, 7, 4, 3, 1, 0],  # Blues-fusion altered
                    'rhythm': 'henderson-blues-fusion',
                    'note_duration': 0.125,
                    'bpm': 125,
                    'description': 'Scott Henderson signature blues-fusion line combining blues vocabulary with altered jazz harmony. Features b9, #9, #11 over dominant chord while maintaining blues feel. Chromatic approach tones throughout create sophisticated blues-jazz hybrid. Ascending emphasizes altered tensions, descending resolves through blues scale. Perfect blend of traditions.',
                    'chord_context': 'C7#9#11, C7alt (blues-fusion altered dominant)',
                    'functional_harmony': 'I7alt in blues-fusion context (blues meets jazz)',
                    'target_notes': 'Db (b9), Eb (#9), F# (#11), Bb (b7)',
                    'techniques': ['blues-fusion', 'altered harmony', 'chromatic approach', 'hybrid vocabulary', 'Henderson phrasing']
                },
                {
                    'name': 'Stern Outside-Inside Chromatic Approach',
                    'artist': 'Mike Stern style',
                    'intervals': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 19, 21, 24, 22, 19, 17, 14, 12, 10, 7, 5, 3, 0],  # Outside-inside
                    'rhythm': 'stern-fusion-aggressive',
                    'note_duration': 0.125,
                    'bpm': 135,
                    'description': 'Mike Stern\'s characteristic outside-inside approach: complete chromatic ascent (outside) resolving to clear chord tones (inside). Chromatic buildup creates intense tension before resolving to pentatonic/arpeggio descent. Demonstrates Stern\'s approach to chromatic vocabulary with strong resolution. Aggressive fusion articulation.',
                    'chord_context': 'C7alt → Cmaj7 (outside tension → inside resolution)',
                    'functional_harmony': 'Chromatic outside playing resolving to inside harmony',
                    'target_notes': 'Complete chromatic (outside) → C-E-G-B-D-G (inside pentatonic)',
                    'techniques': ['outside-inside', 'chromatic tension', 'strong resolution', 'aggressive articulation', 'fusion vocabulary']
                },
                {
                    'name': 'McLaughlin Melodic Minor Fusion Run',
                    'artist': 'John McLaughlin style',
                    'intervals': [0, 2, 3, 5, 7, 9, 11, 12, 14, 15, 17, 19, 21, 23, 24, 26, 27, 29, 31, 33, 35, 36, 33, 31, 29, 26, 24, 21, 19, 17, 14, 12, 9, 7, 5, 3, 2, 0],  # Melodic minor
                    'rhythm': 'mclaughlin-speed-fusion',
                    'note_duration': 0.0625,
                    'bpm': 170,
                    'description': 'John McLaughlin blazing melodic minor run spanning three octaves. Features C melodic minor ascending with chromatic passing tones at octave transitions. Demonstrates McLaughlin\'s combination of Indian classical scales with jazz vocabulary. Requires exceptional speed and accuracy. Characteristic Mahavishnu Orchestra fusion vocabulary.',
                    'chord_context': 'Cm/maj7, Cm/maj9 (melodic minor harmony)',
                    'functional_harmony': 'i melodic minor with extended range',
                    'target_notes': 'C (R), Eb (b3), G (5th), B (maj7), D (9th)',
                    'techniques': ['melodic minor', 'three-octave runs', 'extreme speed', 'Indian classical influence', 'fusion mastery']
                },
                {
                    'name': 'Henderson/Willis Polyrhythmic Fusion',
                    'artist': 'Tribal Tech style',
                    'intervals': [0, 3, 5, 7, 10, 12, 15, 17, 19, 22, 24, 27, 29, 31, 34, 36, 34, 31, 29, 26, 24, 22, 19, 17, 14, 12, 10, 7, 5, 3, 0],  # Polyrhythmic
                    'rhythm': 'tribal-tech-polyrhythm',
                    'note_duration': 0.166,  # Quintuplets
                    'bpm': 115,
                    'description': 'Tribal Tech-style polyrhythmic fusion line in quintuplets over 4/4. Features minor pentatonic with chromatic extensions creating rhythmic displacement. Accents fall on unconventional beats creating polyrhythmic feel. Demonstrates Henderson/Willis approach to combining rhythmic and melodic sophistication. Advanced fusion rhythm concept.',
                    'chord_context': 'Cm9, Cm11 (i minor fusion)',
                    'functional_harmony': 'i minor with polyrhythmic subdivision',
                    'target_notes': 'C (R), Eb (b3), G (5th), Bb (b7), D (9th), F (11th)',
                    'techniques': ['polyrhythm', 'quintuplets', 'rhythmic displacement', 'minor pentatonic + extensions', 'tribal tech style']
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
            List of lick recommendations with transposed intervals, sorted by quality
        """
        if style not in self.lick_database:
            return []

        # Sort licks by quality (prioritize advanced licks)
        def lick_quality_score(lick):
            score = 0
            # Prefer licks with chord context (advanced)
            if 'chord_context' in lick and lick['chord_context']:
                score += 100
            # Prefer licks with target notes specified
            if 'target_notes' in lick and lick['target_notes']:
                score += 50
            # Prefer licks with functional harmony
            if 'functional_harmony' in lick and lick['functional_harmony']:
                score += 50
            # Prefer longer, more complex licks
            score += len(lick['intervals']) * 2
            # Prefer licks with more unique intervals (complexity)
            score += len(set(lick['intervals'])) * 3
            return score

        # Sort licks by quality score (highest first)
        sorted_licks = sorted(self.lick_database[style], key=lick_quality_score, reverse=True)
        recommendations = []

        for i, lick in enumerate(sorted_licks[:num_recommendations]):
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
