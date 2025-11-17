"""
Data Loading Utilities

Load training data from various sources for the Music Theory ML Model.
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.theory import Note, Chord, ChordProgression, Scale


class TrainingDataLoader:
    """Load and process training data from various sources"""

    def __init__(self, cache_dir: str = "data/processed"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load_from_music21_corpus(
        self,
        limit: Optional[int] = None,
        composers: Optional[List[str]] = None
    ) -> List[ChordProgression]:
        """
        Load progressions from music21 corpus.

        Args:
            limit: Maximum number of pieces to load
            composers: List of composers to filter by

        Returns:
            List of chord progressions
        """
        try:
            from music21 import corpus, chord as m21chord, key as m21key, stream
        except ImportError:
            print("music21 not installed. Install with: pip install music21")
            return []

        print("Loading from music21 corpus...")
        progressions = []

        # Search for pieces
        if composers:
            works = []
            for composer in composers:
                works.extend(corpus.search(composer, 'composer'))
        else:
            # Load Bach chorales by default (great for harmony)
            works = corpus.search('bach', 'composer')

        if limit:
            works = works[:limit]

        print(f"Found {len(works)} pieces to process")

        for i, work in enumerate(works):
            try:
                print(f"Processing {i+1}/{len(works)}: {work.sourcePath}...")
                score = work.parse()

                # Analyze key
                try:
                    analyzed_key = score.analyze('key')
                    key_note = Note.from_string(analyzed_key.tonic.name)

                    if 'minor' in analyzed_key.mode:
                        scale = Scale.minor(key_note)
                    else:
                        scale = Scale.major(key_note)
                except:
                    # Default to C major if analysis fails
                    scale = Scale.major(Note.from_string('C'))

                # Extract chords
                chords_m21 = score.flat.getElementsByClass(m21chord.Chord)

                if len(chords_m21) > 0:
                    our_chords = []

                    for chord_m21 in chords_m21[:16]:  # Limit per piece
                        try:
                            # Get root
                            root_name = chord_m21.root().name
                            root = Note.from_string(root_name)

                            # Determine quality
                            # This is simplified - full implementation would check all intervals
                            if chord_m21.isMinorTriad():
                                symbol = f"{root_name}m"
                            elif chord_m21.isDiminishedTriad():
                                symbol = f"{root_name}dim"
                            elif chord_m21.isAugmentedTriad():
                                symbol = f"{root_name}aug"
                            elif chord_m21.isSeventh():
                                if chord_m21.isDominantSeventh():
                                    symbol = f"{root_name}7"
                                elif chord_m21.isMajorSeventh():
                                    symbol = f"{root_name}maj7"
                                elif chord_m21.isMinorSeventh():
                                    symbol = f"{root_name}m7"
                                else:
                                    symbol = root_name
                            else:
                                symbol = root_name

                            our_chord = Chord.from_symbol(symbol)
                            our_chords.append(our_chord)

                        except Exception as e:
                            continue

                    if len(our_chords) >= 3:
                        progression = ChordProgression(our_chords, scale)
                        progressions.append(progression)

            except Exception as e:
                print(f"Error processing {work.sourcePath}: {e}")
                continue

        print(f"Successfully loaded {len(progressions)} progressions from music21")
        return progressions

    def load_from_json(self, filepath: str) -> List[ChordProgression]:
        """
        Load progressions from JSON file.

        Expected format:
        [
          {
            "chords": ["C", "Am", "F", "G"],
            "key": "C major",
            "style": "pop"
          },
          ...
        ]
        """
        print(f"Loading from {filepath}...")
        progressions = []

        with open(filepath, 'r') as f:
            data = json.load(f)

        for item in data:
            try:
                # Parse chords
                chords = [Chord.from_symbol(c) for c in item['chords']]

                # Parse key
                if 'key' in item:
                    key_parts = item['key'].split()
                    root = Note.from_string(key_parts[0])
                    if 'minor' in item['key'].lower():
                        scale = Scale.minor(root)
                    else:
                        scale = Scale.major(root)
                else:
                    scale = None

                progression = ChordProgression(chords, scale)
                progressions.append(progression)

            except Exception as e:
                print(f"Error parsing progression: {e}")
                continue

        print(f"Loaded {len(progressions)} progressions from JSON")
        return progressions

    def load_from_midi(
        self,
        filepath: str,
        extract_method: str = 'chordify'
    ) -> List[ChordProgression]:
        """
        Load progressions from MIDI file.

        Args:
            filepath: Path to MIDI file
            extract_method: 'chordify' or 'analyze'
        """
        try:
            from music21 import converter, chord as m21chord
        except ImportError:
            print("music21 required for MIDI loading")
            return []

        print(f"Loading MIDI: {filepath}...")
        progressions = []

        try:
            score = converter.parse(filepath)

            if extract_method == 'chordify':
                # Use music21's chordify to extract harmony
                chordified = score.chordify()

                chords_m21 = chordified.flat.getElementsByClass(m21chord.Chord)

                our_chords = []
                for chord_m21 in chords_m21[:32]:  # Limit to first 32 chords
                    try:
                        root_name = chord_m21.root().name
                        # Simplified quality detection
                        if chord_m21.isMinorTriad():
                            symbol = f"{root_name}m"
                        elif chord_m21.isMajorTriad():
                            symbol = root_name
                        else:
                            symbol = root_name

                        our_chord = Chord.from_symbol(symbol)
                        our_chords.append(our_chord)
                    except:
                        continue

                if len(our_chords) >= 3:
                    # Analyze key
                    try:
                        analyzed_key = score.analyze('key')
                        key_note = Note.from_string(analyzed_key.tonic.name)
                        if 'minor' in analyzed_key.mode:
                            scale = Scale.minor(key_note)
                        else:
                            scale = Scale.major(key_note)
                    except:
                        scale = Scale.major(Note.from_string('C'))

                    progression = ChordProgression(our_chords, scale)
                    progressions.append(progression)

        except Exception as e:
            print(f"Error loading MIDI: {e}")

        print(f"Extracted {len(progressions)} progressions from MIDI")
        return progressions

    def load_lick_database(self, filepath: Optional[str] = None) -> List[Dict]:
        """
        Load lick database for training.

        Returns:
            List of lick dictionaries
        """
        if filepath and Path(filepath).exists():
            with open(filepath, 'r') as f:
                licks = json.load(f)
            print(f"Loaded {len(licks)} licks from {filepath}")
            return licks

        # Otherwise load from our database
        try:
            from data.lick_database import BluesRockLickDatabase

            db = BluesRockLickDatabase()
            licks_data = []

            for lick in db.licks:
                lick_dict = {
                    'name': lick.name,
                    'style': lick.style,
                    'pitches': [str(p) for p in lick.pitches],
                    'difficulty': lick.difficulty,
                    'tags': lick.tags
                }
                licks_data.append(lick_dict)

            print(f"Loaded {len(licks_data)} licks from built-in database")
            return licks_data

        except Exception as e:
            print(f"Error loading lick database: {e}")
            return []

    def generate_synthetic_progressions(
        self,
        num_progressions: int = 1000,
        styles: Optional[List[str]] = None
    ) -> List[ChordProgression]:
        """
        Generate synthetic progressions using common patterns.

        Args:
            num_progressions: Number to generate
            styles: Styles to generate for

        Returns:
            List of chord progressions
        """
        print(f"Generating {num_progressions} synthetic progressions...")

        if styles is None:
            styles = ['pop', 'jazz', 'rock', 'classical']

        progressions = []

        # Common patterns by style
        patterns = {
            'pop': [
                [1, 5, 6, 4],  # I-V-vi-IV
                [1, 6, 4, 5],  # I-vi-IV-V
                [6, 4, 1, 5],  # vi-IV-I-V
                [1, 4, 5, 1],  # I-IV-V-I
            ],
            'jazz': [
                [2, 5, 1],     # ii-V-I
                [1, 6, 2, 5],  # I-vi-ii-V
                [3, 6, 2, 5],  # iii-vi-ii-V (circle)
                [1, 4, 3, 6, 2, 5, 1],  # Extended jazz progression
            ],
            'rock': [
                [1, 4, 1, 5],  # I-IV-I-V
                [1, 7, 4, 1],  # I-bVII-IV-I
                [1, 5, 4, 1],  # I-V-IV-I
            ],
            'classical': [
                [1, 4, 5, 1],  # I-IV-V-I
                [1, 4, 2, 5, 1],  # I-IV-ii-V-I
                [1, 6, 4, 5, 1],  # I-vi-IV-V-I
            ]
        }

        # Keys to generate in
        keys = [
            ('C', True), ('G', True), ('D', True), ('F', True),
            ('A', False), ('E', False), ('D', False), ('G', False)  # False = minor
        ]

        import random

        for _ in range(num_progressions):
            # Random style
            style = random.choice(styles)

            # Random key
            key_name, is_major = random.choice(keys)
            root = Note.from_string(key_name)

            if is_major:
                scale = Scale.major(root)
            else:
                scale = Scale.minor(root)

            # Random pattern
            pattern = random.choice(patterns.get(style, patterns['pop']))

            # Create progression
            progression = ChordProgression.from_degrees(pattern, scale)
            progressions.append(progression)

        print(f"Generated {len(progressions)} synthetic progressions")
        return progressions

    def save_progressions(
        self,
        progressions: List[ChordProgression],
        output_file: str,
        format: str = 'json'
    ):
        """
        Save progressions to file.

        Args:
            progressions: List of progressions
            output_file: Output file path
            format: 'json' or 'pickle'
        """
        print(f"Saving {len(progressions)} progressions to {output_file}...")

        if format == 'json':
            data = []
            for prog in progressions:
                prog_dict = {
                    'chords': [str(c) for c in prog.chords],
                    'key': f"{prog.scale.root} {'major' if 'MAJOR' in prog.scale.scale_type.name else 'minor'}" if prog.scale else None,
                    'roman_numerals': prog.roman_numerals
                }
                data.append(prog_dict)

            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)

        elif format == 'pickle':
            with open(output_file, 'wb') as f:
                pickle.dump(progressions, f)

        print(f"Saved to {output_file}")

    def load_progressions(self, input_file: str, format: str = 'json') -> List[ChordProgression]:
        """Load progressions from saved file"""

        if format == 'json':
            return self.load_from_json(input_file)
        elif format == 'pickle':
            with open(input_file, 'rb') as f:
                progressions = pickle.load(f)
            print(f"Loaded {len(progressions)} progressions from pickle")
            return progressions

    def create_training_dataset(
        self,
        output_dir: str = "data/processed",
        sources: Optional[List[str]] = None,
        limit_per_source: int = 1000
    ) -> Dict[str, List[ChordProgression]]:
        """
        Create a complete training dataset from multiple sources.

        Args:
            output_dir: Where to save the processed data
            sources: List of sources to use ('music21', 'synthetic', etc.)
            limit_per_source: Max items per source

        Returns:
            Dictionary of progressions by source
        """
        if sources is None:
            sources = ['music21', 'synthetic']

        dataset = {}
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print("=" * 60)
        print("CREATING TRAINING DATASET")
        print("=" * 60)

        # Load from music21
        if 'music21' in sources:
            print("\n1. Loading from music21 corpus...")
            music21_progs = self.load_from_music21_corpus(limit=limit_per_source)
            dataset['music21'] = music21_progs
            self.save_progressions(
                music21_progs,
                str(output_path / 'music21_progressions.json')
            )

        # Generate synthetic
        if 'synthetic' in sources:
            print("\n2. Generating synthetic progressions...")
            synthetic_progs = self.generate_synthetic_progressions(limit_per_source)
            dataset['synthetic'] = synthetic_progs
            self.save_progressions(
                synthetic_progs,
                str(output_path / 'synthetic_progressions.json')
            )

        # Summary
        print("\n" + "=" * 60)
        print("DATASET SUMMARY")
        print("=" * 60)
        total = 0
        for source, progs in dataset.items():
            print(f"{source}: {len(progs)} progressions")
            total += len(progs)

        print(f"\nTotal: {total} progressions")
        print(f"Saved to: {output_path}")

        return dataset


def quick_start_dataset():
    """Create a quick start dataset for immediate training"""
    loader = TrainingDataLoader()

    print("Creating quick start dataset (may take a few minutes)...")

    # Try music21 first
    try:
        progressions = loader.load_from_music21_corpus(limit=50)
    except:
        print("music21 not available, using synthetic only")
        progressions = []

    # Add synthetic
    synthetic = loader.generate_synthetic_progressions(500)
    progressions.extend(synthetic)

    # Save
    loader.save_progressions(
        progressions,
        'data/processed/quickstart_progressions.json'
    )

    print(f"\n✓ Quick start dataset created: {len(progressions)} progressions")
    print("  Saved to: data/processed/quickstart_progressions.json")
    print("\nNow you can train:")
    print("  python train.py --task progression --epochs 10")

    return progressions


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Load training data')
    parser.add_argument('--quick-start', action='store_true',
                        help='Create quick start dataset')
    parser.add_argument('--source', type=str, choices=['music21', 'synthetic', 'all'],
                        default='all', help='Data source')
    parser.add_argument('--limit', type=int, default=1000,
                        help='Limit per source')
    parser.add_argument('--output', type=str, default='data/processed',
                        help='Output directory')

    args = parser.parse_args()

    loader = TrainingDataLoader()

    if args.quick_start:
        quick_start_dataset()
    else:
        sources = ['music21', 'synthetic'] if args.source == 'all' else [args.source]
        dataset = loader.create_training_dataset(
            output_dir=args.output,
            sources=sources,
            limit_per_source=args.limit
        )
