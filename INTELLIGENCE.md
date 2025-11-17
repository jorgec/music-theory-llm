# Intelligence & Learning System

Advanced intelligence features for the Music Theory ML Model, providing validation, ranking, learning pathways, and continuous improvement.

## 🧠 Core Intelligence Features

### 1. Music Theory Validation

**Validates musical constructs against established rules** (`validators.py`)

```python
from src.intelligence import MusicTheoryValidator

validator = MusicTheoryValidator(strictness="moderate")

# Validate a melody
result = validator.validate_melody(melody, scale)

print(f"Score: {result.score}/100")
for violation in result.violations:
    print(f"Issue: {violation.description}")
    print(f"Suggestion: {violation.suggestion}")
```

**Features:**
- ✓ Melodic rule checking (leaps, range, contour, scale conformity)
- ✓ Chord progression validation (voice leading, harmonic function)
- ✓ Voice leading analysis (parallel motion, smoothness)
- ✓ Detailed feedback with severity levels (ERROR, WARNING, INFO)
- ✓ Scoring system (0-100) with penalty weights
- ✓ Adjustable strictness (strict, moderate, lenient)

**Rules Checked:**
- Large melodic leaps (>octave)
- Tritone leaps
- Leap resolution
- Melodic range appropriateness
- Scale conformity
- Parallel 5ths and octaves
- Voice leading smoothness
- Harmonic function logic

### 2. Intelligent Evaluation & Ranking

**Ranks suggestions using multiple criteria** (`evaluator.py`)

```python
from src.intelligence import IntelligentEvaluator

evaluator = IntelligentEvaluator(
    strictness="moderate",
    style_preference="jazz"
)

# Rank melody suggestions
rankings = evaluator.rank_melody_suggestions(suggestions, context)

for ranking in rankings:
    print(f"Score: {ranking.overall_score}/100")
    print(f"Explanation: {ranking.explanation}")
    print(f"Strengths: {ranking.strengths}")
```

**Ranking Criteria:**
1. **Theory Correctness** (25%) - Adherence to music theory rules
2. **Voice Leading** (20%) - Smoothness of motion
3. **Stylistic Fit** (15%) - Matches desired style
4. **Harmonic Interest** (15%) - Interesting/sophisticated harmony
5. **Melodic Quality** (15%) - Compelling melodic contour
6. **Creativity** (10%) - Uniqueness of approach

**Benefits:**
- Multi-dimensional scoring
- Style-aware evaluation
- Detailed explanations for each ranking
- Identifies both strengths and weaknesses
- Confidence scoring

### 3. Statistical Progression Analysis

**Learns from datasets of chord progressions** (`statistical_analyzer.py`)

```python
from src.intelligence.statistical_analyzer import StatisticalProgressionAnalyzer

analyzer = StatisticalProgressionAnalyzer()

# Analyze dataset
analyzer.analyze_dataset(progressions, style="jazz")

# Predict next chord
predictions = analyzer.predict_next_chord(current_chord, scale, style="jazz")
# Returns: [('Dm7', 0.35), ('G7', 0.28), ...]

# Get common patterns
patterns = analyzer.get_common_patterns(style="jazz")
# Returns: [([2, 5, 1], 150, 0.45), ...]  # ii-V-I appears 45% of time

# Analyze progression likelihood
analysis = analyzer.analyze_progression_likelihood(progression, style="jazz")
print(analysis['likelihood_score'])  # 0-100
print(analysis['interpretation'])
```

**Features:**
- Builds Markov chain transition probabilities
- Identifies common patterns by frequency
- Predicts likely next chords (top-k)
- Style-specific analysis (jazz, pop, classical, etc.)
- Likelihood scoring for progressions
- Generates statistically likely progressions
- Pattern matching and recognition

**Use Cases:**
- Learning what makes progressions "sound good"
- Predicting logical next chords
- Identifying unusual/creative progressions
- Style classification

### 4. Neural Network Prediction

**Deep learning for chord progression** (`neural_predictor.py`)

```python
from src.intelligence import NeuralChordPredictor

predictor = NeuralChordPredictor(model_path="checkpoints/progression_model")

# Predict next chord
predictions = predictor.predict_next_chord(progression, scale, top_k=5)

# Generate variations
continuations = predictor.predict_next_n_chords(
    progression,
    n=4,
    scale=scale,
    temperature=0.8,
    num_variations=3
)

# Fine-tune on your data
predictor.fine_tune_on_progressions(
    your_progressions,
    num_epochs=10,
    save_path="checkpoints/custom_model"
)
```

