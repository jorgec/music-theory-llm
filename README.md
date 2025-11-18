# Music Theory ML Model

A machine learning model designed to understand and generate music theory concepts.

## Project Overview

This project provides a comprehensive music theory ML framework with:
- **Advanced ML Models**: Transformer-based architecture for chord progression prediction
- **Intelligent Analysis**: Rule-based validation, statistical analysis, and neural prediction
- **Melody Generation**: ML-based lick/phrase generation in multiple styles
- **Adaptive Learning**: Personalized learning paths with progress tracking
- **Interactive Features**: Auto-generated exercises and theory explanations
- **Continuous Improvement**: Feedback collection and model fine-tuning

## 🎵 What Makes This Special?

- **Multi-Layered Intelligence**: Combines music theory rules, statistical analysis, and deep learning
- **Educational Focus**: Built-in learning paths, exercises, and clear explanations
- **Production-Ready**: Comprehensive validation, ranking, and feedback systems
- **Extensible**: Easy to customize and fine-tune on your own data

## Project Structure

```
music-theory-llm/
├── data/                      # Training and evaluation datasets
│   ├── raw/                   # Raw music theory data
│   ├── processed/             # Preprocessed training data
│   └── datasets.py            # Dataset loading utilities
├── src/
│   ├── models/                # Model architectures
│   │   ├── transformer.py     # Transformer implementation
│   │   └── music_encoder.py  # Music theory encoding
│   ├── theory/                # Music theory representations
│   │   ├── notes.py           # Note and pitch representations
│   │   ├── scales.py          # Scale definitions
│   │   ├── chords.py          # Chord structures
│   │   └── progressions.py   # Chord progression logic
│   ├── tokenizer/             # Music theory tokenization
│   │   └── music_tokenizer.py
│   ├── utils/                 # Melody and harmony utilities
│   │   ├── melody.py          # Melody suggestions
│   │   └── harmony.py         # Harmonic analysis
│   └── intelligence/          # 🧠 Intelligence system
│       ├── validators.py      # Music theory rule validation
│       ├── evaluator.py       # Intelligent ranking
│       ├── statistical_analyzer.py  # Statistical progression analysis
│       ├── neural_predictor.py      # Neural chord prediction
│       ├── lick_generator.py        # ML-based lick generation
│       ├── learning_path.py         # Adaptive learning paths
│       ├── explainer.py            # Theory explanations
│       ├── exercises.py            # Exercise generation
│       └── feedback.py             # Feedback collection
├── notebooks/                 # Jupyter notebooks for experimentation
├── tests/                     # Unit tests
├── requirements.txt           # Python dependencies
└── train.py                   # Main training script
```

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Training
```bash
python train.py --config configs/default.yaml
```

### Inference
```python
from src.models import MusicTheoryModel

model = MusicTheoryModel.from_pretrained('checkpoints/best_model')
result = model.generate_progression(key='C', style='jazz')
```

## Features

- **Music Theory Knowledge**: Comprehensive representation of scales, modes, chords, and progressions
- **Transformer Architecture**: State-of-the-art attention-based model
- **Multiple Training Tasks**:
  - Chord progression prediction
  - Scale degree identification
  - Harmonic function analysis
  - Voice leading optimization
- **Flexible Tokenization**: Convert music theory concepts to/from tokens

## 📊 Training Data

See **[TRAINING_DATA.md](TRAINING_DATA.md)** for comprehensive data sources including:

**Chord Progression Datasets:**
- music21 corpus (1,000+ classical pieces)
- McGill Billboard Dataset (1,000 pop songs)
- Lakh MIDI Dataset (176,000+ MIDI files)
- iReal Pro (10,000+ jazz standards)
- Hooktheory TheoryTab (40,000+ analyzed songs)

**Quick Start:**
```bash
# Prepare training data (interactive script)
python scripts/prepare_training_data.py

# Or quick start dataset
python -c "from data.data_loaders import quick_start_dataset; quick_start_dataset()"

# Train on the data
python train.py --task progression --epochs 20
```

## 🎸 Advanced Guitar Lick Database

**156 sophisticated guitar licks from legendary players spanning multiple decades:**
- **Blues**: BB King, Albert King, Muddy Waters, Stevie Ray Vaughan, T-Bone Walker, John Mayer, Joe Bonamassa, Eric Johnson, Josh Smith
- **Rock Fusion**: Guthrie Govan, Greg Howe, Frank Gambale, Allan Holdsworth, Scott Henderson
- **Neo Soul**: Jack Gardiner, Mateus Asato, Cory Wong, Tom Misch
- **Jazz**: Pat Metheny, Wes Montgomery, Charlie Christian, Mike Stern
- **Progressive Metal**: I Built the Sky, Plini, Animals as Leaders, Polyphia
- **Plus**: 5 additional styles (Soul, Funk, Pop Rock, Pop, R&B)

**Features:**
- **51.3% advanced licks** - mastery-focused system
- Chromatic approaches and extensions (9ths, 11ths, 13ths)
- Complete harmonic context (chord progressions, functional harmony)
- Target notes and theory explanations
- Bebop vocabulary, altered harmony, and fusion techniques
- Technique tags (bends, vibrato, slides, tapping, sweeps, legato, etc.)
- Artist-specific cadence patterns

**Usage:**
```python
from data.lick_database import BluesRockLickDatabase

db = BluesRockLickDatabase()
hendrix_licks = db.get_licks_by_guitarist("hendrix")
sixties_licks = db.get_licks_by_era("60s")
bend_licks = db.get_technique_licks("bend")
```

**Demo:**
```bash
python examples/lick_database_demo.py
```

## 🧠 Intelligence System

See **[INTELLIGENCE.md](INTELLIGENCE.md)** for detailed documentation on:

- **Validation**: Rule-based checking with scoring (0-100)
- **Ranking**: Multi-criteria intelligent evaluation
- **Statistical Analysis**: Learn patterns from progression datasets
- **Neural Prediction**: Deep learning for chord prediction
- **Lick Generation**: ML-based melodic phrase generation
- **Learning Paths**: Adaptive curriculum with progress tracking
- **Explanations**: Educational theory explanations
- **Exercises**: Auto-generated practice problems
- **Feedback**: Continuous improvement through user feedback

## Examples

```bash
# Run all demos
python examples/basic_usage.py                    # Music theory basics
python examples/melody_suggestions_demo.py        # Melody generation
python examples/harmonic_analysis_demo.py         # Advanced harmony
python examples/intelligence_demo.py              # 🆕 All intelligence features
python examples/lick_database_demo.py             # 🆕 Guitar lick database
```

## Roadmap

- [x] Core music theory representation
- [x] Transformer model architecture
- [x] Training pipeline
- [x] Melody suggestion system
- [x] Harmonic analysis tools
- [x] 🆕 Rule-based validation
- [x] 🆕 Statistical progression analysis
- [x] 🆕 Neural chord prediction
- [x] 🆕 ML-based lick generation
- [x] 🆕 Adaptive learning system
- [ ] Pre-trained models
- [ ] Audio generation
- [ ] Real-time collaboration

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide with examples
- **[INTELLIGENCE.md](INTELLIGENCE.md)** - Intelligence system documentation
- **[examples/](examples/)** - Comprehensive demos

## License

MIT
