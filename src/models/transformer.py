"""
Transformer model for music theory understanding and generation.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, Dict
import math


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""

    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        # Create positional encoding matrix
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))

        pe = torch.zeros(max_len, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape (batch_size, seq_len, d_model)
        """
        x = x + self.pe[:x.size(1), :]
        return self.dropout(x)


class MusicTheoryTransformer(nn.Module):
    """
    Transformer model for music theory understanding and generation.

    This model can be used for:
    - Chord progression prediction
    - Scale identification
    - Harmonic analysis
    - Music theory question answering
    """

    def __init__(
        self,
        vocab_size: int,
        d_model: int = 512,
        nhead: int = 8,
        num_encoder_layers: int = 6,
        num_decoder_layers: int = 6,
        dim_feedforward: int = 2048,
        dropout: float = 0.1,
        max_seq_length: int = 512,
        pad_token_id: int = 0
    ):
        """
        Initialize the Music Theory Transformer.

        Args:
            vocab_size: Size of the vocabulary
            d_model: Dimension of the model embeddings
            nhead: Number of attention heads
            num_encoder_layers: Number of encoder layers
            num_decoder_layers: Number of decoder layers
            dim_feedforward: Dimension of feedforward network
            dropout: Dropout rate
            max_seq_length: Maximum sequence length
            pad_token_id: Token ID for padding
        """
        super().__init__()

        self.d_model = d_model
        self.vocab_size = vocab_size
        self.pad_token_id = pad_token_id

        # Token embedding
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_token_id)

        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model, max_seq_length, dropout)

        # Transformer
        self.transformer = nn.Transformer(
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=num_encoder_layers,
            num_decoder_layers=num_decoder_layers,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )

        # Output projection
        self.output_projection = nn.Linear(d_model, vocab_size)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize weights with Xavier uniform"""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

    def forward(
        self,
        src: torch.Tensor,
        tgt: torch.Tensor,
        src_mask: Optional[torch.Tensor] = None,
        tgt_mask: Optional[torch.Tensor] = None,
        src_key_padding_mask: Optional[torch.Tensor] = None,
        tgt_key_padding_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass through the transformer.

        Args:
            src: Source sequence (batch_size, src_seq_len)
            tgt: Target sequence (batch_size, tgt_seq_len)
            src_mask: Source attention mask
            tgt_mask: Target attention mask (causal mask)
            src_key_padding_mask: Source padding mask (batch_size, src_seq_len)
            tgt_key_padding_mask: Target padding mask (batch_size, tgt_seq_len)

        Returns:
            Output logits (batch_size, tgt_seq_len, vocab_size)
        """
        # Embed and add positional encoding
        src_emb = self.embedding(src) * math.sqrt(self.d_model)
        src_emb = self.pos_encoder(src_emb)

        tgt_emb = self.embedding(tgt) * math.sqrt(self.d_model)
        tgt_emb = self.pos_encoder(tgt_emb)

        # Generate causal mask for target if not provided
        if tgt_mask is None:
            tgt_mask = self.generate_square_subsequent_mask(tgt.size(1)).to(tgt.device)

        # Pass through transformer
        output = self.transformer(
            src_emb,
            tgt_emb,
            src_mask=src_mask,
            tgt_mask=tgt_mask,
            src_key_padding_mask=src_key_padding_mask,
            tgt_key_padding_mask=tgt_key_padding_mask
        )

        # Project to vocabulary
        logits = self.output_projection(output)

        return logits

    def encode(
        self,
        src: torch.Tensor,
        src_mask: Optional[torch.Tensor] = None,
        src_key_padding_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Encode source sequence.

        Args:
            src: Source sequence (batch_size, src_seq_len)
            src_mask: Source attention mask
            src_key_padding_mask: Source padding mask

        Returns:
            Encoder output (batch_size, src_seq_len, d_model)
        """
        src_emb = self.embedding(src) * math.sqrt(self.d_model)
        src_emb = self.pos_encoder(src_emb)

        # Use only the encoder part
        memory = self.transformer.encoder(
            src_emb,
            mask=src_mask,
            src_key_padding_mask=src_key_padding_mask
        )

        return memory

    @staticmethod
    def generate_square_subsequent_mask(sz: int) -> torch.Tensor:
        """Generate causal mask for decoder"""
        mask = torch.triu(torch.ones(sz, sz), diagonal=1)
        mask = mask.masked_fill(mask == 1, float('-inf'))
        return mask

    @torch.no_grad()
    def generate(
        self,
        src: torch.Tensor,
        max_length: int = 100,
        temperature: float = 1.0,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        eos_token_id: Optional[int] = None
    ) -> torch.Tensor:
        """
        Generate sequence using the model.

        Args:
            src: Source sequence (batch_size, src_seq_len)
            max_length: Maximum generation length
            temperature: Sampling temperature
            top_k: Top-k sampling
            top_p: Nucleus (top-p) sampling
            eos_token_id: End of sequence token ID

        Returns:
            Generated sequence (batch_size, generated_length)
        """
        self.eval()
        batch_size = src.size(0)
        device = src.device

        # Encode source
        memory = self.encode(src)

        # Start with BOS token (assume it's token 1)
        bos_token_id = 1
        generated = torch.full((batch_size, 1), bos_token_id, dtype=torch.long, device=device)

        for _ in range(max_length):
            # Generate causal mask
            tgt_mask = self.generate_square_subsequent_mask(generated.size(1)).to(device)

            # Embed and encode target
            tgt_emb = self.embedding(generated) * math.sqrt(self.d_model)
            tgt_emb = self.pos_encoder(tgt_emb)

            # Decode
            output = self.transformer.decoder(tgt_emb, memory, tgt_mask=tgt_mask)
            logits = self.output_projection(output[:, -1, :])  # Get last token logits

            # Apply temperature
            logits = logits / temperature

            # Apply top-k filtering
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float('-inf')

            # Apply top-p (nucleus) filtering
            if top_p is not None:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

                # Remove tokens with cumulative probability above the threshold
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[:, 1:] = sorted_indices_to_remove[:, :-1].clone()
                sorted_indices_to_remove[:, 0] = 0

                for i in range(batch_size):
                    indices_to_remove = sorted_indices[i, sorted_indices_to_remove[i]]
                    logits[i, indices_to_remove] = float('-inf')

            # Sample next token
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            # Append to generated sequence
            generated = torch.cat([generated, next_token], dim=1)

            # Check for EOS token
            if eos_token_id is not None and (next_token == eos_token_id).all():
                break

        return generated

    def get_loss(
        self,
        src: torch.Tensor,
        tgt: torch.Tensor,
        src_key_padding_mask: Optional[torch.Tensor] = None,
        tgt_key_padding_mask: Optional[torch.Tensor] = None,
        label_smoothing: float = 0.0
    ) -> torch.Tensor:
        """
        Compute cross-entropy loss for training.

        Args:
            src: Source sequence (batch_size, src_seq_len)
            tgt: Target sequence (batch_size, tgt_seq_len)
            src_key_padding_mask: Source padding mask
            tgt_key_padding_mask: Target padding mask
            label_smoothing: Label smoothing factor

        Returns:
            Loss value
        """
        # Target input is tgt without last token
        # Target output is tgt without first token
        tgt_input = tgt[:, :-1]
        tgt_output = tgt[:, 1:]

        # Create padding mask for target input
        if tgt_key_padding_mask is not None:
            tgt_input_padding_mask = tgt_key_padding_mask[:, :-1]
        else:
            tgt_input_padding_mask = None

        # Forward pass
        logits = self.forward(
            src,
            tgt_input,
            src_key_padding_mask=src_key_padding_mask,
            tgt_key_padding_mask=tgt_input_padding_mask
        )

        # Compute loss
        loss = F.cross_entropy(
            logits.reshape(-1, self.vocab_size),
            tgt_output.reshape(-1),
            ignore_index=self.pad_token_id,
            label_smoothing=label_smoothing
        )

        return loss

    def save_pretrained(self, save_path: str):
        """Save model checkpoint"""
        import os
        os.makedirs(save_path, exist_ok=True)

        checkpoint = {
            'model_state_dict': self.state_dict(),
            'vocab_size': self.vocab_size,
            'd_model': self.d_model,
            'pad_token_id': self.pad_token_id
        }

        torch.save(checkpoint, os.path.join(save_path, 'pytorch_model.bin'))

    @classmethod
    def from_pretrained(cls, load_path: str) -> 'MusicTheoryTransformer':
        """Load model checkpoint"""
        import os
        checkpoint = torch.load(os.path.join(load_path, 'pytorch_model.bin'))

        model = cls(
            vocab_size=checkpoint['vocab_size'],
            d_model=checkpoint['d_model'],
            pad_token_id=checkpoint['pad_token_id']
        )

        model.load_state_dict(checkpoint['model_state_dict'])
        return model
