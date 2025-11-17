"""
Encoder-only model for music theory classification and analysis tasks.
"""

import torch
import torch.nn as nn
from typing import Optional
from .transformer import PositionalEncoding


class MusicTheoryEncoder(nn.Module):
    """
    Encoder-only transformer for music theory understanding tasks.

    Suitable for:
    - Chord classification
    - Scale identification
    - Harmonic function prediction
    - Music theory concept classification
    """

    def __init__(
        self,
        vocab_size: int,
        d_model: int = 512,
        nhead: int = 8,
        num_layers: int = 6,
        dim_feedforward: int = 2048,
        dropout: float = 0.1,
        max_seq_length: int = 512,
        pad_token_id: int = 0,
        num_classes: Optional[int] = None
    ):
        """
        Initialize the encoder.

        Args:
            vocab_size: Size of the vocabulary
            d_model: Dimension of the model embeddings
            nhead: Number of attention heads
            num_layers: Number of encoder layers
            dim_feedforward: Dimension of feedforward network
            dropout: Dropout rate
            max_seq_length: Maximum sequence length
            pad_token_id: Token ID for padding
            num_classes: Number of output classes (None for sequence output)
        """
        super().__init__()

        self.d_model = d_model
        self.vocab_size = vocab_size
        self.pad_token_id = pad_token_id
        self.num_classes = num_classes

        # Token embedding
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_token_id)

        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model, max_seq_length, dropout)

        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # Classification head (if num_classes is specified)
        if num_classes is not None:
            self.classifier = nn.Sequential(
                nn.Linear(d_model, d_model // 2),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(d_model // 2, num_classes)
            )
        else:
            self.classifier = None

        # Output projection for sequence tasks
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
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        output_hidden_states: bool = False
    ) -> torch.Tensor:
        """
        Forward pass through the encoder.

        Args:
            input_ids: Input token IDs (batch_size, seq_len)
            attention_mask: Attention mask (batch_size, seq_len)
            output_hidden_states: Whether to return hidden states

        Returns:
            If num_classes is set: class logits (batch_size, num_classes)
            Otherwise: sequence logits (batch_size, seq_len, vocab_size)
        """
        # Create padding mask (True for padding positions)
        if attention_mask is not None:
            key_padding_mask = (attention_mask == 0)
        else:
            key_padding_mask = (input_ids == self.pad_token_id)

        # Embed and add positional encoding
        embeddings = self.embedding(input_ids) * torch.sqrt(torch.tensor(self.d_model, dtype=torch.float32))
        embeddings = self.pos_encoder(embeddings)

        # Pass through encoder
        encoder_output = self.encoder(embeddings, src_key_padding_mask=key_padding_mask)

        if output_hidden_states:
            return encoder_output

        # For classification, use [CLS] token (first token) or mean pooling
        if self.classifier is not None:
            # Mean pooling over non-padded tokens
            if attention_mask is not None:
                mask_expanded = attention_mask.unsqueeze(-1).expand(encoder_output.size()).float()
                sum_embeddings = torch.sum(encoder_output * mask_expanded, dim=1)
                sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
                pooled = sum_embeddings / sum_mask
            else:
                pooled = encoder_output.mean(dim=1)

            logits = self.classifier(pooled)
            return logits

        # For sequence tasks, project each token
        logits = self.output_projection(encoder_output)
        return logits

    def get_embeddings(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Get contextual embeddings for input sequence.

        Args:
            input_ids: Input token IDs (batch_size, seq_len)
            attention_mask: Attention mask (batch_size, seq_len)

        Returns:
            Contextualized embeddings (batch_size, seq_len, d_model)
        """
        return self.forward(input_ids, attention_mask, output_hidden_states=True)

    def predict(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Make predictions (for classification tasks).

        Args:
            input_ids: Input token IDs (batch_size, seq_len)
            attention_mask: Attention mask (batch_size, seq_len)

        Returns:
            Predicted class indices (batch_size,)
        """
        self.eval()
        with torch.no_grad():
            logits = self.forward(input_ids, attention_mask)
            predictions = torch.argmax(logits, dim=-1)
        return predictions

    def save_pretrained(self, save_path: str):
        """Save model checkpoint"""
        import os
        os.makedirs(save_path, exist_ok=True)

        checkpoint = {
            'model_state_dict': self.state_dict(),
            'vocab_size': self.vocab_size,
            'd_model': self.d_model,
            'pad_token_id': self.pad_token_id,
            'num_classes': self.num_classes
        }

        torch.save(checkpoint, os.path.join(save_path, 'pytorch_model.bin'))

    @classmethod
    def from_pretrained(cls, load_path: str) -> 'MusicTheoryEncoder':
        """Load model checkpoint"""
        import os
        checkpoint = torch.load(os.path.join(load_path, 'pytorch_model.bin'))

        model = cls(
            vocab_size=checkpoint['vocab_size'],
            d_model=checkpoint['d_model'],
            pad_token_id=checkpoint['pad_token_id'],
            num_classes=checkpoint.get('num_classes')
        )

        model.load_state_dict(checkpoint['model_state_dict'])
        return model
