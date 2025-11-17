"""
Music Theory Explainer

Generates clear, educational explanations of music theory concepts,
analyses, and suggestions.
"""

from typing import Dict, List
from src.theory import Chord, ChordProgression, Scale


class TheoryExplainer:
    """Generates human-readable explanations of music theory"""

    def explain_chord(self, chord: Chord) -> str:
        """Explain a chord's structure and characteristics"""
        explanation = [f"**{chord}**"]

        # Notes
        notes = ', '.join(str(n) for n in chord.notes)
        explanation.append(f"Notes: {notes}")

        # Quality
        if chord.is_major():
            explanation.append("Quality: Major - bright, happy sound")
        elif chord.is_minor():
            explanation.append("Quality: Minor - darker, sadder sound")
        elif chord.is_diminished():
            explanation.append("Quality: Diminished - tense, unstable sound")
        elif chord.is_augmented():
            explanation.append("Quality: Augmented - mysterious, dreamy sound")

        # Intervals
        explanation.append(f"Intervals from root: {', '.join(str(i) for i in chord.get_intervals())}")

        return '\n'.join(explanation)

    def explain_progression(self, progression: ChordProgression) -> str:
        """Explain a chord progression"""
        explanation = []

        explanation.append(f"**Progression Analysis: {progression}**\n")

        if progression.scale:
            explanation.append(f"Key: {progression.scale.root} {progression.scale.scale_type.name}")

        if progression.roman_numerals:
            explanation.append(f"Roman numerals: {' - '.join(progression.roman_numerals)}")

        # Explain harmonic motion
        functions = progression.get_harmonic_functions()
        if functions:
            func_names = [f.value if f else '?' for f in functions]
            explanation.append(f"Harmonic functions: {' → '.join(func_names)}")
            explanation.append(self._explain_functional_motion(functions))

        # Cadence
        cadence = progression.get_cadence_type()
        if cadence:
            explanation.append(f"\nCadence: {cadence}")
            explanation.append(self._explain_cadence(cadence))

        return '\n'.join(explanation)

    def _explain_functional_motion(self, functions: List) -> str:
        """Explain the harmonic function progression"""
        from src.theory.progressions import HarmonicFunction

        explanations = {
            HarmonicFunction.TONIC: "stable, at rest",
            HarmonicFunction.SUBDOMINANT: "moving away from tonic, building tension",
            HarmonicFunction.DOMINANT: "maximum tension, wants to resolve to tonic"
        }

        parts = []
        for func in functions:
            if func in explanations:
                parts.append(f"{func.value} ({explanations[func]})")

        return "Motion: " + " → ".join(parts) if parts else ""

    def _explain_cadence(self, cadence: str) -> str:
        """Explain a cadence type"""
        explanations = {
            'authentic cadence': "Strong resolution from V to I - sounds complete and final",
            'plagal cadence': "IV to I - the 'Amen' cadence, gentle resolution",
            'half cadence': "Ends on V - creates a pause or question, not final",
            'deceptive cadence': "V to something other than I - surprises the listener"
        }

        return explanations.get(cadence, "")
