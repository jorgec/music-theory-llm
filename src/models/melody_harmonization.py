"""
Melody Generation and Harmonization Models

Provides transformer-based models for:
1. Melody generation from chord progressions
2. Harmonization of melodies with chords
3. Multi-task learning combining both
"""

import torch
import torch.nn as nn
from typing import List, Optional, Tuple
from pathlib import Path

from .transformer import MusicTheoryTransformer


class MelodyGenerator(nn.Module):
    """
    Generate melodies conditioned on chord progressions

    Input: Chord progression tokens
    Output: Melody note sequence
    """

    def __init__(
        self,
        vocab_size: int,
        d_model: int = 256,
        num_encoder_layers: int = 4,
        num_decoder_layers: int = 4,
        nhead: int = 8,
        dim_feedforward: int = 1024,
        dropout: float = 0.1,
        max_seq_length: int = 512,
        pad_token_id: int = 0
    ):
        super().__init__()

        self.d_model = d_model
        self.pad_token_id = pad_token_id

        # Embeddings for chords (input) and notes (output)
        self.chord_embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_token_id)
        self.note_embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_token_id)

        # Positional encoding
        self.pos_encoder = nn.Parameter(torch.randn(1, max_seq_length, d_model))

        # Transformer encoder-decoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_encoder_layers)

        decoder_layer = nn.TransformerDecoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_decoder_layers)

        # Output projection
        self.output_projection = nn.Linear(d_model, vocab_size)

        self._init_weights()

    def _init_weights(self):
        """Initialize weights"""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

    def forward(
        self,
        chord_tokens: torch.Tensor,
        melody_tokens: torch.Tensor,
        chord_mask: Optional[torch.Tensor] = None,
        melody_mask: Optional[torch.Tensor] = None,
        tgt_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass

        Args:
            chord_tokens: (batch, chord_seq_len) - chord progression tokens
            melody_tokens: (batch, melody_seq_len) - melody note tokens
            chord_mask: (batch, chord_seq_len) - padding mask for chords
            melody_mask: (batch, melody_seq_len) - padding mask for melody
            tgt_mask: (melody_seq_len, melody_seq_len) - causal mask

        Returns:
            logits: (batch, melody_seq_len, vocab_size)
        """

        # Encode chord progression
        chord_emb = self.chord_embedding(chord_tokens)
        chord_emb = chord_emb + self.pos_encoder[:, :chord_emb.size(1), :]

        memory = self.encoder(
            chord_emb,
            src_key_padding_mask=chord_mask == 0 if chord_mask is not None else None
        )

        # Decode melody
        melody_emb = self.note_embedding(melody_tokens)
        melody_emb = melody_emb + self.pos_encoder[:, :melody_emb.size(1), :]

        output = self.decoder(
            melody_emb,
            memory,
            tgt_mask=tgt_mask,
            tgt_key_padding_mask=melody_mask == 0 if melody_mask is not None else None,
            memory_key_padding_mask=chord_mask == 0 if chord_mask is not None else None
        )

        logits = self.output_projection(output)
        return logits

    def generate_square_subsequent_mask(self, sz: int) -> torch.Tensor:
        """Generate causal mask"""
        mask = torch.triu(torch.ones(sz, sz), diagonal=1).bool()
        return mask

    def generate_melody(
        self,
        chord_tokens: torch.Tensor,
        max_length: int = 64,
        temperature: float = 1.0,
        top_k: int = 10
    ) -> torch.Tensor:
        """
        Generate melody from chord progression

        Args:
            chord_tokens: (batch, chord_seq_len) - chord progression
            max_length: Maximum melody length
            temperature: Sampling temperature
            top_k: Top-k sampling

        Returns:
            melody: (batch, max_length) - generated melody tokens
        """
        self.eval()
        batch_size = chord_tokens.size(0)
        device = chord_tokens.device

        # Start with BOS token (assume token 1)
        melody = torch.ones(batch_size, 1, dtype=torch.long, device=device)

        with torch.no_grad():
            for _ in range(max_length - 1):
                # Create causal mask
                tgt_mask = self.generate_square_subsequent_mask(melody.size(1)).to(device)

                # Forward pass
                logits = self.forward(chord_tokens, melody, tgt_mask=tgt_mask)

                # Get next token probabilities
                next_token_logits = logits[:, -1, :] / temperature

                # Top-k sampling
                if top_k > 0:
                    top_k_logits, top_k_indices = torch.topk(next_token_logits, top_k)
                    probs = torch.softmax(top_k_logits, dim=-1)
                    next_token_idx = torch.multinomial(probs, 1)
                    next_token = top_k_indices.gather(-1, next_token_idx)
                else:
                    probs = torch.softmax(next_token_logits, dim=-1)
                    next_token = torch.multinomial(probs, 1)

                # Append to sequence
                melody = torch.cat([melody, next_token], dim=1)

        return melody

    def save_pretrained(self, save_path: str):
        """Save model"""
        Path(save_path).mkdir(parents=True, exist_ok=True)
        torch.save({
            'model_state_dict': self.state_dict(),
            'd_model': self.d_model,
        }, Path(save_path) / 'pytorch_model.bin')

    @classmethod
    def from_pretrained(cls, load_path: str, vocab_size: int, **kwargs):
        """Load model"""
        checkpoint = torch.load(Path(load_path) / 'pytorch_model.bin')
        model = cls(vocab_size=vocab_size, d_model=checkpoint['d_model'], **kwargs)
        model.load_state_dict(checkpoint['model_state_dict'])
        return model


class HarmonizationModel(nn.Module):
    """
    Generate chord progressions for melodies

    Input: Melody note sequence
    Output: Chord progression tokens
    """

    def __init__(
        self,
        vocab_size: int,
        d_model: int = 256,
        num_encoder_layers: int = 4,
        num_decoder_layers: int = 4,
        nhead: int = 8,
        dim_feedforward: int = 1024,
        dropout: float = 0.1,
        max_seq_length: int = 512,
        pad_token_id: int = 0
    ):
        super().__init__()

        self.d_model = d_model
        self.pad_token_id = pad_token_id

        # Embeddings
        self.note_embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_token_id)
        self.chord_embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_token_id)

        # Positional encoding
        self.pos_encoder = nn.Parameter(torch.randn(1, max_seq_length, d_model))

        # Transformer
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_encoder_layers)

        decoder_layer = nn.TransformerDecoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_decoder_layers)

        # Output projection
        self.output_projection = nn.Linear(d_model, vocab_size)

        self._init_weights()

    def _init_weights(self):
        """Initialize weights"""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

    def forward(
        self,
        melody_tokens: torch.Tensor,
        chord_tokens: torch.Tensor,
        melody_mask: Optional[torch.Tensor] = None,
        chord_mask: Optional[torch.Tensor] = None,
        tgt_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass"""

        # Encode melody
        melody_emb = self.note_embedding(melody_tokens)
        melody_emb = melody_emb + self.pos_encoder[:, :melody_emb.size(1), :]

        memory = self.encoder(
            melody_emb,
            src_key_padding_mask=melody_mask == 0 if melody_mask is not None else None
        )

        # Decode chords
        chord_emb = self.chord_embedding(chord_tokens)
        chord_emb = chord_emb + self.pos_encoder[:, :chord_emb.size(1), :]

        output = self.decoder(
            chord_emb,
            memory,
            tgt_mask=tgt_mask,
            tgt_key_padding_mask=chord_mask == 0 if chord_mask is not None else None,
            memory_key_padding_mask=melody_mask == 0 if melody_mask is not None else None
        )

        logits = self.output_projection(output)
        return logits

    def generate_square_subsequent_mask(self, sz: int) -> torch.Tensor:
        """Generate causal mask"""
        mask = torch.triu(torch.ones(sz, sz), diagonal=1).bool()
        return mask

    def harmonize(
        self,
        melody_tokens: torch.Tensor,
        max_chord_length: int = 16,
        temperature: float = 1.0
    ) -> torch.Tensor:
        """
        Generate chord progression for melody

        Args:
            melody_tokens: (batch, melody_seq_len) - melody to harmonize
            max_chord_length: Maximum number of chords
            temperature: Sampling temperature

        Returns:
            chords: (batch, max_chord_length) - chord progression
        """
        self.eval()
        batch_size = melody_tokens.size(0)
        device = melody_tokens.device

        # Start with BOS token
        chords = torch.ones(batch_size, 1, dtype=torch.long, device=device)

        with torch.no_grad():
            for _ in range(max_chord_length - 1):
                tgt_mask = self.generate_square_subsequent_mask(chords.size(1)).to(device)

                logits = self.forward(melody_tokens, chords, tgt_mask=tgt_mask)
                next_chord_logits = logits[:, -1, :] / temperature

                probs = torch.softmax(next_chord_logits, dim=-1)
                next_chord = torch.multinomial(probs, 1)

                chords = torch.cat([chords, next_chord], dim=1)

        return chords

    def save_pretrained(self, save_path: str):
        """Save model"""
        Path(save_path).mkdir(parents=True, exist_ok=True)
        torch.save({
            'model_state_dict': self.state_dict(),
            'd_model': self.d_model,
        }, Path(save_path) / 'pytorch_model.bin')

    @classmethod
    def from_pretrained(cls, load_path: str, vocab_size: int, **kwargs):
        """Load model"""
        checkpoint = torch.load(Path(load_path) / 'pytorch_model.bin')
        model = cls(vocab_size=vocab_size, d_model=checkpoint['d_model'], **kwargs)
        model.load_state_dict(checkpoint['model_state_dict'])
        return model
