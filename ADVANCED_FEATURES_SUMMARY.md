# Music Theory ML - Advanced Features Summary

## Overview
This document summarizes the advanced enhancements to the Music Theory ML system, focusing on extended chord support, comprehensive lick databases, and the intelligent recommendation system.

## Table of Contents
1. [Advanced Chord Support](#advanced-chord-support)
2. [Style-Specific Generators](#style-specific-generators)
3. [Recommendation System](#recommendation-system)
4. [Lick & Riff Databases](#lick--riff-databases)
5. [Model Architecture](#model-architecture)
6. [Training Configurations](#training-configurations)
7. [Usage Examples](#usage-examples)

---

## Advanced Chord Support

### 32+ Chord Quality Types

The system now supports an extensive range of chord qualities covering everything from basic triads to complex 13th and altered chords:

#### Triads (6 types)
- **Major**: `C` - `[0, 4, 7]`
- **Minor**: `Cm` - `[0, 3, 7]`
- **Diminished**: `Cdim` - `[0, 3, 6]`
- **Augmented**: `Caug` - `[0, 4, 8]`
- **Suspended 2nd**: `Csus2` - `[0, 2, 7]`
- **Suspended 4th**: `Csus4` - `[0, 5, 7]`

#### 7th Chords (7 types)
- **Major 7th**: `Cmaj7` - `[0, 4, 7, 11]`
- **Minor 7th**: `Cm7` - `[0, 3, 7, 10]`
- **Dominant 7th**: `C7` - `[0, 4, 7, 10]`
- **Diminished 7th**: `Cdim7` - `[0, 3, 6, 9]`
- **Half-Diminished 7th**: `Cm7b5` - `[0, 3, 6, 10]` *(Jazz ii-V-i)*
- **Augmented 7th**: `Caug7` - `[0, 4, 8, 10]`
- **Minor-Major 7th**: `CmMaj7` - `[0, 3, 7, 11]`

#### 9th Chords (5 types)
- **Major 9th**: `Cmaj9` - `[0, 4, 7, 11, 14]`
- **Minor 9th**: `Cm9` - `[0, 3, 7, 10, 14]`
- **Dominant 9th**: `C9` - `[0, 4, 7, 10, 14]`
- **Dominant 7b9**: `C7b9` - `[0, 4, 7, 10, 13]` *(Bebop classic)*
- **Dominant 7#9**: `C7#9` - `[0, 4, 7, 10, 15]` *(Hendrix chord)*

#### 11th Chords (3 types)
- **Dominant 11th**: `C11` - `[0, 4, 7, 10, 14, 17]`
- **Minor 11th**: `Cm11` - `[0, 3, 7, 10, 14, 17]`
- **Major 11th**: `Cmaj11` - `[0, 4, 7, 11, 14, 17]`

#### 13th Chords (4 types)
- **Dominant 13th**: `C13` - `[0, 4, 7, 10, 14, 21]` *(Jazz standard)*
- **Minor 13th**: `Cm13` - `[0, 3, 7, 10, 14, 21]`
- **Major 13th**: `Cmaj13` - `[0, 4, 7, 11, 14, 21]`
- **Dominant 7b13**: `C7b13` - `[0, 4, 7, 10, 20]`

#### Altered Chords (2 types)
- **Altered Dominant**: `C7alt` - `[0, 4, 10, 13, 15, 20]` *(b9, #9, b13)*
- **Lydian Dominant**: `C7#11` - `[0, 4, 7, 10, 18]` *(Melodic minor)*

#### Other Chords (5 types)
- **Power Chord**: `C5` - `[0, 7]`
- **Major 6th**: `C6` - `[0, 4, 7, 9]`
- **Minor 6th**: `Cm6` - `[0, 3, 7, 9]`
- **Major 6/9**: `C6/9` - `[0, 4, 7, 9, 14]` *(Jazz voicing)*
- **Minor 6/9**: `Cm6/9` - `[0, 3, 7, 9, 14]`

### Specific Requested Chord Examples

All specifically requested chord types are fully supported:

```python
from src.theory import Chord, ChordQuality, Note

# Dm7
Chord(Note.from_string('D'), ChordQuality.MINOR_7)
# → Dm7

# GMaj7
Chord(Note.from_string('G'), ChordQuality.MAJOR_7)
# → Gmaj7

# C#7#9 (Hendrix chord)
Chord(Note.from_string('C#'), ChordQuality.DOMINANT_7_SHARP_9)
# → C#7#9

# Dm7b5 (half-diminished)
Chord(Note.from_string('D'), ChordQuality.HALF_DIMINISHED_7)
# → Dm7b5

# Diminished chords
Chord(Note.from_string('B'), ChordQuality.DIMINISHED_7)
# → Bdim7
```

---

## Style-Specific Generators

### 10 Musical Styles Supported

Each style has dedicated generators with authentic harmonic patterns:

#### Priority Styles (Primary Focus)

1. **Neo Soul** (189 progressions)
   - Extended chords: maj9, m9, 13
   - Chromatic movement
   - Gospel-influenced harmony
   - Example: `Cmaj9 → Am9 → Dm9 → G9`

2. **Blues** (182 progressions with advanced chords)
   - 12-bar blues (classic, quick change, jazz)
   - Minor blues
   - Advanced: 7#9, 7b9, diminished passing, altered
   - Example: `E7#9 → Ab7#9 → E7#9 → E7`

3. **Progressive Metal** (200 progressions)
   - Modal progressions (Phrygian, Lydian)
   - Polymodal harmony
   - Technical riffs
   - Example: `Em → F → G → Em` (Phrygian)

4. **Rock Fusion** (198 progressions)
   - Jazz-rock hybrids
   - Modal fusion
   - Complex harmony
   - Example: `Cmaj7 → Em7 → Fmaj7 → Dm7`

#### Additional Styles

5. **Jazz** (151 progressions with advanced chords)
   - ii-V-I progressions
   - Turnarounds
   - Advanced: ii-V7alt-I, m7b5-V7#9-i, sophisticated 13ths
   - Example: `Dm9 → G7alt → Cmaj9`

6. **Math Rock** (200 progressions)
   - Angular progressions with unexpected intervals
   - Asymmetric patterns

7. **Post Rock** (200 progressions)
   - Atmospheric, building progressions
   - Pedal tones

8. **Shoegaze** (200 progressions)
   - Dreamy progressions with suspended chords
   - Dissonant textures

9. **Metalcore** (200 progressions)
   - Breakdown progressions
   - Power chords with chromatic movement

10. **R&B** (196 progressions)
    - Smooth progressions with extended chords
    - Gospel influences

**Total**: 1,916 style-specific chord progressions

---

## Recommendation System

### Three-Tier Recommendation Engine

#### 1. ChordProgressionRecommender
- **Statistical Analysis**: Transition probability matrices per style
- **Neural Embeddings**: Learned similarity (when model loaded)
- **Rule-Based Filtering**: Music theory validation

Features:
- Recommend progressions by style and key
- Predict next chord based on context
- Score progressions using multiple factors:
  - Transition probability
  - Chord variety
  - Voice leading quality

Example:
```python
from src.recommender import MusicRecommendationSystem
from src.theory import Note

system = MusicRecommendationSystem()

# Get neo soul progressions in C
recs = system.progression_recommender.recommend_progressions(
    style='neo_soul',
    key=Note.from_string('C'),
    num_recommendations=5
)

# Each recommendation includes:
# - Chord progression
# - Score (0-1)
# - Explanation
# - Metadata
```

#### 2. MelodyRecommender
- AI-powered melody generation
- Conditioned on chord progressions
- Temperature and top-k sampling
- Multiple variations

Features:
- Generate melodies that fit progressions
- Rule-based fallback when no model loaded
- Adjustable creativity via temperature

#### 3. LickRecommender
- Extensive style-specific lick databases
- Interval-based representations
- Automatic transposition to any key
- Technique annotations

Features:
- 10 blues licks with techniques
- 10 jazz licks with techniques
- Licks for all other styles
- Context-aware suggestions

---

## Lick & Riff Databases

### Blues Licks (10 comprehensive patterns)

1. **Classic Blues Box**
   - Pattern: Minor pentatonic with blue note
   - Techniques: Bends on b5 (blue note), vibrato
   - Description: Blues box position 1

2. **BB King Box**
   - Pattern: Quick returns in box pattern
   - Techniques: Quick hammer-ons, wide vibrato
   - Description: BB King signature sound

3. **Turnaround Lick**
   - Pattern: Chromatic descent
   - Techniques: Chromatic run, swing eighth notes
   - Description: I-VI-ii-V turnarounds

4. **Albert King Lick**
   - Pattern: Behind-the-beat phrasing
   - Techniques: Heavy bends, laid-back timing
   - Description: Minor pentatonic with feel

5. **Stevie Ray Vaughan Lick**
   - Pattern: Blue note with octave jump
   - Techniques: Aggressive bends, palm muting
   - Description: Texas blues style

6. **Double Stop Blues**
   - Pattern: Parallel sixths
   - Techniques: Double stops, rake
   - Description: Classic blues sound

7. **Slide Blues Lick**
   - Pattern: Open position slide
   - Techniques: Slide, open tuning
   - Description: Delta blues

8. **Muddy Waters Lick**
   - Pattern: Blue note emphasis
   - Techniques: Heavy vibrato, quarter bends
   - Description: Chicago blues

9. **T-Bone Walker Lick**
   - Pattern: Jazz-blues hybrid with 6th
   - Techniques: Smooth legato, light vibrato
   - Description: Jump blues style

10. **Diminished Blues Run**
    - Pattern: Blues scale with passing diminished
    - Techniques: Hammer-ons, pull-offs
    - Description: Fast blues runs

### Jazz Licks (10 comprehensive patterns)

1. **ii-V-I Bebop Lick**
   - Pattern: Chromatic approach tones
   - Techniques: Chromatic approach, eighth note lines
   - Description: Classic bebop over ii-V-I

2. **Altered Scale Lick**
   - Pattern: Altered dominant scale
   - Techniques: Altered tones, outside playing
   - Description: For 7alt chords

3. **Wes Montgomery Octaves**
   - Pattern: Parallel octaves
   - Techniques: Thumb picking, octave technique
   - Description: Wes Montgomery style

4. **Pat Martino Minor ii-V**
   - Pattern: Dorian and harmonic minor
   - Techniques: Modal playing, position shifting
   - Description: Minor ii-V-i approach

5. **Diminished Arpeggio**
   - Pattern: Diminished 7th arpeggio (symmetric)
   - Techniques: Sweep picking, symmetrical fingering
   - Description: Cycles every minor 3rd

6. **Charlie Parker Blues**
   - Pattern: Chromatic passing tones
   - Techniques: Fast alternate picking, swing phrasing
   - Description: Bird blues style

7. **Grant Green Soul Jazz**
   - Pattern: Minor pentatonic with blues feel
   - Techniques: Slight bends, funky rhythm
   - Description: Bluesy jazz approach

8. **Joe Pass Walking Bass**
   - Pattern: Chord tones walking
   - Techniques: Thumb bass, chord melody
   - Description: Walking bassline with chords

9. **Half-Diminished Lick**
   - Pattern: Locrian mode
   - Techniques: Voice leading, modal approach
   - Description: Over m7b5 chords

10. **Lydian Dominant Run**
    - Pattern: Lydian dominant (melodic minor 4th)
    - Techniques: Raised 4th, exotic sound
    - Description: Over 7#11 chords

---

## Model Architecture

### 50M Parameter Model (train_50m_model.py)

**Configuration**:
- **Model Size**: 55.97M parameters
- **Architecture**:
  - d_model: 576
  - Num layers: 6 (encoder + decoder)
  - Num heads: 8
  - FFN dimension: 2,304 (4x d_model)
  - Dropout: 0.1

**Training**:
- Epochs: 50
- Batch size: 64
- Learning rate: 5e-5
- Optimizer: AdamW (β1=0.9, β2=0.98, eps=1e-9)
- Weight decay: 0.01
- LR Schedule: Warmup (2 epochs) + linear decay
- Gradient clipping: 1.0
- Label smoothing: 0.1

**Performance**:
- Memory footprint: ~224 MB
- Training time: ~50-60 hours on GPU
- Best for: Complex harmony, extended chords, advanced patterns

### Priority Style Models (train_priority_styles.py)

Optimized configurations for each priority style:

#### Neo Soul Model
- **Parameters**: 21.4M
- **Architecture**: d_model=384, layers=6
- **Training**: 60 epochs, batch_size=32, lr=8e-5
- **Focus**: Extended chords, chromatic movement, gospel influences

#### Blues Model
- **Parameters**: 6.4M
- **Architecture**: d_model=256, layers=4
- **Training**: 50 epochs, batch_size=32, lr=1e-4
- **Focus**: 12-bar blues, pentatonic patterns, dominant 7ths, altered dominants

#### Progressive Metal Model
- **Parameters**: 21.4M
- **Architecture**: d_model=384, layers=6
- **Training**: 60 epochs, batch_size=32, lr=8e-5
- **Focus**: Modal progressions, polymodal harmony, technical riffs

#### Rock Fusion Model
- **Parameters**: 21.4M
- **Architecture**: d_model=384, layers=6
- **Training**: 60 epochs, batch_size=32, lr=8e-5
- **Focus**: Jazz-rock hybrids, complex harmony, modal fusion

**Total**: 70.5M parameters across all priority models

---

## Training Configurations

### Dataset Sizes
- Neo Soul: 189 progressions
- Blues: 182 progressions (with advanced chords)
- Progressive Metal: 200 progressions
- Rock Fusion: 198 progressions
- Jazz: 151 progressions (with advanced chords)
- Math Rock: 200 progressions
- Post Rock: 200 progressions
- Shoegaze: 200 progressions
- Metalcore: 200 progressions
- R&B: 196 progressions

**Total**: 1,916 style-specific progressions

### Training Features
- **Label Smoothing**: 0.1 (prevents overconfidence)
- **Gradient Clipping**: 1.0 (training stability)
- **Warmup Scheduling**: 2 epochs (smooth learning start)
- **Advanced LR Scheduling**: Cosine annealing with restarts
- **Data Augmentation**: Key transposition
- **Style-Specific Fine-tuning**: Separate models per genre

---

## Usage Examples

### 1. Get Recommendations for All Components

```python
from src.recommender import MusicRecommendationSystem
from src.theory import Note

system = MusicRecommendationSystem()

# Get complete recommendations for neo soul in D
results = system.get_complete_recommendations(
    style='neo_soul',
    key=Note.from_string('D'),
    include_progressions=True,
    include_melodies=True,
    include_licks=True
)

# Access progressions
for rec in results['progressions'][:3]:
    prog = rec.item
    chords = [c.to_symbol() for c in prog.chords]
    print(f"{' → '.join(chords)} (Score: {rec.score:.3f})")

# Access licks
for rec in results['licks'][:3]:
    lick = rec.item
    print(f"{lick['name']}: {rec.explanation}")
    print(f"Notes: {' - '.join(lick['transposed_notes'][:8])}")
```

### 2. Predict Next Chord

```python
from src.theory import Chord, ChordQuality, Scale, Note

system = MusicRecommendationSystem()

# Current progression: Cmaj7 → Am9
key = Note.from_string('C')
scale = Scale.major(key)

current = [
    Chord(scale.notes[0], ChordQuality.MAJOR_7),  # Cmaj7
    Chord(scale.notes[5], ChordQuality.MINOR_9),  # Am9
]

# What should come next in neo soul style?
next_chords = system.progression_recommender.recommend_next_chord(
    current_progression=current,
    style='neo_soul',
    top_k=5
)

for chord_key, prob, explanation in next_chords:
    print(f"{chord_key}: {prob*100:.1f}% - {explanation}")
```

### 3. Work with Advanced Chords

```python
from src.theory import Chord, ChordQuality, Note

# Create advanced chords
chords = [
    Chord(Note.from_string('D'), ChordQuality.MINOR_9),          # Dm9
    Chord(Note.from_string('G'), ChordQuality.ALTERED),          # G7alt
    Chord(Note.from_string('C'), ChordQuality.MAJOR_9),          # Cmaj9
    Chord(Note.from_string('A'), ChordQuality.HALF_DIMINISHED_7),  # Am7b5
    Chord(Note.from_string('D'), ChordQuality.DOMINANT_7_SHARP_9), # D7#9
]

for chord in chords:
    print(f"{chord.to_symbol()}: {chord.quality.value}")
```

### 4. Train Priority Style Models

```bash
# Train all priority styles
python train_priority_styles.py

# Train specific styles
python train_priority_styles.py --styles neo_soul blues

# Show training plan without training
python train_priority_styles.py --dry-run

# Custom configuration
python train_priority_styles.py --save-dir my_models
```

### 5. Demo Advanced Features

```bash
# Comprehensive recommendation demo
python demo_recommender.py

# Advanced chord support demo
python demo_advanced_chords.py
```

---

## Technical Implementation Details

### Chord Representation
- **Interval-based**: All chords defined by semitone intervals from root
- **Symbolic Naming**: Automatic conversion to/from standard notation
- **Voice Leading**: Calculated using interval distances
- **Transposition**: Efficient key changes using modular arithmetic

### Recommendation Algorithms

#### Statistical Component
```python
# Transition probability calculation
P(chord_j | chord_i, style) = count(i→j in style) / count(i in style)

# Progression scoring
score = α·transition_prob + β·variety + γ·smoothness
```

#### Neural Component
```python
# When model is loaded:
embeddings = model.encode_progression(progression)
similarity = cosine_similarity(embeddings, database_embeddings)
recommendations = top_k(similarity)
```

### Lick Transposition
```python
# Transpose lick to target key
def transpose_lick(intervals, source_key, target_key):
    shift = (target_key.midi - source_key.midi) % 12
    return [(interval + shift) % 12 for interval in intervals]
```

---

## Key Features Summary

### ✓ Comprehensive Chord Support
- 32+ chord quality types
- All requested chord types (Dm7, GMaj7, 7#9, m7b5, etc.)
- Full support for extended chords (9ths, 11ths, 13ths)
- Altered dominants (7b9, 7#9, 7alt, 7#11)
- Diminished and half-diminished chords

### ✓ Extensive Style Coverage
- 10 musical styles with authentic patterns
- 1,916 total style-specific progressions
- Priority focus on neo soul, blues, progressive metal, rock fusion
- Advanced jazz and blues progressions with extended chords

### ✓ Intelligent Recommendations
- Multi-strategy recommendation engine
- Statistical + neural + rule-based approaches
- Context-aware next chord prediction
- Style-specific lick suggestions with techniques

### ✓ Professional Lick Databases
- 10 blues licks with authentic techniques
- 10 jazz licks covering multiple approaches
- Technique annotations (bends, slides, hammer-ons, etc.)
- Automatic transposition to any key

### ✓ Scalable Architecture
- 50M parameter ultra-large model
- Priority-optimized models (6.4M - 21.4M each)
- Total 70.5M parameters across priority styles
- Advanced training techniques (label smoothing, gradient clipping, warmup)

### ✓ Production Ready
- Model quantization (71.7% size reduction)
- 2-4x faster CPU inference
- Complete API for all features
- Comprehensive test coverage

---

## Future Enhancements

Potential areas for expansion:

1. **Additional Styles**
   - Funk, Latin, Gospel, Country
   - Classical (Bach chorales, Romantic harmony)
   - Modern pop, EDM

2. **Advanced Features**
   - Rhythm pattern recommendations
   - Voicing suggestions (shell, drop-2, drop-3)
   - Reharmonization engine
   - Chord substitution suggester

3. **ML Enhancements**
   - Transformer-XL for longer context
   - Multi-modal learning (audio + symbolic)
   - Style transfer between genres
   - Personalized recommendations via fine-tuning

4. **Integration**
   - MIDI export
   - DAW plugin
   - Web interface
   - Mobile app

---

## Conclusion

The Music Theory ML system now provides comprehensive support for:

- **All requested chord types**: Extended chords, altered dominants, diminished, m7b5
- **Extensive lick databases**: Blues and jazz with authentic techniques and playing styles
- **Intelligent recommendations**: Context-aware suggestions for progressions, melodies, and licks
- **Priority style focus**: Neo soul, blues, progressive metal, rock fusion fully optimized
- **Production-ready**: Quantized models, efficient inference, complete API

The system is ready for professional music composition, education, and performance applications.

---

*Music Theory ML - Advanced Features v2.0*
*Last Updated: 2025*
