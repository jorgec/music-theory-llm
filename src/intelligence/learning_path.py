"""
Adaptive Learning Path Generator

Creates personalized learning pathways for music theory concepts,
adapts difficulty based on user performance, and tracks progress.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


class DifficultyLevel(Enum):
    """Difficulty levels for concepts and exercises"""
    BEGINNER = 1
    ELEMENTARY = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5


class ConceptCategory(Enum):
    """Categories of music theory concepts"""
    NOTES_INTERVALS = "notes_intervals"
    SCALES = "scales"
    CHORDS = "chords"
    PROGRESSIONS = "progressions"
    HARMONY = "harmony"
    MELODY = "melody"
    RHYTHM = "rhythm"
    VOICE_LEADING = "voice_leading"


@dataclass
class LearningConcept:
    """Represents a music theory concept to learn"""
    id: str
    name: str
    category: ConceptCategory
    difficulty: DifficultyLevel
    description: str
    prerequisites: List[str] = field(default_factory=list)  # IDs of prerequisite concepts
    skills: List[str] = field(default_factory=list)  # Skills gained
    examples: List[str] = field(default_factory=list)


@dataclass
class UserProgress:
    """Tracks user's learning progress"""
    user_id: str
    mastered_concepts: Dict[str, float] = field(default_factory=dict)  # concept_id -> mastery score (0-1)
    current_level: DifficultyLevel = DifficultyLevel.BEGINNER
    completed_exercises: List[str] = field(default_factory=list)
    performance_history: List[Dict] = field(default_factory=list)
    last_activity: Optional[datetime] = None
    total_study_time: int = 0  # minutes


