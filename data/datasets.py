"""
Dataset generation and loading utilities for music theory training.
"""

import torch
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict, Tuple, Optional
import random
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.theory import Note, Chord, Scale, ChordProgression, chord_from_scale_degree
from src.theory.scales import ScaleType, COMMON_SCALES
from src.theory.chords import ChordQuality
from src.theory.progressions import COMMON_PROGRESSIONS, get_common_progression
from src.tokenizer import MusicTheoryTokenizer


class ChordProgressionDataset(Dataset):
    """
    Dataset for chord progression prediction tasks.

    Generates chord progressions in various keys and asks the model to predict
    the next chord or complete the progression.
    """

    def __init__(
        self,
        num_samples: int = 10000,
        max_progression_length: int = 8,
        tokenizer: Optional[MusicTheoryTokenizer] = None
    ):
        """
        Initialize the dataset.

        Args:
            num_samples: Number of samples to generate
            max_progression_length: Maximum length of chord progressions
            tokenizer: Tokenizer to use (creates default if None)
        """
        self.num_samples = num_samples
        self.max_progression_length = max_progression_length
        self.tokenizer = tokenizer or MusicTheoryTokenizer()

        # Generate all samples
        self.samples = self._generate_samples()

    def _generate_samples(self) -> List[Dict]:
        """Generate training samples"""
        samples = []

        # All possible root notes
        roots = [Note.from_string(n) for n in ['C', 'D', 'E', 'F', 'G', 'A', 'B',
                                                 'C#', 'D#', 'F#', 'G#', 'A#']]

        for _ in range(self.num_samples):
            # Random key
            root = random.choice(roots)
            is_minor = random.random() < 0.3  # 30% minor keys

            if is_minor:
                scale = Scale.minor(root)
            else:
                scale = Scale.major(root)

            # Choose progression type
            if random.random() < 0.5:
                # Use common progression
                prog_name = random.choice(list(COMMON_PROGRESSIONS.keys()))
                progression = get_common_progression(prog_name, scale)
            else:
                # Generate random diatonic progression
                length = random.randint(4, self.max_progression_length)
                degrees = [random.randint(1, 7) for _ in range(length)]
                progression = ChordProgression.from_degrees(degrees, scale)

            # Create training sample: predict next chord given previous ones
            prog_length = len(progression.chords)
            if prog_length > 1:
                # Split at random point
                split_point = random.randint(1, prog_length - 1)

                input_chords = progression.chords[:split_point]
                target_chord = progression.chords[split_point]

                input_prog = ChordProgression(input_chords, scale)

                sample = {
                    'input': input_prog,
                    'target': target_chord,
                    'scale': scale
                }

                samples.append(sample)

        return samples

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        sample = self.samples[idx]

        # Tokenize input progression
        input_tokens = self.tokenizer.encode(sample['input'])

        # Tokenize target chord
        target_tokens = self.tokenizer.encode(sample['target'])

        return {
            'input_ids': torch.tensor(input_tokens, dtype=torch.long),
            'target_ids': torch.tensor(target_tokens, dtype=torch.long)
        }


class ScaleIdentificationDataset(Dataset):
    """
    Dataset for scale identification tasks.

    Given a sequence of notes, identify the scale.
    """

    def __init__(
        self,
        num_samples: int = 5000,
        tokenizer: Optional[MusicTheoryTokenizer] = None
    ):
        self.num_samples = num_samples
        self.tokenizer = tokenizer or MusicTheoryTokenizer()
        self.samples = self._generate_samples()

    def _generate_samples(self) -> List[Dict]:
        samples = []

        roots = [Note.from_string(n) for n in ['C', 'D', 'E', 'F', 'G', 'A', 'B',
                                                 'C#', 'Eb', 'F#', 'Ab', 'Bb']]

        scale_types = [
            ScaleType.MAJOR,
            ScaleType.NATURAL_MINOR,
            ScaleType.HARMONIC_MINOR,
            ScaleType.DORIAN,
            ScaleType.MIXOLYDIAN,
            ScaleType.PHRYGIAN,
        ]

        for _ in range(self.num_samples):
            root = random.choice(roots)
            scale_type = random.choice(scale_types)
            scale = Scale(root, scale_type)

            # Sample some notes from the scale (not necessarily in order)
            num_notes = random.randint(4, 7)
            notes = random.sample(scale.notes, num_notes)

            sample = {
                'notes': notes,
                'scale': scale
            }

            samples.append(sample)

        return samples

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        sample = self.samples[idx]

        # Tokenize input notes
        input_tokens = []
        for note in sample['notes']:
            input_tokens.extend(self.tokenizer.encode_note(note))

        # Tokenize target scale
        target_tokens = self.tokenizer.encode_scale(sample['scale'])

        # Add special tokens
        input_tokens = [self.tokenizer.bos_token_id] + input_tokens + [self.tokenizer.eos_token_id]
        target_tokens = [self.tokenizer.bos_token_id] + target_tokens + [self.tokenizer.eos_token_id]

        return {
            'input_ids': torch.tensor(input_tokens, dtype=torch.long),
            'target_ids': torch.tensor(target_tokens, dtype=torch.long)
        }


