"""
Comprehensive Intelligence Features Demo

Demonstrates all advanced intelligence features:
- Rule validation and scoring
- Intelligent evaluation and ranking
- Statistical progression analysis
- Neural network prediction
- ML-based lick generation
- Adaptive learning paths
- Theory explanations
- Interactive exercises
- Feedback collection
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.theory import Note, Chord, Scale, ChordProgression, Pitch
from src.intelligence import (
    MusicTheoryValidator, IntelligentEvaluator,
    NeuralChordPredictor, LearningPathGenerator,
    TheoryExplainer, ExerciseGenerator,
    FeedbackSystem, ModelImprover
)
from src.intelligence.statistical_analyzer import StatisticalProgressionAnalyzer
from src.intelligence.lick_generator import NeuralLickGenerator
from src.utils import MelodySuggester, HarmonicAnalyzer


def demo_validation_and_scoring():
    """Demonstrate music theory validation"""
    print("=" * 80)
    print("MUSIC THEORY VALIDATION & SCORING")
    print("=" * 80)
    print()

    validator = MusicTheoryValidator(strictness="moderate")

    # Example 1: Validate a melody
    melody = [
        Pitch.from_string('C4'),
        Pitch.from_string('E4'),
        Pitch.from_string('G4'),
        Pitch.from_string('C5'),  # Large leap
        Pitch.from_string('B4'),
        Pitch.from_string('A4')
    ]

    scale = Scale.major(Note.from_string('C'))

    print("Validating melody:")
    print(f"  {' - '.join(str(p) for p in melody)}")
    print()

    result = validator.validate_melody(melody, scale)

    print(f"Overall Score: {result.score:.1f}/100")
    print(f"Valid: {result.is_valid}")
    print()

    if result.violations:
        print("Issues found:")
        for v in result.violations:
            print(f"  [{v.severity.value.upper()}] {v.rule_name}")
            print(f"    {v.description}")
            if v.suggestion:
                print(f"    💡 {v.suggestion}")
            print()

    if result.strengths:
        print("Strengths:")
        for s in result.strengths:
            print(f"  ✓ {s}")
        print()

    print(f"Feedback: {result.overall_feedback}")
    print()

    # Example 2: Validate chord progression
    progression = ChordProgression.from_degrees([1, 4, 5, 1], scale)

    print("\nValidating chord progression:")
    print(f"  {progression}")
    print()

    prog_result = validator.validate_chord_progression(progression)

    print(f"Overall Score: {prog_result.score:.1f}/100")
    print(f"Feedback: {prog_result.overall_feedback}")
    print()


def demo_intelligent_ranking():
    """Demonstrate intelligent evaluation and ranking"""
    print("=" * 80)
    print("INTELLIGENT SUGGESTION RANKING")
    print("=" * 80)
    print()

    # Create suggestions
    scale = Scale.major(Note.from_string('C'))
    progression = ChordProgression.from_degrees([1, 4, 5], scale)

    suggester = MelodySuggester()
    melody = [Pitch.from_string('E4'), Pitch.from_string('D4')]

    suggestions = suggester.suggest_continuations(
        partial_melody=melody,
        progression=progression,
        current_chord_idx=1,
        num_suggestions=4,
        num_notes=4
    )

    # Rank suggestions
    evaluator = IntelligentEvaluator(
        strictness="moderate",
        style_preference="jazz"
    )

    context = {
        'progression': progression,
        'current_chord': progression.chords[1],
        'current_chord_idx': 1,
        'scale': scale
    }

    rankings = evaluator.rank_melody_suggestions(suggestions, context)

    print("Ranked Melody Suggestions:")
    print("-" * 80)

    for i, ranking in enumerate(rankings, 1):
        print(f"\n#{i} - Score: {ranking.overall_score:.1f}/100")
        print(f"  {' → '.join(str(p) for p in ranking.suggestion.pitches)}")
        print(f"  {ranking.explanation}")

        # Show criterion scores
        print(f"  Scores:")
        for criterion, score in ranking.criterion_scores.items():
            print(f"    {criterion}: {score:.0f}")

        if ranking.strengths:
            print(f"  Strengths: {', '.join(ranking.strengths[:2])}")

    print()


def demo_statistical_analysis():
    """Demonstrate statistical progression analysis"""
    print("=" * 80)
    print("STATISTICAL PROGRESSION ANALYSIS")
    print("=" * 80)
    print()

    analyzer = StatisticalProgressionAnalyzer()

    # Create training dataset
    print("Training on sample progressions...")
    c_major = Scale.major(Note.from_string('C'))

    training_progs = [
        ChordProgression.from_degrees([1, 4, 5, 1], c_major),
        ChordProgression.from_degrees([1, 5, 6, 4], c_major),
        ChordProgression.from_degrees([1, 6, 4, 5], c_major),
        ChordProgression.from_degrees([1, 4, 1, 5], c_major),
        ChordProgression.from_degrees([6, 4, 1, 5], c_major),
    ]

    analyzer.analyze_dataset(training_progs, style="pop")

    print(f"Analyzed {len(training_progs)} progressions")
    print()

    # Predict next chord
    partial = ChordProgression.from_degrees([1, 5], c_major)
    print(f"Given progression: {' - '.join(str(c) for c in partial.chords)}")
    print("\nMost likely next chords:")

    predictions = analyzer.predict_next_chord(
        partial.chords[-1],
        c_major,
        style="pop",
        top_k=5
    )

    for chord_name, prob in predictions:
        print(f"  {chord_name}: {prob*100:.1f}%")

    print()

    # Analyze common patterns
    print("\nMost common patterns:")
    patterns = analyzer.get_common_patterns(style="pop", top_k=5)

    for pattern, count, freq in patterns:
        roman = ' - '.join(['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'][d-1] for d in pattern)
        print(f"  {roman}: {freq*100:.0f}%")

    print()


def demo_neural_prediction():
    """Demonstrate neural network prediction"""
    print("=" * 80)
    print("NEURAL NETWORK CHORD PREDICTION")
    print("=" * 80)
    print()

    predictor = NeuralChordPredictor()  # Untrained for demo

    scale = Scale.major(Note.from_string('G'))
    progression = ChordProgression.from_degrees([1, 4], scale)

    print(f"Given: {' - '.join(str(c) for c in progression.chords)}")
    print("\nPredicted next chords (using fallback rules):")

    predictions = predictor.predict_next_chord(progression, scale, top_k=5)

    for chord_name, prob in predictions:
        print(f"  {chord_name}: {prob*100:.0f}%")

    print()

    # Generate multiple variations
    print("\nGenerating 3 possible continuations (2 more chords):")
    continuations = predictor.predict_next_n_chords(
        progression,
        n=2,
        scale=scale,
        num_variations=3
    )

    for i, cont in enumerate(continuations, 1):
        print(f"  {i}. {' - '.join(str(c) for c in cont.chords)}")

    print()


def demo_lick_generation():
    """Demonstrate ML-based lick generation"""
    print("=" * 80)
    print("ML-BASED LICK GENERATION")
    print("=" * 80)
    print()

    generator = NeuralLickGenerator()

    chord = Chord.from_symbol('G7')
    scale = Scale.major(Note.from_string('C'))

    styles = ['jazz', 'blues', 'rock', 'classical']

    print(f"Generating licks over {chord} in {scale.root} major:\n")

    for style in styles:
        lick = generator.generate_lick(
            chord=chord,
            scale=scale,
            style=style,
            length=6,
            difficulty=3
        )

        print(f"{style.upper()} LICK:")
        print(f"  {' → '.join(str(p) for p in lick.pitches)}")
        print(f"  {lick.description}")
        print(f"  Difficulty: {lick.difficulty}/5")
        print(f"  Tags: {', '.join(lick.tags)}")
        print()


def demo_learning_path():
    """Demonstrate adaptive learning path"""
    print("=" * 80)
    print("ADAPTIVE LEARNING PATH")
    print("=" * 80)
    print()

    path_gen = LearningPathGenerator()
    user_id = "demo_user"

    # Get initial learning path
    print(f"Learning path for {user_id}:")
    path = path_gen.get_learning_path(user_id)

    print(f"\nRecommended concepts to learn ({len(path)} total):")
    for i, concept in enumerate(path[:5], 1):
        print(f"  {i}. {concept.name}")
        print(f"     Category: {concept.category.value}")
        print(f"     Difficulty: {concept.difficulty.name}")
        print(f"     {concept.description}")
        print()

    # Simulate learning
    print("Simulating practice sessions...")
    path_gen.record_performance(user_id, "notes_basic", 0.9, "identification")
    path_gen.record_performance(user_id, "intervals_basic", 0.85, "construction")
    path_gen.record_performance(user_id, "major_scale", 0.8, "building")

    # Get progress report
    print("\nProgress Report:")
    report = path_gen.get_progress_report(user_id)

    print(f"  Current Level: {report['current_level']}")
    print(f"  Mastered: {report['mastered']}/{report['total_concepts']} concepts")
    print(f"  Completion: {report['completion_percentage']:.1f}%")
    print(f"  Next Recommended: {report['next_recommended']}")
    print()


def demo_explanations():
    """Demonstrate theory explanations"""
    print("=" * 80)
    print("MUSIC THEORY EXPLANATIONS")
    print("=" * 80)
    print()

    explainer = TheoryExplainer()

    # Explain a chord
    chord = Chord.from_symbol('Cmaj7')
    print(explainer.explain_chord(chord))
    print()

    # Explain a progression
    scale = Scale.major(Note.from_string('C'))
    progression = ChordProgression.from_degrees([1, 4, 5, 1], scale)

    print("\n" + explainer.explain_progression(progression))
    print()


def demo_exercises():
    """Demonstrate exercise generation"""
    print("=" * 80)
    print("INTERACTIVE EXERCISES")
    print("=" * 80)
    print()

    generator = ExerciseGenerator()

    # Generate different types of exercises
    exercises = [
        generator.generate_interval_exercise(difficulty=2),
        generator.generate_chord_identification_exercise(difficulty=2),
        generator.generate_progression_exercise(difficulty=3)
    ]

    for i, exercise in enumerate(exercises, 1):
        print(f"Exercise {i} - {exercise.concept.replace('_', ' ').title()}")
        print(f"Difficulty: {exercise.difficulty}/5")
        print(f"\nQuestion: {exercise.question}")

        if exercise.options:
            print("\nOptions:")
            for j, option in enumerate(exercise.options, 1):
                print(f"  {j}. {option}")

        print(f"\nAnswer: {exercise.correct_answer}")
        print(f"Explanation: {exercise.explanation}")
        print("\n" + "-" * 80 + "\n")


def demo_feedback_system():
    """Demonstrate feedback collection"""
    print("=" * 80)
    print("FEEDBACK & IMPROVEMENT SYSTEM")
    print("=" * 80)
    print()

    feedback_system = FeedbackSystem()

    # Simulate feedback
    print("Collecting user feedback...")

    feedback_system.record_feedback(
        user_id="user1",
        item_type="melody",
        item_data={'pitches': ['C4', 'D4', 'E4']},
        rating=5,
        comments="Perfect!",
        was_used=True
    )

    feedback_system.record_feedback(
        user_id="user2",
        item_type="progression",
        item_data={'chords': ['C', 'F', 'G']},
        rating=4,
        was_used=True
    )

    feedback_system.record_feedback(
        user_id="user3",
        item_type="lick",
        item_data={'style': 'jazz'},
        rating=2,
        comments="Too complex",
        was_used=False
    )

    # Get summary
    summary = feedback_system.get_feedback_summary()

    print("\nFeedback Summary:")
    print(f"  Total feedback: {summary['total']}")
    print(f"  Average rating: {summary['avg_rating']:.1f}/5")
    print(f"  High rated (4-5★): {summary['high_rated']}")
    print(f"  Low rated (1-2★): {summary['low_rated']}")

    print("\n  By Item Type:")
    for item_type, stats in summary['by_type'].items():
        print(f"    {item_type}:")
        print(f"      Count: {stats['count']}")
        print(f"      Avg Rating: {stats['avg_rating']:.1f}/5")
        print(f"      Usage Rate: {stats['usage_rate']*100:.0f}%")

    # Get improvement recommendations
    improver = ModelImprover(feedback_system)
    recommendations = improver.analyze_feedback_patterns()

    print("\nImprovement Recommendations:")
    for rec in recommendations:
        print(f"  • {rec}")

    print()


def main():
    """Run all demos"""
    print("\n")
    print("█" * 80)
    print(" " * 20 + "MUSIC THEORY ML - INTELLIGENCE FEATURES")
    print("█" * 80)
    print("\n")

    demos = [
        ("Validation & Scoring", demo_validation_and_scoring),
        ("Intelligent Ranking", demo_intelligent_ranking),
        ("Statistical Analysis", demo_statistical_analysis),
        ("Neural Prediction", demo_neural_prediction),
        ("Lick Generation", demo_lick_generation),
        ("Learning Path", demo_learning_path),
        ("Explanations", demo_explanations),
        ("Exercises", demo_exercises),
        ("Feedback System", demo_feedback_system)
    ]

    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"Error in {name}: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("=" * 80)
    print("✓ Intelligence features demo completed!")
    print()
    print("Key Features Demonstrated:")
    print("  • Music theory rule validation with detailed feedback")
    print("  • Intelligent suggestion ranking with multiple criteria")
    print("  • Statistical analysis of chord progression patterns")
    print("  • Neural network-based chord prediction")
    print("  • ML-based melodic lick generation (multiple styles)")
    print("  • Adaptive learning paths with progress tracking")
    print("  • Clear theory explanations for education")
    print("  • Auto-generated practice exercises")
    print("  • Feedback collection for continuous improvement")
    print("=" * 80)
    print()


if __name__ == '__main__':
    main()