**Features:**
- Transformer-based architecture
- Temperature-controlled generation
- Multiple variation generation
- Fine-tuning capability
- Fallback to rule-based prediction
- Likelihood evaluation

### 5. ML-Based Lick Generation

**Generates melodic phrases/licks** (`lick_generator.py`)

```python
from src.intelligence.lick_generator import NeuralLickGenerator

generator = NeuralLickGenerator()

# Generate a lick
lick = generator.generate_lick(
    chord=Chord.from_symbol('G7'),
    scale=Scale.major(Note.from_string('C')),
    style="jazz",
    length=8,
    difficulty=3
)

print(f"Lick: {' → '.join(str(p) for p in lick.pitches)}")
print(f"Description: {lick.description}")
print(f"Works over: {lick.works_over}")
print(f"Tags: {lick.tags}")
```

**Supported Styles:**
- **Jazz**: Bebop lines, chromatic approaches, arpeggios
- **Blues**: Pentatonic, bends, blue notes
- **Rock**: Fast pentatonic runs, power patterns
- **Classical**: Stepwise motion, ornaments, balanced phrases

**Features:**
- Style-specific generation
- Difficulty levels (1-5)
- Pre-loaded lick database
- Learn from custom licks
- Find similar licks
- Automatic descriptions and tagging

### 6. Adaptive Learning Paths

**Personalized curriculum with progress tracking** (`learning_path.py`)

```python
from src.intelligence import LearningPathGenerator, DifficultyLevel

path_gen = LearningPathGenerator()

# Get personalized learning path
path = path_gen.get_learning_path(user_id="user123")

# Get next concept
next_concept = path_gen.get_next_concept(user_id="user123")
print(f"Learn next: {next_concept.name}")
print(f"Prerequisites: {next_concept.prerequisites}")

# Record practice performance
path_gen.record_performance(
    user_id="user123",
    concept_id="major_scale",
    score=0.85,  # 85% correct
    exercise_type="construction"
)

# Get progress report
report = path_gen.get_progress_report(user_id="user123")
print(f"Level: {report['current_level']}")
print(f"Mastered: {report['mastered']}/{report['total_concepts']}")
print(f"Completion: {report['completion_percentage']}%")
```

**Curriculum Structure:**
1. **Beginner**: Notes, intervals, major scales
2. **Elementary**: Minor scales, basic triads
3. **Intermediate**: 7th chords, diatonic harmony, progressions
4. **Advanced**: Harmonic functions, voice leading, secondary dominants
5. **Expert**: Modal interchange, advanced reharmonization

**Features:**
- Prerequisite tracking
- Adaptive difficulty adjustment
- Performance-based mastery scoring
- Progress analytics
- Category-based organization
- Study time tracking

### 7. Theory Explanations

**Clear, educational explanations** (`explainer.py`)

```python
from src.intelligence import TheoryExplainer

explainer = TheoryExplainer()

# Explain a chord
explanation = explainer.explain_chord(Chord.from_symbol('Cmaj7'))
# Returns formatted explanation with notes, quality, intervals

# Explain a progression
explanation = explainer.explain_progression(progression)
# Includes key, Roman numerals, harmonic functions, cadence analysis
```

**Explanations Include:**
- Chord notes and quality descriptions
- Interval analysis
- Harmonic function meanings
- Cadence types and effects
- Functional motion descriptions

### 8. Exercise Generation

**Auto-generated practice exercises** (`exercises.py`)

```python
from src.intelligence import ExerciseGenerator

generator = ExerciseGenerator()

# Generate exercises
interval_ex = generator.generate_interval_exercise(difficulty=2)
chord_ex = generator.generate_chord_identification_exercise(difficulty=3)
progression_ex = generator.generate_progression_exercise(difficulty=3)

print(f"Question: {interval_ex.question}")
print(f"Options: {interval_ex.options}")
print(f"Answer: {interval_ex.correct_answer}")
print(f"Explanation: {interval_ex.explanation}")
```

**Exercise Types:**
- Interval identification
- Chord identification from notes
- Progression analysis (Roman numerals)
- Scale construction (coming soon)
- Voice leading (coming soon)

### 9. Feedback & Improvement

**Continuous improvement through user feedback** (`feedback.py`)

