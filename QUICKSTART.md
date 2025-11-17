## Quick Start Guide

This guide will help you get started with the Music Theory ML Model.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd music-theory-llm

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### 1. Working with Music Theory Concepts

```python
from src.theory import Note, Chord, Scale, ChordProgression

# Create notes and chords
c_note = Note.from_string('C')
c_major = Chord.from_symbol('C')
g7 = Chord.from_symbol('G7')

# Create scales
c_major_scale = Scale.major(Note.from_string('C'))
a_minor_scale = Scale.minor(Note.from_string('A'))

# Create chord progressions
progression = ChordProgression.from_degrees([1, 4, 5, 1], c_major_scale)
print(progression)
# Output: Key of C:
#         C - F - G - C
#         (I - IV - V - I)
```

### 2. Melody Suggestions

```python
from src.theory import Pitch
from src.utils import MelodySuggester

# Create a partial melody
melody = [
    Pitch.from_string('E4'),
    Pitch.from_string('D4'),
    Pitch.from_string('C4')
]

# Get suggestions
suggester = MelodySuggester()
suggestions = suggester.suggest_continuations(
    partial_melody=melody,
    progression=progression,
    current_chord_idx=1,
    num_suggestions=4,
    num_notes=4
)

# Each suggestion includes:
# - pitches: The melodic continuation
# - description: Explanation of the choice
# - tension_trajectory: How tension evolves
# - voice_leading_quality: Quality score (1-5)

for i, option in enumerate(suggestions, 1):
    print(f"Option {i}: {option.description}")
    print(f"Notes: {' -> '.join(str(p) for p in option.pitches)}")
```

### 3. Harmonic Analysis

```python
from src.utils import HarmonicAnalyzer

analyzer = HarmonicAnalyzer()

# Comprehensive analysis
analysis = analyzer.analyze_progression(progression)
print(f"Key: {analysis['key']}")
print(f"Cadence: {analysis['cadence_type']}")

# Get harmonic suggestions
passing_chords = analyzer.suggest_passing_chords(progression)
secondary_doms = analyzer.suggest_secondary_dominants(progression)
borrowed_chords = analyzer.suggest_modal_interchange(progression)
extensions = analyzer.suggest_chord_extensions(progression)

# Each suggestion includes detailed explanations
for sugg in passing_chords:
    print(f"{sugg.chord}: {sugg.description}")
```

### 4. Training a Model

```bash
# Train on chord progression prediction
python train.py --task progression --epochs 20 --batch-size 32

# Train on scale identification
python train.py --task scale --epochs 20

# Train on chord quality classification
python train.py --task quality --epochs 15
```

## Running Examples

```bash
# Basic usage examples
cd examples
python basic_usage.py

# Melody suggestion demo
python melody_suggestions_demo.py

# Advanced harmonic analysis demo
python harmonic_analysis_demo.py
```

## Key Features

### Melody Suggestions
- **Stepwise continuation**: Smooth voice leading maintaining tension
- **Leap with resolution**: Creates drama then resolves
- **Approach patterns**: Tension-release through chromatic/diatonic approaches
- **Arpeggio patterns**: Emphasizes underlying harmony

### Harmonic Analysis
- **Passing chords**: Smooth chromatic and diatonic connections
- **Secondary dominants**: Temporary tonicization (V7/x chords)
- **Tritone substitutions**: Jazz reharmonization technique
- **Modal interchange**: Borrowed chords from parallel modes
- **Chord extensions**: Add 9th, 11th, 13th for sophisticated color
- **Voice leading analysis**: Evaluate smoothness of chord transitions

## Common Use Cases

### Generate a chord progression in any key

```python
from src.theory import Scale, ChordProgression
from src.theory.progressions import get_common_progression

# Get a common progression
scale = Scale.major(Note.from_string('G'))
prog = get_common_progression('I-V-vi-IV', scale)
print(prog)
# Output: G - D - Em - C
```

### Analyze melody-harmony fit

```python
from src.utils import MelodySuggester

melody = [Pitch.from_string('E4'), Pitch.from_string('G4')]
chord = Chord.from_symbol('C')

suggester = MelodySuggester()
analysis = suggester.analyze_melody_harmony_fit(melody, chord)

print(f"Chord tones: {len(analysis['chord_tones'])}")
print(f"Tension level: {analysis['avg_tension']}")
```

### Get reharmonization ideas

```python
from src.utils import HarmonicAnalyzer

analyzer = HarmonicAnalyzer()

# Start with simple progression
simple_prog = ChordProgression.from_degrees([1, 4, 5, 1], c_major_scale)

# Get all enhancement suggestions
passing = analyzer.suggest_passing_chords(simple_prog)
secondary = analyzer.suggest_secondary_dominants(simple_prog)
borrowed = analyzer.suggest_modal_interchange(simple_prog)

# Apply suggestions to create richer harmony
```

### Transpose progressions

```python
# Transpose from C to D
c_scale = Scale.major(Note.from_string('C'))
d_scale = Scale.major(Note.from_string('D'))

prog_c = ChordProgression.from_degrees([1, 6, 4, 5], c_scale)
prog_d = prog_c.to_key(d_scale)

print(f"In C: {prog_c}")
print(f"In D: {prog_d}")
```

## Model Training Details

The library includes three types of training tasks:

1. **Chord Progression Prediction**: Given a partial progression, predict the next chord
2. **Scale Identification**: Given notes, identify the scale
3. **Chord Quality Classification**: Given notes, classify the chord type

Models use transformer architecture and can be customized:
- Adjust `--d-model` for embedding dimension
- Adjust `--num-layers` for model depth
- Adjust `--epochs` and `--lr` for training

## Next Steps

- Explore the `examples/` directory for more demos
- Check out `src/theory/` for music theory implementations
- Read the model documentation in `src/models/`
- Train your own model with custom data

## Tips

- Use Roman numeral analysis for key-independent progressions
- Experiment with different scale modes (Dorian, Mixolydian, etc.)
- Try modal interchange for interesting harmonic colors
- Use chord extensions to add sophistication to basic progressions
- Analyze voice leading quality when choosing between options

## Need Help?

- Check the examples in `examples/` directory
- Read the full documentation in each module
- Review the model architecture in `src/models/`