class LearningPathGenerator:
    """
    Generates adaptive learning paths for music theory.

    Features:
    - Personalized curriculum based on skill level
    - Adaptive difficulty adjustment
    - Prerequisite tracking
    - Progress analytics
    - Recommended next concepts
    """

    def __init__(self):
        self.concepts = self._initialize_concepts()
        self.user_progress = {}

    def _initialize_concepts(self) -> Dict[str, LearningConcept]:
        """Initialize the curriculum of music theory concepts"""
        concepts = {}

        # Level 1: Beginner concepts
        concepts['notes_basic'] = LearningConcept(
            id='notes_basic',
            name='Musical Notes and the Chromatic Scale',
            category=ConceptCategory.NOTES_INTERVALS,
            difficulty=DifficultyLevel.BEGINNER,
            description='Learn the 12 notes of the chromatic scale, sharps and flats',
            prerequisites=[],
            skills=['identify_notes', 'use_accidentals'],
            examples=['C, C#/Db, D, D#/Eb...']
        )

        concepts['intervals_basic'] = LearningConcept(
            id='intervals_basic',
            name='Basic Intervals',
            category=ConceptCategory.NOTES_INTERVALS,
            difficulty=DifficultyLevel.BEGINNER,
            description='Learn intervals: unison, 2nd, 3rd, 4th, 5th, 6th, 7th, octave',
            prerequisites=['notes_basic'],
            skills=['identify_intervals', 'calculate_distance'],
            examples=['C to E = major 3rd', 'C to G = perfect 5th']
        )

        concepts['major_scale'] = LearningConcept(
            id='major_scale',
            name='Major Scale',
            category=ConceptCategory.SCALES,
            difficulty=DifficultyLevel.BEGINNER,
            description='Learn the major scale pattern (W-W-H-W-W-W-H)',
            prerequisites=['intervals_basic'],
            skills=['construct_major_scales', 'identify_scale_degrees'],
            examples=['C Major: C-D-E-F-G-A-B-C']
        )

        concepts['minor_scale'] = LearningConcept(
            id='minor_scale',
            name='Natural Minor Scale',
            category=ConceptCategory.SCALES,
            difficulty=DifficultyLevel.ELEMENTARY,
            description='Learn the natural minor scale and relative minors',
            prerequisites=['major_scale'],
            skills=['construct_minor_scales', 'find_relative_minors'],
            examples=['A Minor: A-B-C-D-E-F-G-A']
        )

        concepts['triads'] = LearningConcept(
            id='triads',
            name='Basic Triads',
            category=ConceptCategory.CHORDS,
            difficulty=DifficultyLevel.ELEMENTARY,
            description='Learn major, minor, diminished, and augmented triads',
            prerequisites=['intervals_basic', 'major_scale'],
            skills=['construct_triads', 'identify_chord_quality'],
            examples=['C major = C-E-G', 'A minor = A-C-E']
        )

        concepts['seventh_chords'] = LearningConcept(
            id='seventh_chords',
            name='Seventh Chords',
            category=ConceptCategory.CHORDS,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description='Learn maj7, min7, dom7, and diminished 7th chords',
            prerequisites=['triads'],
            skills=['construct_seventh_chords', 'identify_seventh_chords'],
            examples=['Cmaj7 = C-E-G-B', 'G7 = G-B-D-F']
        )

        concepts['diatonic_harmony'] = LearningConcept(
            id='diatonic_harmony',
            name='Diatonic Harmony',
            category=ConceptCategory.HARMONY,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description='Learn diatonic chords in major and minor keys',
            prerequisites=['major_scale', 'minor_scale', 'triads'],
            skills=['build_diatonic_chords', 'roman_numeral_analysis'],
            examples=['In C major: I=C, ii=Dm, iii=Em, IV=F, V=G, vi=Am, vii°=Bdim']
        )

        concepts['basic_progressions'] = LearningConcept(
            id='basic_progressions',
            name='Common Chord Progressions',
            category=ConceptCategory.PROGRESSIONS,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description='Learn common progressions like I-IV-V, I-V-vi-IV, ii-V-I',
            prerequisites=['diatonic_harmony'],
            skills=['create_progressions', 'analyze_progressions'],
            examples=['I-IV-V-I', 'I-V-vi-IV', 'ii-V-I']
        )

        concepts['harmonic_function'] = LearningConcept(
            id='harmonic_function',
            name='Harmonic Functions',
            category=ConceptCategory.HARMONY,
            difficulty=DifficultyLevel.ADVANCED,
            description='Learn tonic, subdominant, and dominant functions',
            prerequisites=['diatonic_harmony', 'basic_progressions'],
            skills=['identify_functions', 'use_functional_harmony'],
            examples=['T (I, vi), S (IV, ii), D (V, vii°)']
        )

        concepts['voice_leading_basic'] = LearningConcept(
            id='voice_leading_basic',
            name='Basic Voice Leading',
            category=ConceptCategory.VOICE_LEADING,
            difficulty=DifficultyLevel.ADVANCED,
            description='Learn smooth voice leading principles',
            prerequisites=['triads', 'basic_progressions'],
            skills=['voice_lead_chords', 'avoid_parallel_fifths'],
            examples=['Keep common tones, move other voices by step']
        )

        concepts['secondary_dominants'] = LearningConcept(
            id='secondary_dominants',
            name='Secondary Dominants',
            category=ConceptCategory.HARMONY,
            difficulty=DifficultyLevel.ADVANCED,
            description='Learn V/x chords - dominants of chords other than I',
            prerequisites=['seventh_chords', 'harmonic_function'],
            skills=['identify_secondary_dominants', 'use_tonicization'],
            examples=['V/V (D7 in key of C)', 'V/vi (E7 in key of C)']
        )

        concepts['modal_interchange'] = LearningConcept(
            id='modal_interchange',
            name='Modal Interchange',
            category=ConceptCategory.HARMONY,
            difficulty=DifficultyLevel.EXPERT,
            description='Learn borrowed chords from parallel modes',
            prerequisites=['diatonic_harmony', 'minor_scale'],
            skills=['identify_borrowed_chords', 'use_modal_mixture'],
            examples=['iv in major (from parallel minor)', 'bVII in major']
        )

        return concepts

    def get_learning_path(
        self,
        user_id: str,
        goal: Optional[str] = None
    ) -> List[LearningConcept]:
        """
        Generate personalized learning path for user.

        Args:
            user_id: User identifier
            goal: Optional specific goal (e.g., 'jazz_harmony', 'classical_theory')

        Returns:
            Ordered list of concepts to learn
        """
        # Get or create user progress
        if user_id not in self.user_progress:
            self.user_progress[user_id] = UserProgress(user_id=user_id)

        progress = self.user_progress[user_id]

        # Find concepts to learn
        available_concepts = []

        for concept_id, concept in self.concepts.items():
            # Skip if already mastered
            if progress.mastered_concepts.get(concept_id, 0) >= 0.8:
                continue

            # Check if prerequisites are met
            prereqs_met = all(
                progress.mastered_concepts.get(prereq_id, 0) >= 0.7
                for prereq_id in concept.prerequisites
            )

            if prereqs_met:
                available_concepts.append(concept)

        # Sort by difficulty and relevance
        available_concepts.sort(key=lambda c: (c.difficulty.value, c.id))

        return available_concepts

    def get_next_concept(self, user_id: str) -> Optional[LearningConcept]:
        """Get the next recommended concept to learn"""
        path = self.get_learning_path(user_id)
        return path[0] if path else None

    def record_performance(
        self,
        user_id: str,
        concept_id: str,
        score: float,  # 0-1
        exercise_type: str
    ):
        """
        Record user's performance on an exercise.

        Args:
            user_id: User identifier
            concept_id: Concept being practiced
            score: Performance score (0-1)
            exercise_type: Type of exercise
        """
        if user_id not in self.user_progress:
            self.user_progress[user_id] = UserProgress(user_id=user_id)

        progress = self.user_progress[user_id]

        # Update mastery (weighted average)
        current_mastery = progress.mastered_concepts.get(concept_id, 0)
        # Give more weight to recent performance
        new_mastery = current_mastery * 0.7 + score * 0.3
        progress.mastered_concepts[concept_id] = new_mastery

        # Record in history
        progress.performance_history.append({
            'timestamp': datetime.now().isoformat(),
            'concept_id': concept_id,
            'exercise_type': exercise_type,
            'score': score,
            'mastery_after': new_mastery
        })

        progress.last_activity = datetime.now()

        # Update level if appropriate
        self._update_user_level(progress)

    def _update_user_level(self, progress: UserProgress):
        """Update user's level based on mastered concepts"""
        # Count mastered concepts by difficulty
        mastered_by_level = {level: 0 for level in DifficultyLevel}

        for concept_id, mastery in progress.mastered_concepts.items():
            if mastery >= 0.8 and concept_id in self.concepts:
                difficulty = self.concepts[concept_id].difficulty
                mastered_by_level[difficulty] += 1

        # Determine appropriate level
        if mastered_by_level[DifficultyLevel.EXPERT] >= 3:
            progress.current_level = DifficultyLevel.EXPERT
        elif mastered_by_level[DifficultyLevel.ADVANCED] >= 4:
            progress.current_level = DifficultyLevel.ADVANCED
        elif mastered_by_level[DifficultyLevel.INTERMEDIATE] >= 5:
            progress.current_level = DifficultyLevel.INTERMEDIATE
        elif mastered_by_level[DifficultyLevel.ELEMENTARY] >= 4:
            progress.current_level = DifficultyLevel.ELEMENTARY
        else:
            progress.current_level = DifficultyLevel.BEGINNER

    def get_progress_report(self, user_id: str) -> Dict:
        """Generate comprehensive progress report"""
        if user_id not in self.user_progress:
            return {'error': 'User not found'}

        progress = self.user_progress[user_id]

        # Calculate statistics
        total_concepts = len(self.concepts)
        mastered_count = sum(1 for m in progress.mastered_concepts.values() if m >= 0.8)
        in_progress_count = sum(1 for m in progress.mastered_concepts.values() if 0.3 < m < 0.8)

        # Group by category
        category_progress = {}
        for concept_id, mastery in progress.mastered_concepts.items():
            if concept_id in self.concepts:
                category = self.concepts[concept_id].category.value
                if category not in category_progress:
                    category_progress[category] = {'mastered': 0, 'total': 0}
                category_progress[category]['total'] += 1
                if mastery >= 0.8:
                    category_progress[category]['mastered'] += 1

        # Recent activity
        recent_exercises = progress.performance_history[-10:] if progress.performance_history else []

        return {
            'user_id': user_id,
            'current_level': progress.current_level.name,
            'total_concepts': total_concepts,
            'mastered': mastered_count,
            'in_progress': in_progress_count,
            'completion_percentage': (mastered_count / total_concepts * 100),
            'category_progress': category_progress,
            'recent_activity': recent_exercises,
            'next_recommended': self.get_next_concept(user_id).name if self.get_next_concept(user_id) else None,
            'total_exercises': len(progress.completed_exercises),
            'study_time_minutes': progress.total_study_time
        }

    def save_progress(self, filepath: str):
        """Save all user progress to file"""
        data = {
            user_id: {
                'mastered_concepts': prog.mastered_concepts,
                'current_level': prog.current_level.name,
                'completed_exercises': prog.completed_exercises,
                'performance_history': prog.performance_history,
                'total_study_time': prog.total_study_time
            }
            for user_id, prog in self.user_progress.items()
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load_progress(self, filepath: str):
        """Load user progress from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        for user_id, prog_data in data.items():
            progress = UserProgress(user_id=user_id)
            progress.mastered_concepts = prog_data['mastered_concepts']
            progress.current_level = DifficultyLevel[prog_data['current_level']]
            progress.completed_exercises = prog_data['completed_exercises']
            progress.performance_history = prog_data['performance_history']
            progress.total_study_time = prog_data.get('total_study_time', 0)

            self.user_progress[user_id] = progress