```python
from src.intelligence import FeedbackSystem, ModelImprover

feedback_system = FeedbackSystem()

# Record feedback
feedback_system.record_feedback(
    user_id="user123",
    item_type="melody",
    item_data={'pitches': [...]},
    rating=5,  # 1-5 stars
    comments="Perfect for jazz!",
    was_used=True
)

# Analyze feedback
summary = feedback_system.get_feedback_summary()
print(f"Average rating: {summary['avg_rating']}/5")
print(f"Usage rate: {summary['by_type']['melody']['usage_rate']}")

# Get improvement recommendations
improver = ModelImprover(feedback_system)
recommendations = improver.analyze_feedback_patterns()
for rec in recommendations:
    print(f"• {rec}")

# Get high-quality examples for fine-tuning
good_examples = improver.get_high_quality_examples("progression", min_rating=4)
```

## 🎯 Complete Workflow Example

```python
from src.theory import *
from src.intelligence import *

# 1. Generate suggestions
suggester = MelodySuggester()
suggestions = suggester.suggest_continuations(melody, progression, 1, num_notes=4)

# 2. Validate each suggestion
validator = MusicTheoryValidator()
validated_suggestions = []
for sug in suggestions:
    result = validator.validate_melody(sug.pitches, scale)
    validated_suggestions.append((sug, result))

# 3. Rank by quality
evaluator = IntelligentEvaluator(style_preference="jazz")
rankings = evaluator.rank_melody_suggestions(suggestions, context)

# 4. Present top suggestions with explanations
best = rankings[0]
explainer = TheoryExplainer()
print(f"Score: {best.overall_score}/100")
print(f"Explanation: {best.explanation}")

# 5. Collect user feedback
feedback_system = FeedbackSystem()
feedback_system.record_feedback(
    user_id="user",
    item_type="melody",
    item_data={'pitches': [str(p) for p in best.suggestion.pitches]},
    rating=5,
    was_used=True
)

# 6. Update learning progress
path_gen = LearningPathGenerator()
path_gen.record_performance("user", "melody_writing", 0.9, "generation")
```

## 📊 Statistics & Analytics

### Progression Analysis
```python
analyzer = StatisticalProgressionAnalyzer()
analyzer.analyze_dataset(1000_progressions, style="pop")

# Generate report
report = analyzer.get_summary_report(style="pop")
print(report)
# Shows:
# - Most common chords
# - Most common transitions
# - Common patterns (I-V-vi-IV, etc.)
# - Cadence frequencies
```

### Learning Analytics
```python
path_gen = LearningPathGenerator()
report = path_gen.get_progress_report(user_id)
# Returns:
# - Current level
# - Mastered concepts
# - Category breakdown
# - Recent activity
# - Next recommendations
```

## 🚀 Training Your Own Models

### Train Progression Predictor
```bash
python train.py --task progression --epochs 50 --train-samples 50000
```

### Fine-Tune on Custom Data
```python
predictor = NeuralChordPredictor()
predictor.fine_tune_on_progressions(
    your_progressions,
    num_epochs=20,
    learning_rate=1e-4,
    save_path="checkpoints/custom"
)
```

### Train Lick Generator
```python
generator = NeuralLickGenerator()
generator.learn_from_licks(
    your_licks,
    num_epochs=30,
    learning_rate=1e-3
)
```

## 🎓 Learning Pathway

1. **Start**: Basic validation and explanations
2. **Intermediate**: Statistical analysis and ranking
3. **Advanced**: Neural prediction and generation
4. **Expert**: Fine-tuning models on custom data

## 📈 Pathways for Improvement

### For the Model:
1. Collect user feedback consistently
2. Analyze feedback patterns
3. Fine-tune on high-quality examples
4. A/B test improvements
5. Iterate based on metrics

### For the User:
1. Follow adaptive learning path
2. Practice with generated exercises
3. Get immediate feedback
4. Track progress over time
5. Advance to next difficulty level

## 🎯 Key Advantages

1. **Multi-Layered Intelligence**: Combines rules, statistics, and ML
2. **Transparent**: Clear explanations and scoring
3. **Adaptive**: Learns from feedback and adjusts difficulty
4. **Educational**: Built-in learning paths and exercises
5. **Extensible**: Easy to add new validators, rankers, etc.
6. **Production-Ready**: Comprehensive error handling and fallbacks

## 💡 Best Practices

1. **Use validation** before presenting suggestions to users
2. **Rank suggestions** to show best options first
3. **Provide explanations** to make it educational
4. **Collect feedback** to continuously improve
5. **Track progress** to keep users engaged
6. **Start simple** with rule-based, add ML gradually
7. **Fine-tune** models on your specific use case

## 🔮 Future Enhancements

- Style transfer (convert between styles)
- Multi-objective optimization
- Attention visualization
- Real-time collaborative learning
- Auto-curriculum generation
- Difficulty auto-calibration
- More exercise types
- Audio generation integration
