"""
Neural Network-based Chord Progression Predictor

Uses transformer models to predict next chords and generate progressions
based on learned patterns from training data.
"""

import torch
import torch.nn.functional as F
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models import MusicTheoryTransformer
from src.tokenizer import MusicTheoryTokenizer
from src.theory import Chord, ChordProgression, Scale, Note
from src.theory import chord_from_scale_degree


class NeuralChordPredictor:
    """
    Neural network-based chord progression predictor.

    Uses a trained transformer model to:
    - Predict next chords given a partial progression
    - Generate complete progressions
    - Suggest harmonically coherent continuations
    - Learn from user feedback
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = None
    ):
        """
        Initialize predictor.

        Args:
            model_path: Path to trained model (None for untrained)
            device: 'cuda', 'cpu', or None for auto
        """
        self.tokenizer = MusicTheoryTokenizer()

        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device

        # Load or create model
        if model_path and Path(model_path).exists():
            self.model = MusicTheoryTransformer.from_pretrained(model_path)
            self.model.to(self.device)
            self.model.eval()
            self.is_trained = True
        else:
            self.model = MusicTheoryTransformer(
                vocab_size=len(self.tokenizer),
                d_model=256,
                num_encoder_layers=4,
                num_decoder_layers=4,
                pad_token_id=self.tokenizer.pad_token_id
            )
            self.model.to(self.device)
            self.is_trained = False

    def predict_next_chord(
        self,
        progression: ChordProgression,
        scale: Optional[Scale] = None,
        top_k: int = 5,
        temperature: float = 1.0
    ) -> List[Tuple[Chord, float]]:
        """
        Predict most likely next chords.

        Args:
            progression: Current progression
            scale: Optional scale context
            top_k: Number of predictions to return
            temperature: Sampling temperature (higher = more random)

        Returns:
            List of (Chord, probability) tuples
        """
        if not self.is_trained:
            return self._fallback_predict(progression, scale, top_k)

        self.model.eval()

        with torch.no_grad():
            # Encode progression
            input_ids = self.tokenizer.encode(progression, add_special_tokens=True)
            input_tensor = torch.tensor([input_ids], dtype=torch.long).to(self.device)

            # Encode memory
            memory = self.model.encode(input_tensor)

            # Start with BOS token for target
            tgt = torch.tensor([[self.tokenizer.bos_token_id]], dtype=torch.long).to(self.device)

            # Get next token predictions
            tgt_emb = self.model.embedding(tgt) * torch.sqrt(torch.tensor(self.model.d_model, dtype=torch.float32))
            tgt_emb = self.model.pos_encoder(tgt_emb)

            # Decode
            output = self.model.transformer.decoder(tgt_emb, memory)
            logits = self.model.output_projection(output[:, -1, :])

            # Apply temperature
            logits = logits / temperature

            # Get probabilities
            probs = F.softmax(logits, dim=-1)

            # Get top k predictions
            top_probs, top_indices = torch.topk(probs, min(top_k * 2, probs.size(-1)), dim=-1)

            # Decode tokens to chords
            predictions = []
            for prob, idx in zip(top_probs[0], top_indices[0]):
                token = self.tokenizer.id2token.get(idx.item())
                if token and token not in ['[BOS]', '[EOS]', '[PAD]', '[MASK]', '[SEP]']:
                    try:
                        # Try to parse as chord
                        # This is simplified - in practice, we'd need better chord parsing from tokens
                        if len(predictions) < top_k:
                            predictions.append((token, prob.item()))
                    except:
                        pass

            return predictions[:top_k]

    def predict_next_n_chords(
        self,
        progression: ChordProgression,
        n: int = 4,
        scale: Optional[Scale] = None,
        temperature: float = 0.8,
        num_variations: int = 3
    ) -> List[ChordProgression]:
        """
        Generate multiple possible continuations of n chords.

        Args:
            progression: Starting progression
            n: Number of chords to generate
            scale: Optional scale
            temperature: Sampling temperature
            num_variations: Number of variations to generate

        Returns:
            List of possible continuation progressions
        """
        if not self.is_trained:
            return self._fallback_generate_continuations(progression, n, scale, num_variations)

        variations = []

        for _ in range(num_variations):
            # Start with existing progression
            current_prog = ChordProgression(progression.chords.copy(), scale)

            # Generate n new chords
            for _ in range(n):
                predictions = self.predict_next_chord(
                    current_prog,
                    scale,
                    top_k=5,
                    temperature=temperature
                )

                if predictions:
                    # Sample from predictions
                    import random
                    # Weight by probability
                    chords, probs = zip(*predictions)
                    chosen = random.choices(chords, weights=probs, k=1)[0]

                    # Parse chord and add
                    try:
                        if isinstance(chosen, str):
                            next_chord = Chord.from_symbol(chosen)
                        else:
                            next_chord = chosen

                        current_prog.chords.append(next_chord)
                    except:
                        # If parsing fails, use diatonic fallback
                        if scale:
                            degree = (len(current_prog.chords) % 7) + 1
                            next_chord = chord_from_scale_degree(scale, degree)
                            current_prog.chords.append(next_chord)

            variations.append(current_prog)

        return variations

    def generate_progression(
        self,
        scale: Scale,
        length: int = 4,
        start_chord: Optional[Chord] = None,
        style_hints: Optional[Dict] = None,
        temperature: float = 0.9
    ) -> ChordProgression:
        """
        Generate a complete progression from scratch.

        Args:
            scale: Scale/key for the progression
            length: Number of chords
            start_chord: Optional starting chord (defaults to I)
            style_hints: Optional style parameters
            temperature: Sampling temperature

        Returns:
            Generated chord progression
        """
        if start_chord is None:
            start_chord = chord_from_scale_degree(scale, 1)

        # Start with one chord
        current_prog = ChordProgression([start_chord], scale)

        # Generate remaining chords
        continuations = self.predict_next_n_chords(
            current_prog,
            n=length - 1,
            scale=scale,
            temperature=temperature,
            num_variations=1
        )

        return continuations[0] if continuations else current_prog

    def evaluate_progression_likelihood(
        self,
        progression: ChordProgression
    ) -> float:
        """
        Evaluate how likely a progression is according to the model.

        Returns:
            Likelihood score (0-100)
        """
        if not self.is_trained:
            return 50.0

        self.model.eval()

        with torch.no_grad():
            # Encode progression
            input_ids = self.tokenizer.encode(progression)
            # Split into src and tgt for evaluation
            if len(input_ids) < 4:
                return 50.0

            src = input_ids[:-2]
            tgt = input_ids[1:]

            src_tensor = torch.tensor([src], dtype=torch.long).to(self.device)
            tgt_tensor = torch.tensor([tgt], dtype=torch.long).to(self.device)

            # Compute loss (lower loss = more likely)
            try:
                loss = self.model.get_loss(src_tensor, tgt_tensor)
                # Convert loss to score (lower loss = higher score)
                # Typical loss ranges from 0 to 5+
                score = max(0, min(100, 100 - loss.item() * 15))
                return score
            except:
                return 50.0

    def _fallback_predict(
        self,
        progression: ChordProgression,
        scale: Optional[Scale],
        top_k: int
    ) -> List[Tuple[str, float]]:
        """Fallback to rule-based prediction when model is untrained"""
        if not scale:
            return []

        # Simple diatonic progression rules
        last_chord = progression.chords[-1]
        current_degree = scale.get_degree_of_note(last_chord.root)

        if not current_degree:
            return []

        # Common progressions from each degree
        common_next = {
            1: [(4, 0.3), (5, 0.25), (6, 0.2), (2, 0.15), (1, 0.1)],  # I -> IV, V, vi, ii, I
            2: [(5, 0.6), (1, 0.2), (4, 0.15), (6, 0.05)],  # ii -> V, I, IV, vi
            3: [(6, 0.5), (4, 0.25), (2, 0.15), (1, 0.1)],  # iii -> vi, IV, ii, I
            4: [(5, 0.4), (1, 0.3), (2, 0.2), (7, 0.1)],  # IV -> V, I, ii, vii
            5: [(1, 0.5), (6, 0.25), (4, 0.15), (2, 0.1)],  # V -> I, vi, IV, ii
            6: [(2, 0.3), (4, 0.25), (5, 0.25), (1, 0.2)],  # vi -> ii, IV, V, I
            7: [(1, 0.6), (3, 0.2), (6, 0.15), (5, 0.05)],  # vii -> I, iii, vi, V
        }

        predictions = []
        for next_degree, prob in common_next.get(current_degree, [(1, 1.0)])[:top_k]:
            chord = chord_from_scale_degree(scale, next_degree, seventh=True)
            predictions.append((str(chord), prob))

        return predictions

    def _fallback_generate_continuations(
        self,
        progression: ChordProgression,
        n: int,
        scale: Optional[Scale],
        num_variations: int
    ) -> List[ChordProgression]:
        """Fallback generation using rule-based approach"""
        if not scale:
            return [progression]

        variations = []

        for variation_idx in range(num_variations):
            chords = progression.chords.copy()

            for i in range(n):
                # Get predictions
                current_prog = ChordProgression(chords, scale)
                predictions = self._fallback_predict(current_prog, scale, top_k=5)

                if predictions:
                    # Add some randomness between variations
                    import random
                    chord_strs, probs = zip(*predictions)

                    # Adjust randomness based on variation
                    if variation_idx > 0:
                        # Make later variations more diverse
                        adjusted_probs = [p ** (0.5 + variation_idx * 0.2) for p in probs]
                        total = sum(adjusted_probs)
                        adjusted_probs = [p/total for p in adjusted_probs]
                    else:
                        adjusted_probs = probs

                    chosen = random.choices(chord_strs, weights=adjusted_probs, k=1)[0]
                    next_chord = Chord.from_symbol(chosen)
                    chords.append(next_chord)

            variations.append(ChordProgression(chords, scale))

        return variations

    def fine_tune_on_progressions(
        self,
        progressions: List[ChordProgression],
        num_epochs: int = 10,
        learning_rate: float = 1e-4,
        save_path: Optional[str] = None
    ):
        """
        Fine-tune the model on a set of progressions.

        Args:
            progressions: Training progressions
            num_epochs: Number of training epochs
            learning_rate: Learning rate
            save_path: Optional path to save the fine-tuned model
        """
        from torch.utils.data import DataLoader, Dataset
        import torch.optim as optim

        # Create dataset
        class ProgressionDataset(Dataset):
            def __init__(self, progressions, tokenizer):
                self.data = []
                for prog in progressions:
                    tokens = tokenizer.encode(prog)
                    if len(tokens) >= 4:  # Need minimum length
                        self.data.append(tokens)

            def __len__(self):
                return len(self.data)

            def __getitem__(self, idx):
                tokens = self.data[idx]
                # Split into src and tgt
                mid = len(tokens) // 2
                src = tokens[:mid]
                tgt = tokens[mid:]
                return torch.tensor(src, dtype=torch.long), torch.tensor(tgt, dtype=torch.long)

        dataset = ProgressionDataset(progressions, self.tokenizer)
        dataloader = DataLoader(dataset, batch_size=8, shuffle=True)

        # Set up training
        self.model.train()
        optimizer = optim.AdamW(self.model.parameters(), lr=learning_rate)

        print(f"Fine-tuning on {len(dataset)} progressions...")

        for epoch in range(num_epochs):
            total_loss = 0
            for batch_idx, (src, tgt) in enumerate(dataloader):
                src = src.to(self.device)
                tgt = tgt.to(self.device)

                optimizer.zero_grad()

                # Forward pass
                loss = self.model.get_loss(src, tgt, label_smoothing=0.1)

                # Backward pass
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / len(dataloader)
            print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {avg_loss:.4f}")

        self.is_trained = True

        if save_path:
            self.model.save_pretrained(save_path)
            print(f"Model saved to {save_path}")

    def get_attention_weights(
        self,
        progression: ChordProgression
    ) -> Optional[torch.Tensor]:
        """
        Get attention weights for visualization.

        Returns:
            Attention weights tensor or None if model untrained
        """
        if not self.is_trained:
            return None

        self.model.eval()

        with torch.no_grad():
            input_ids = self.tokenizer.encode(progression)
            input_tensor = torch.tensor([input_ids], dtype=torch.long).to(self.device)

            # This would require modifying the model to return attention weights
            # For now, return None
            # TODO: Implement attention weight extraction

            return None
