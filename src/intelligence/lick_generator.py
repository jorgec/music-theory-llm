"""
ML-Based Melodic Lick/Phrase Generator

Generates melodic phrases (licks) using machine learning models and music theory rules.
Learns from example licks and can generate style-specific melodic patterns.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.theory import Pitch, Chord, Scale, Note, Interval
from src.models import MusicTheoryEncoder
from src.tokenizer import MusicTheoryTokenizer


@dataclass
class MelodicLick:
    """Represents a melodic lick/phrase"""
    pitches: List[Pitch]
    name: str
    style: str  # 'jazz', 'blues', 'rock', 'classical', etc.
    difficulty: int  # 1-5
    description: str
    tags: List[str]  # e.g., ['chromatic', 'arpeggiated', 'bluesy']
    works_over: List[str]  # Chord types this works over


class LickDatabase:
    """Database of melodic licks for training and reference"""

    def __init__(self):
        self.licks = []
        self._initialize_common_licks()

    def _initialize_common_licks(self):
        """Initialize with common licks across styles"""

        # Jazz ii-V-I lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('D4'), Pitch.from_string('F4'),
                Pitch.from_string('A4'), Pitch.from_string('C5'),
                Pitch.from_string('B4'), Pitch.from_string('A4'),
                Pitch.from_string('G4'), Pitch.from_string('E4')
            ],
            name="Classic ii-V-I",
            style="jazz",
            difficulty=3,
            description="Classic ascending arpeggio on ii, resolving down through V to I",
            tags=['arpeggiated', 'bebop', 'ii-V-I'],
            works_over=['Dm7', 'G7', 'Cmaj7']
        ))

        # Blues lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('C4'), Pitch.from_string('Eb4'),
                Pitch.from_string('F4'), Pitch.from_string('Gb4'),
                Pitch.from_string('F4'), Pitch.from_string('Eb4'),
                Pitch.from_string('C4')
            ],
            name="Blues Bend",
            style="blues",
            difficulty=2,
            description="Classic blues lick with minor 3rd and tritone",
            tags=['blues', 'pentatonic', 'bend'],
            works_over=['C7', 'blues']
        ))

        # Chromatic approach lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('F4'), Pitch.from_string('E4'),
                Pitch.from_string('Eb4'), Pitch.from_string('D4'),
                Pitch.from_string('Db4'), Pitch.from_string('C4')
            ],
            name="Chromatic Descent",
            style="jazz",
            difficulty=3,
            description="Chromatic descending line, creates tension",
            tags=['chromatic', 'tension', 'bebop'],
            works_over=['Cmaj7', 'C7']
        ))

        # Rock pentatonic lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('A3'), Pitch.from_string('C4'),
                Pitch.from_string('D4'), Pitch.from_string('E4'),
                Pitch.from_string('G4'), Pitch.from_string('E4'),
                Pitch.from_string('D4'), Pitch.from_string('C4')
            ],
            name="Rock Pentatonic Run",
            style="rock",
            difficulty=2,
            description="Fast pentatonic run, very common in rock",
            tags=['pentatonic', 'fast', 'rock'],
            works_over=['Am', 'C', 'F']
        ))

        # Classical turn ornament
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('C5'), Pitch.from_string('D5'),
                Pitch.from_string('C5'), Pitch.from_string('B4'),
                Pitch.from_string('C5')
            ],
            name="Turn Ornament",
            style="classical",
            difficulty=2,
            description="Classical melodic ornament (turn around main note)",
            tags=['ornament', 'baroque', 'classical'],
            works_over=['C', 'Cmaj7']
        ))

    def add_lick(self, lick: MelodicLick):
        """Add a lick to the database"""
        self.licks.append(lick)

    def get_licks_by_style(self, style: str) -> List[MelodicLick]:
        """Get all licks of a specific style"""
        return [lick for lick in self.licks if lick.style == style]

    def get_licks_by_difficulty(self, difficulty: int) -> List[MelodicLick]:
        """Get licks of specific difficulty"""
        return [lick for lick in self.licks if lick.difficulty == difficulty]

    def get_licks_for_chord(self, chord: Chord) -> List[MelodicLick]:
        """Get licks that work over a specific chord"""
        chord_str = str(chord)
        return [
            lick for lick in self.licks
            if any(c in chord_str for c in lick.works_over) or 'any' in lick.works_over
        ]


class NeuralLickGenerator:
    """
    ML-based melodic lick generator.

    Uses an LSTM or Transformer to learn patterns from lick database
    and generate new licks in various styles.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = None
    ):
        """
        Initialize lick generator.

        Args:
            model_path: Path to trained model
            device: Computing device
        """
        self.tokenizer = MusicTheoryTokenizer()
        self.lick_db = LickDatabase()

        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device

        # Use encoder model for lick generation
        if model_path and Path(model_path).exists():
            self.model = MusicTheoryEncoder.from_pretrained(model_path)
            self.model.to(self.device)
            self.is_trained = True
        else:
            self.model = MusicTheoryEncoder(
                vocab_size=len(self.tokenizer),
                d_model=128,
                num_layers=3,
                pad_token_id=self.tokenizer.pad_token_id
            )
            self.model.to(self.device)
            self.is_trained = False

    def generate_lick(
        self,
        chord: Chord,
        scale: Scale,
        style: str = "jazz",
        length: int = 8,
        difficulty: int = 3,
        temperature: float = 0.9
    ) -> MelodicLick:
        """
        Generate a melodic lick.

        Args:
            chord: Chord to play over
            scale: Scale context
            style: Musical style
            length: Number of notes
            difficulty: Difficulty level (1-5)
            temperature: Creativity (higher = more random)

        Returns:
            Generated MelodicLick
        """
        if not self.is_trained:
            return self._rule_based_generate(chord, scale, style, length, difficulty)

        # TODO: Implement neural generation
        # For now, fall back to rule-based
        return self._rule_based_generate(chord, scale, style, length, difficulty)

    def _rule_based_generate(
        self,
        chord: Chord,
        scale: Scale,
        style: str,
        length: int,
        difficulty: int
    ) -> MelodicLick:
        """
        Generate lick using music theory rules.

        Uses different strategies based on style and difficulty.
        """
        pitches = []
        base_octave = 4

        if style == "jazz":
            pitches = self._generate_jazz_lick(chord, scale, length, base_octave, difficulty)
            tags = ['jazz', 'bebop', 'improvised']

        elif style == "blues":
            pitches = self._generate_blues_lick(chord, scale, length, base_octave, difficulty)
            tags = ['blues', 'pentatonic', 'soulful']

        elif style == "rock":
            pitches = self._generate_rock_lick(chord, scale, length, base_octave, difficulty)
            tags = ['rock', 'pentatonic', 'energetic']

        elif style == "classical":
            pitches = self._generate_classical_lick(chord, scale, length, base_octave, difficulty)
            tags = ['classical', 'melodic', 'structured']

        else:
            # Generic melodic lick
            pitches = self._generate_generic_lick(chord, scale, length, base_octave, difficulty)
            tags = ['melodic', 'general']

        description = self._generate_description(pitches, chord, style)

        return MelodicLick(
            pitches=pitches,
            name=f"Generated {style.title()} Lick",
            style=style,
            difficulty=difficulty,
            description=description,
            tags=tags,
            works_over=[str(chord)]
        )

    def _generate_jazz_lick(
        self,
        chord: Chord,
        scale: Scale,
        length: int,
        octave: int,
        difficulty: int
    ) -> List[Pitch]:
        """Generate jazz-style lick"""
        pitches = []

        # Start on chord tone
        chord_tones = [Pitch(n, octave) for n in chord.notes]
        current = random.choice(chord_tones)
        pitches.append(current)

        for i in range(length - 1):
            # Jazz often uses chromatic approaches and arpeggios

            if difficulty >= 4 and random.random() < 0.3:
                # Chromatic approach to next chord tone
                target = random.choice(chord_tones)
                approach = Pitch(target.note, target.octave).transpose(-1)
                pitches.append(approach)
                if len(pitches) < length:
                    pitches.append(target)
                    current = target
            elif difficulty >= 3 and random.random() < 0.4:
                # Arpeggio motion
                next_tone = chord_tones[(chord_tones.index(current) + 1) % len(chord_tones)]
                pitches.append(next_tone)
                current = next_tone
            else:
                # Scale motion
                step = random.choice([2, 1, -1, -2])  # Steps and skips
                next_pitch = current.transpose(step)

                # Keep in reasonable range
                if 45 <= next_pitch.midi_number <= 80:
                    pitches.append(next_pitch)
                    current = next_pitch

        return pitches[:length]

    def _generate_blues_lick(
        self,
        chord: Chord,
        scale: Scale,
        length: int,
        octave: int,
        difficulty: int
    ) -> List[Pitch]:
        """Generate blues-style lick"""
        # Blues scale: root, m3, 4, b5, 5, m7
        root = chord.root
        blues_intervals = [0, 3, 5, 6, 7, 10]  # Blues scale
        blues_notes = [root.transpose(i) for i in blues_intervals]

        pitches = []
        current = Pitch(root, octave)
        pitches.append(current)

        for i in range(length - 1):
            # Blues licks often use bends, repeated notes, and pentatonic patterns

            if random.random() < 0.3:
                # "Bend" - go up a half step and back down
                bent = current.transpose(1)
                pitches.append(bent)
                if len(pitches) < length:
                    pitches.append(current)
            elif random.random() < 0.4:
                # Jump to another blues scale note
                next_note = random.choice(blues_notes)
                next_pitch = Pitch(next_note, octave if random.random() < 0.7 else octave + 1)
                pitches.append(next_pitch)
                current = next_pitch
            else:
                # Stepwise motion
                step = random.choice([1, 2, -1, -2])
                next_pitch = current.transpose(step)
                pitches.append(next_pitch)
                current = next_pitch

        return pitches[:length]

    def _generate_rock_lick(
        self,
        chord: Chord,
        scale: Scale,
        length: int,
        octave: int,
        difficulty: int
    ) -> List[Pitch]:
        """Generate rock-style lick"""
        # Use pentatonic scale
        root = chord.root
        pentatonic_intervals = [0, 2, 3, 7, 10]  # Minor pentatonic
        pent_notes = [root.transpose(i) for i in pentatonic_intervals]

        pitches = []

        # Rock licks often have fast runs and repeated patterns
        pattern_length = min(4, length)
        pattern = []

        for i in range(pattern_length):
            note = random.choice(pent_notes)
            pitch = Pitch(note, octave if i < 2 else octave + 1)
            pattern.append(pitch)

        # Repeat or vary the pattern
        while len(pitches) < length:
            pitches.extend(pattern)

        return pitches[:length]

    def _generate_classical_lick(
        self,
        chord: Chord,
        scale: Scale,
        length: int,
        octave: int,
        difficulty: int
    ) -> List[Pitch]:
        """Generate classical-style lick"""
        pitches = []

        # Classical melodies are very stepwise
        scale_notes = [Pitch(n, octave) for n in scale.notes]
        current = random.choice(scale_notes[:3])  # Start in lower range
        pitches.append(current)

        for i in range(length - 1):
            # Mostly stepwise motion
            if random.random() < 0.8:  # 80% steps
                step = random.choice([2, 1, -1, -2])
                next_pitch = current.transpose(step)
            else:  # 20% small leaps
                step = random.choice([3, 4, 5, -3, -4])
                next_pitch = current.transpose(step)

                # Resolve leaps by contrary motion
                if i < length - 2 and abs(step) > 2:
                    pitches.append(next_pitch)
                    current = next_pitch
                    # Resolve
                    resolve_step = -2 if step > 0 else 2
                    next_pitch = current.transpose(resolve_step)

            if 50 <= next_pitch.midi_number <= 80:
                pitches.append(next_pitch)
                current = next_pitch

        return pitches[:length]

    def _generate_generic_lick(
        self,
        chord: Chord,
        scale: Scale,
        length: int,
        octave: int,
        difficulty: int
    ) -> List[Pitch]:
        """Generate generic melodic lick"""
        pitches = []
        scale_notes = [Pitch(n, octave) for n in scale.notes]

        current = random.choice(scale_notes)
        pitches.append(current)

        for _ in range(length - 1):
            # Mix of steps and chord tones
            if random.random() < 0.5:
                # Stepwise
                step = random.choice([2, 1, -1, -2])
                next_pitch = current.transpose(step)
            else:
                # Jump to chord tone
                chord_tones = [Pitch(n, octave) for n in chord.notes]
                next_pitch = random.choice(chord_tones)

            if 48 <= next_pitch.midi_number <= 84:
                pitches.append(next_pitch)
                current = next_pitch

        return pitches[:length]

    def _generate_description(self, pitches: List[Pitch], chord: Chord, style: str) -> str:
        """Generate description of the lick"""
        if not pitches:
            return "Empty lick"

        descriptions = []

        # Analyze contour
        if pitches[-1].midi_number > pitches[0].midi_number:
            descriptions.append("ascending")
        elif pitches[-1].midi_number < pitches[0].midi_number:
            descriptions.append("descending")
        else:
            descriptions.append("balanced")

        # Check for chromatic motion
        has_chromatic = any(
            abs(pitches[i + 1].midi_number - pitches[i].midi_number) == 1
            for i in range(len(pitches) - 1)
        )

        if has_chromatic:
            descriptions.append("with chromatic motion")

        # Style-specific description
        descriptions.append(f"in {style} style")

        # Mention chord
        descriptions.append(f"over {chord}")

        return f"{' '.join(descriptions[:3]).capitalize()}, works well {descriptions[-1]}"

    def learn_from_licks(
        self,
        licks: List[MelodicLick],
        num_epochs: int = 20,
        learning_rate: float = 1e-3
    ):
        """
        Train the model on a set of licks.

        Args:
            licks: List of licks to learn from
            num_epochs: Training epochs
            learning_rate: Learning rate
        """
        from torch.utils.data import Dataset, DataLoader
        import torch.optim as optim

        # Create dataset
        class LickDataset(Dataset):
            def __init__(self, licks, tokenizer):
                self.data = []
                for lick in licks:
                    # Encode lick
                    tokens = []
                    for pitch in lick.pitches:
                        tokens.extend(tokenizer.encode_note(pitch.note))

                    if len(tokens) >= 4:
                        self.data.append(tokens)

            def __len__(self):
                return len(self.data)

            def __getitem__(self, idx):
                return torch.tensor(self.data[idx], dtype=torch.long)

        dataset = LickDataset(licks, self.tokenizer)

        if len(dataset) == 0:
            print("No valid licks to train on")
            return

        # Custom collate function
        def collate_fn(batch):
            max_len = max(len(item) for item in batch)
            padded = []
            masks = []

            for item in batch:
                pad_len = max_len - len(item)
                padded_item = torch.cat([item, torch.zeros(pad_len, dtype=torch.long)])
                mask = torch.cat([torch.ones(len(item)), torch.zeros(pad_len)])

                padded.append(padded_item)
                masks.append(mask)

            return torch.stack(padded), torch.stack(masks)

        dataloader = DataLoader(dataset, batch_size=8, shuffle=True, collate_fn=collate_fn)

        # Train
        self.model.train()
        optimizer = optim.AdamW(self.model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss(ignore_index=0)

        print(f"Training on {len(dataset)} licks...")

        for epoch in range(num_epochs):
            total_loss = 0

            for input_ids, attention_mask in dataloader:
                input_ids = input_ids.to(self.device)
                attention_mask = attention_mask.to(self.device)

                optimizer.zero_grad()

                # Forward pass
                logits = self.model(input_ids, attention_mask)

                # Compute loss (predict next token)
                loss = criterion(
                    logits[:, :-1, :].reshape(-1, logits.size(-1)),
                    input_ids[:, 1:].reshape(-1)
                )

                # Backward
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / len(dataloader)
            print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {avg_loss:.4f}")

        self.is_trained = True

    def get_similar_licks(
        self,
        lick: MelodicLick,
        top_k: int = 5
    ) -> List[MelodicLick]:
        """Find similar licks from database"""
        # Simple similarity based on style, difficulty, and tags
        similar = []

        for db_lick in self.lick_db.licks:
            if db_lick == lick:
                continue

            score = 0

            # Same style
            if db_lick.style == lick.style:
                score += 3

            # Similar difficulty
            if abs(db_lick.difficulty - lick.difficulty) <= 1:
                score += 2

            # Common tags
            common_tags = set(db_lick.tags) & set(lick.tags)
            score += len(common_tags)

            similar.append((db_lick, score))

        # Sort by score
        similar.sort(key=lambda x: x[1], reverse=True)

        return [lick for lick, score in similar[:top_k]]
