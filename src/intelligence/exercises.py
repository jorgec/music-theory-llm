"""Exercise Generator - Creates interactive music theory exercises"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import random
from src.theory import Note, Chord, Scale, ChordProgression, chord_from_scale_degree


@dataclass
class Exercise:
    """An exercise with question and answer"""
    id: str
    concept: str
    difficulty: int
    question: str
    correct_answer: str
    options: Optional[List[str]] = None  # For multiple choice
    explanation: str = ""


class ExerciseGenerator:
    """Generates practice exercises for music theory concepts"""

    def generate_interval_exercise(self, difficulty: int = 1) -> Exercise:
        """Generate interval identification exercise"""
        notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        note1 = Note.from_string(random.choice(notes))
        interval = random.choice([2, 4, 7, 5] if difficulty <= 2 else [1, 3, 6, 8, 10])
        note2 = note1.transpose(interval)

        interval_names = {2: 'major 2nd', 4: 'major 3rd', 7: 'perfect 5th', 5: 'perfect 4th',
                         1: 'minor 2nd', 3: 'minor 3rd', 6: 'tritone'}

        return Exercise(
            id=f"interval_{random.randint(1000,9999)}",
            concept="intervals",
            difficulty=difficulty,
            question=f"What is the interval from {note1} to {note2}?",
            correct_answer=interval_names.get(interval, f"{interval} semitones"),
            options=list(interval_names.values()) if difficulty <= 2 else None,
            explanation=f"Count {interval} semitones from {note1} to reach {note2}"
        )

    def generate_chord_identification_exercise(self, difficulty: int = 2) -> Exercise:
        """Generate chord identification exercise"""
        roots = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        root = random.choice(roots)

        if difficulty <= 2:
            qualities = ['major', 'minor']
            symbols = ['', 'm']
        else:
            qualities = ['major', 'minor', 'dominant 7th', 'major 7th']
            symbols = ['', 'm', '7', 'maj7']

        idx = random.randint(0, len(qualities)-1)
        quality = qualities[idx]
        symbol = symbols[idx]

        chord = Chord.from_symbol(f"{root}{symbol}")
        notes = ', '.join(str(n) for n in chord.notes)

        return Exercise(
            id=f"chord_{random.randint(1000,9999)}",
            concept="chord_identification",
            difficulty=difficulty,
            question=f"What chord has the notes: {notes}?",
            correct_answer=f"{root}{symbol}",
            options=[f"{root}{s}" for s in symbols],
            explanation=f"These notes form a {quality} chord"
        )

    def generate_progression_exercise(self, difficulty: int = 3) -> Exercise:
        """Generate progression analysis exercise"""
        scale = Scale.major(Note.from_string(random.choice(['C', 'G', 'D', 'F'])))
        degrees = [1, 4, 5, 1] if difficulty <= 2 else [1, 6, 4, 5]
        prog = ChordProgression.from_degrees(degrees, scale)

        chord_str = ' - '.join(str(c) for c in prog.chords)
        roman = ' - '.join(prog.roman_numerals)

        return Exercise(
            id=f"prog_{random.randint(1000,9999)}",
            concept="progression_analysis",
            difficulty=difficulty,
            question=f"Analyze this progression in {scale.root} major: {chord_str}",
            correct_answer=roman,
            explanation=f"In {scale.root} major, the Roman numeral analysis is {roman}"
        )
