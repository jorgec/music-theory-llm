"""
Music Theory Tokenizer

Converts music theory concepts (notes, chords, progressions) to/from token sequences
that can be processed by transformer models.
"""

from typing import List, Dict, Optional, Union, Tuple
import json
from pathlib import Path
from ..theory import Note, Chord, Scale, ChordProgression


class MusicTheoryTokenizer:
    """
    Tokenizer for music theory concepts.

    Vocabulary:
    - Special tokens: [PAD], [BOS], [EOS], [MASK], [SEP]
    - Notes: C, C#, D, ..., B
    - Chord qualities: major, minor, dim, aug, 7, maj7, m7, etc.
    - Scale types: major_scale, minor_scale, dorian, etc.
    - Functional tokens: tonic, dominant, subdominant
    - Context tokens: key:, chord:, progression:, scale:
    """

    def __init__(self, vocab_file: Optional[str] = None):
        """
        Initialize the tokenizer.

        Args:
            vocab_file: Optional path to a vocabulary file
        """
        if vocab_file and Path(vocab_file).exists():
            self.load_vocab(vocab_file)
        else:
            self._build_default_vocab()

    def _build_default_vocab(self):
        """Build the default vocabulary"""

        # Special tokens
        special_tokens = [
            '[PAD]', '[BOS]', '[EOS]', '[MASK]', '[SEP]', '[UNK]'
        ]

        # Note names
        notes = [
            'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F',
            'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'
        ]

        # Chord qualities
        chord_qualities = [
            'major', 'minor', 'dim', 'aug', 'sus2', 'sus4',
            '7', 'maj7', 'm7', 'dim7', 'm7b5', 'aug7', 'mMaj7',
            '9', 'maj9', 'm9', '6', 'm6', '5'
        ]

        # Scale types
        scale_types = [
            'major_scale', 'natural_minor_scale', 'harmonic_minor_scale',
            'melodic_minor_scale', 'ionian', 'dorian', 'phrygian',
            'lydian', 'mixolydian', 'aeolian', 'locrian',
            'major_pentatonic', 'minor_pentatonic', 'blues_scale'
        ]

        # Harmonic functions
        functions = ['tonic', 'dominant', 'subdominant']

        # Roman numerals
        roman_numerals = [
            'I', 'II', 'III', 'IV', 'V', 'VI', 'VII',
            'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii'
        ]

        # Context markers
        context_markers = [
            'key:', 'chord:', 'progression:', 'scale:',
            'degree:', 'function:', 'cadence:', 'note:'
        ]

        # Cadence types
        cadences = [
            'authentic_cadence', 'plagal_cadence',
            'half_cadence', 'deceptive_cadence'
        ]

        # Additional music theory terms
        theory_terms = [
            'root', 'third', 'fifth', 'seventh', 'ninth',
            'inversion', 'first_inversion', 'second_inversion',
            'parallel', 'relative', 'leading_tone', 'tonic_note',
            'mediant', 'subdominant_note', 'dominant_note', 'submediant'
        ]

        # Combine all tokens
        all_tokens = (
            special_tokens + notes + chord_qualities + scale_types +
            functions + roman_numerals + context_markers +
            cadences + theory_terms
        )

        # Create token to ID mapping
        self.token2id = {token: idx for idx, token in enumerate(all_tokens)}
        self.id2token = {idx: token for token, idx in self.token2id.items()}
        self.vocab_size = len(all_tokens)

        # Store special token IDs
        self.pad_token_id = self.token2id['[PAD]']
        self.bos_token_id = self.token2id['[BOS]']
        self.eos_token_id = self.token2id['[EOS]']
        self.mask_token_id = self.token2id['[MASK]']
        self.sep_token_id = self.token2id['[SEP]']
        self.unk_token_id = self.token2id['[UNK]']

    def encode_note(self, note: Note) -> List[int]:
        """Encode a note to token IDs"""
        note_str = str(note)
        token_id = self.token2id.get(note_str, self.unk_token_id)
        return [token_id]

    def encode_chord(self, chord: Chord) -> List[int]:
        """Encode a chord to token IDs"""
        tokens = []

        # Add root note
        root_str = str(chord.root)
        tokens.append(self.token2id.get(root_str, self.unk_token_id))

        # Add quality
        from ..theory.chords import CHORD_SYMBOLS
        quality_str = CHORD_SYMBOLS.get(chord.quality, '').lower()
        if not quality_str:
            quality_str = 'major'

        # Map common quality strings to vocab
        quality_map = {
            '': 'major',
            'm': 'minor',
            'dim': 'dim',
            'aug': 'aug',
            'sus2': 'sus2',
            'sus4': 'sus4',
            '7': '7',
            'maj7': 'maj7',
            'm7': 'm7',
            'dim7': 'dim7',
            'm7b5': 'm7b5',
        }

        quality_token = quality_map.get(quality_str, quality_str)
        tokens.append(self.token2id.get(quality_token, self.unk_token_id))

        return tokens

    def encode_scale(self, scale: Scale) -> List[int]:
        """Encode a scale to token IDs"""
        tokens = []

        # Add root note
        root_str = str(scale.root)
        tokens.append(self.token2id.get(root_str, self.unk_token_id))

        # Add scale type
        scale_type_str = scale.scale_type.name.lower() + '_scale'
        tokens.append(self.token2id.get(scale_type_str, self.unk_token_id))

        return tokens

    def encode_progression(self, progression: ChordProgression) -> List[int]:
        """Encode a chord progression to token IDs"""
        tokens = []

        # Add key information if available
        if progression.scale:
            tokens.append(self.token2id['key:'])
            tokens.extend(self.encode_scale(progression.scale))

        # Add progression marker
        tokens.append(self.token2id['progression:'])

        # Add each chord
        for i, chord in enumerate(progression.chords):
            if i > 0:
                tokens.append(self.token2id['[SEP]'])
            tokens.extend(self.encode_chord(chord))

        return tokens

    def encode(
        self,
        obj: Union[Note, Chord, Scale, ChordProgression, str],
        add_special_tokens: bool = True
    ) -> List[int]:
        """
        Encode a music theory object or string to token IDs.

        Args:
            obj: Note, Chord, Scale, ChordProgression, or string
            add_special_tokens: Whether to add [BOS] and [EOS] tokens

        Returns:
            List of token IDs
        """
        if isinstance(obj, Note):
            tokens = self.encode_note(obj)
        elif isinstance(obj, Chord):
            tokens = self.encode_chord(obj)
        elif isinstance(obj, Scale):
            tokens = self.encode_scale(obj)
        elif isinstance(obj, ChordProgression):
            tokens = self.encode_progression(obj)
        elif isinstance(obj, str):
            tokens = self.encode_string(obj)
        else:
            raise ValueError(f"Cannot encode object of type {type(obj)}")

        if add_special_tokens:
            tokens = [self.bos_token_id] + tokens + [self.eos_token_id]

        return tokens

    def encode_string(self, text: str) -> List[int]:
        """Encode a string by splitting on whitespace and looking up tokens"""
        tokens = []
        for word in text.split():
            token_id = self.token2id.get(word, self.unk_token_id)
            tokens.append(token_id)
        return tokens

    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Decode token IDs back to a string.

        Args:
            token_ids: List of token IDs
            skip_special_tokens: Whether to skip special tokens in output

        Returns:
            Decoded string
        """
        special_ids = {
            self.pad_token_id, self.bos_token_id, self.eos_token_id,
            self.mask_token_id, self.sep_token_id
        }

        tokens = []
        for token_id in token_ids:
            if skip_special_tokens and token_id in special_ids:
                continue
            token = self.id2token.get(token_id, '[UNK]')
            tokens.append(token)

        return ' '.join(tokens)

    def batch_encode(
        self,
        objects: List[Union[Note, Chord, Scale, ChordProgression, str]],
        padding: bool = True,
        max_length: Optional[int] = None,
        add_special_tokens: bool = True
    ) -> Dict[str, List[List[int]]]:
        """
        Encode a batch of objects.

        Args:
            objects: List of objects to encode
            padding: Whether to pad sequences to the same length
            max_length: Maximum sequence length (None for no limit)
            add_special_tokens: Whether to add special tokens

        Returns:
            Dictionary with 'input_ids' and 'attention_mask'
        """
        # Encode all objects
        encoded = [self.encode(obj, add_special_tokens) for obj in objects]

        # Determine max length
        if max_length is None:
            max_length = max(len(seq) for seq in encoded)

        # Truncate and pad
        input_ids = []
        attention_masks = []

        for seq in encoded:
            # Truncate
            if len(seq) > max_length:
                seq = seq[:max_length]

            # Create attention mask (1 for real tokens, 0 for padding)
            attention_mask = [1] * len(seq)

            # Pad
            if padding and len(seq) < max_length:
                padding_length = max_length - len(seq)
                seq = seq + [self.pad_token_id] * padding_length
                attention_mask = attention_mask + [0] * padding_length

            input_ids.append(seq)
            attention_masks.append(attention_mask)

        return {
            'input_ids': input_ids,
            'attention_mask': attention_masks
        }

    def save_vocab(self, vocab_file: str):
        """Save vocabulary to a JSON file"""
        vocab_data = {
            'token2id': self.token2id,
            'special_tokens': {
                'pad': self.pad_token_id,
                'bos': self.bos_token_id,
                'eos': self.eos_token_id,
                'mask': self.mask_token_id,
                'sep': self.sep_token_id,
                'unk': self.unk_token_id
            }
        }

        with open(vocab_file, 'w') as f:
            json.dump(vocab_data, f, indent=2)

    def load_vocab(self, vocab_file: str):
        """Load vocabulary from a JSON file"""
        with open(vocab_file, 'r') as f:
            vocab_data = json.load(f)

        self.token2id = vocab_data['token2id']
        self.id2token = {int(idx): token for token, idx in self.token2id.items()}
        self.vocab_size = len(self.token2id)

        special = vocab_data['special_tokens']
        self.pad_token_id = special['pad']
        self.bos_token_id = special['bos']
        self.eos_token_id = special['eos']
        self.mask_token_id = special['mask']
        self.sep_token_id = special['sep']
        self.unk_token_id = special['unk']

    def __len__(self) -> int:
        return self.vocab_size