class ChordQualityDataset(Dataset):
    """
    Dataset for chord quality classification.

    Given notes, classify the chord quality.
    """

    def __init__(
        self,
        num_samples: int = 5000,
        tokenizer: Optional[MusicTheoryTokenizer] = None
    ):
        self.num_samples = num_samples
        self.tokenizer = tokenizer or MusicTheoryTokenizer()
        self.samples = self._generate_samples()

        # Create label mapping
        self.qualities = [
            ChordQuality.MAJOR,
            ChordQuality.MINOR,
            ChordQuality.DIMINISHED,
            ChordQuality.AUGMENTED,
            ChordQuality.MAJOR_7,
            ChordQuality.MINOR_7,
            ChordQuality.DOMINANT_7,
        ]
        self.quality_to_label = {q: i for i, q in enumerate(self.qualities)}

    def _generate_samples(self) -> List[Dict]:
        samples = []

        roots = [Note.from_string(n) for n in ['C', 'D', 'E', 'F', 'G', 'A', 'B']]

        for _ in range(self.num_samples):
            root = random.choice(roots)
            quality = random.choice(self.qualities)
            chord = Chord(root, quality)

            sample = {
                'chord': chord,
                'quality': quality
            }

            samples.append(sample)

        return samples

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        sample = self.samples[idx]

        # Tokenize chord notes
        input_tokens = []
        for note in sample['chord'].notes:
            input_tokens.extend(self.tokenizer.encode_note(note))

        input_tokens = [self.tokenizer.bos_token_id] + input_tokens + [self.tokenizer.eos_token_id]

        # Get label
        label = self.quality_to_label[sample['quality']]

        return {
            'input_ids': torch.tensor(input_tokens, dtype=torch.long),
            'label': torch.tensor(label, dtype=torch.long)
        }


def collate_fn_seq2seq(batch: List[Dict]) -> Dict[str, torch.Tensor]:
    """Collate function for sequence-to-sequence tasks"""

    # Get max lengths
    max_input_len = max(item['input_ids'].size(0) for item in batch)
    max_target_len = max(item['target_ids'].size(0) for item in batch)

    # Pad sequences
    input_ids = []
    target_ids = []
    input_masks = []
    target_masks = []

    for item in batch:
        inp = item['input_ids']
        tgt = item['target_ids']

        # Pad input
        inp_pad_len = max_input_len - inp.size(0)
        if inp_pad_len > 0:
            inp = torch.cat([inp, torch.zeros(inp_pad_len, dtype=torch.long)])
        input_ids.append(inp)
        input_masks.append((inp != 0).long())

        # Pad target
        tgt_pad_len = max_target_len - tgt.size(0)
        if tgt_pad_len > 0:
            tgt = torch.cat([tgt, torch.zeros(tgt_pad_len, dtype=torch.long)])
        target_ids.append(tgt)
        target_masks.append((tgt != 0).long())

    return {
        'input_ids': torch.stack(input_ids),
        'target_ids': torch.stack(target_ids),
        'input_mask': torch.stack(input_masks),
        'target_mask': torch.stack(target_masks)
    }


def collate_fn_classification(batch: List[Dict]) -> Dict[str, torch.Tensor]:
    """Collate function for classification tasks"""

    max_len = max(item['input_ids'].size(0) for item in batch)

    input_ids = []
    labels = []
    attention_masks = []

    for item in batch:
        inp = item['input_ids']

        # Pad
        pad_len = max_len - inp.size(0)
        if pad_len > 0:
            inp = torch.cat([inp, torch.zeros(pad_len, dtype=torch.long)])

        input_ids.append(inp)
        attention_masks.append((inp != 0).long())
        labels.append(item['label'])

    return {
        'input_ids': torch.stack(input_ids),
        'attention_mask': torch.stack(attention_masks),
        'labels': torch.stack(labels)
    }


def get_dataloader(
    dataset_type: str = 'progression',
    batch_size: int = 32,
    num_samples: int = 10000,
    shuffle: bool = True,
    num_workers: int = 0
) -> DataLoader:
    """
    Create a dataloader for a specific task.

    Args:
        dataset_type: Type of dataset ('progression', 'scale', 'quality')
        batch_size: Batch size
        num_samples: Number of samples to generate
        shuffle: Whether to shuffle data
        num_workers: Number of worker processes

    Returns:
        DataLoader
    """
    tokenizer = MusicTheoryTokenizer()

    if dataset_type == 'progression':
        dataset = ChordProgressionDataset(num_samples, tokenizer=tokenizer)
        collate = collate_fn_seq2seq
    elif dataset_type == 'scale':
        dataset = ScaleIdentificationDataset(num_samples, tokenizer=tokenizer)
        collate = collate_fn_seq2seq
    elif dataset_type == 'quality':
        dataset = ChordQualityDataset(num_samples, tokenizer=tokenizer)
        collate = collate_fn_classification
    else:
        raise ValueError(f"Unknown dataset type: {dataset_type}")

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=collate,
        num_workers=num_workers
    )
