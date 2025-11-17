# Music Theory ML Model

A machine learning model designed to understand and generate music theory concepts.

## Project Overview

This project aims to build a transformer-based model that can:
- Understand music theory concepts (scales, chords, progressions, harmony)
- Generate musically coherent chord progressions
- Analyze harmonic relationships
- Provide music theory explanations and suggestions
- Handle various music notation formats

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
│   ├── training/              # Training scripts
│   │   ├── trainer.py         # Training loop
│   │   └── config.py          # Training configuration
│   ├── theory/                # Music theory representations
│   │   ├── notes.py           # Note and pitch representations
│   │   ├── scales.py          # Scale definitions
│   │   ├── chords.py          # Chord structures
│   │   └── progressions.py   # Chord progression logic
│   ├── tokenizer/             # Music theory tokenization
│   │   └── music_tokenizer.py
│   └── utils/                 # Utility functions
│       ├── midi.py            # MIDI processing
│       └── notation.py        # Music notation helpers
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

## Roadmap

- [x] Project setup
- [ ] Core music theory representation
- [ ] Dataset creation
- [ ] Model architecture
- [ ] Training pipeline
- [ ] Evaluation metrics
- [ ] Pre-trained model release

## License

MIT
