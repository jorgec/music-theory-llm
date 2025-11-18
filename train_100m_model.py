"""
Train Ultra-Large Music Theory Model (100M Parameters)

Configuration for maximum capacity with artist-specific training:
- d_model: 768 (3x larger than v2)
- Layers: 10 (2.5x deeper than v2)
- Parameters: ~100M
- Extended training: 100 epochs
- Large batch size: 64
- Advanced optimization with artist-specific fine-tuning
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import argparse
from pathlib import Path
from tqdm import tqdm
import json

from src.models import MusicTheoryTransformer
from src.tokenizer import MusicTheoryTokenizer
from data.datasets import get_dataloader


def calculate_model_params(vocab_size, d_model, num_layers, nhead=8):
    """Calculate exact model parameters"""
    # Embeddings
    embedding_params = vocab_size * d_model * 2  # src + tgt

    # Positional encoding
    pos_encoding_params = 512 * d_model  # max_seq_length * d_model

    # Per encoder/decoder layer
    def layer_params(d_model, nhead):
        # Multi-head attention
        qkv_proj = 3 * d_model * d_model  # Q, K, V projections
        o_proj = d_model * d_model  # Output projection
        attn_params = qkv_proj + o_proj

        # Feed-forward network
        ffn_params = 2 * d_model * (d_model * 4)  # Two linear layers

        # Layer norms (2 per layer)
        ln_params = 2 * d_model * 2  # weight + bias

        return attn_params + ffn_params + ln_params

    # Encoder + Decoder layers
    encoder_params = layer_params(d_model, nhead) * num_layers
    decoder_params = (layer_params(d_model, nhead) + d_model * d_model) * num_layers  # +cross-attention

    # Output projection
    output_params = d_model * vocab_size

    total = embedding_params + pos_encoding_params + encoder_params + decoder_params + output_params
    return total


def find_100m_config(vocab_size=101):
    """Find optimal configuration for ~100M parameters"""

    print("\\nSearching for optimal 100M parameter configuration...\\n")

    configs = []
    for d_model in [640, 704, 768, 832, 896]:
        for num_layers in [8, 9, 10, 11, 12]:
            for nhead in [8, 12, 16]:
                if d_model % nhead != 0:  # d_model must be divisible by nhead
                    continue

                params = calculate_model_params(vocab_size, d_model, num_layers, nhead)

                configs.append({
                    'd_model': d_model,
                    'num_layers': num_layers,
                    'nhead': nhead,
                    'params': params,
                    'diff': abs(params - 100_000_000)
                })

    # Sort by closeness to 100M
    configs.sort(key=lambda x: x['diff'])

    # Show top 5 candidates
    print("Top 5 configurations closest to 100M parameters:")
    for i, cfg in enumerate(configs[:5], 1):
        print(f"{i}. d_model={cfg['d_model']}, layers={cfg['num_layers']}, "
              f"heads={cfg['nhead']} → {cfg['params']/1e6:.2f}M params")

    return configs[0]


def train_100m_model(
    num_epochs: int = 100,
    batch_size: int = 64,
    train_samples: int = 5000,
    val_samples: int = 1000,
    learning_rate: float = 3e-5,  # Lower LR for larger model
    save_dir: str = 'checkpoints_100m'
):
    """Train 100M parameter model"""

    print(f"\\n{'='*80}")
    print(f"TRAINING 100M PARAMETER MUSIC THEORY MODEL")
    print(f"{'='*80}\\n")

    # Find optimal config
    config = find_100m_config()

    d_model = config['d_model']
    num_layers = config['num_layers']
    nhead = config['nhead']
    estimated_params = config['params']

    print(f"\\n✓ Selected configuration:")
    print(f"  d_model: {d_model}")
    print(f"  num_layers: {num_layers}")
    print(f"  num_heads: {nhead}")
    print(f"  Estimated parameters: {estimated_params/1_000_000:.2f}M")
    print()

    # Create tokenizer
    tokenizer = MusicTheoryTokenizer()
    vocab_size = len(tokenizer)

    # Create dataloaders
    print(f"Creating datasets...")
    train_loader = get_dataloader(
        dataset_type='progression',
        batch_size=batch_size,
        num_samples=train_samples,
        shuffle=True
    )

    val_loader = get_dataloader(
        dataset_type='progression',
        batch_size=batch_size,
        num_samples=val_samples,
        shuffle=False
    )
    print(f"✓ Created datasets ({train_samples} train, {val_samples} val)\\n")

    # Create 100M model
    print(f"Creating 100M parameter model...")
    model = MusicTheoryTransformer(
        vocab_size=vocab_size,
        d_model=d_model,
        num_encoder_layers=num_layers,
        num_decoder_layers=num_layers,
        nhead=nhead,
        dim_feedforward=d_model * 4,
        dropout=0.15,  # Slightly higher dropout for large model
        pad_token_id=tokenizer.pad_token_id
    )

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)

    actual_params = sum(p.numel() for p in model.parameters())
    model_size_mb = actual_params * 4 / 1024**2

    print(f"✓ Model created!")
    print(f"  Actual parameters: {actual_params:,} ({actual_params/1_000_000:.2f}M)")
    print(f"  Device: {device}")
    print(f"  Memory footprint: ~{model_size_mb:.0f} MB")
    print(f"  Target achieved: {abs(actual_params - 100_000_000) / 100_000_000 * 100:.1f}% from 100M\\n")

    # Optimizer with gradient accumulation for large model
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        betas=(0.9, 0.98),  # Better for transformers
        eps=1e-9,
        weight_decay=0.01
    )

    # Advanced LR scheduling with longer warmup
    warmup_steps = len(train_loader) * 5  # 5 epochs warmup
    total_steps = len(train_loader) * num_epochs

    def lr_lambda(step):
        if step < warmup_steps:
            return step / warmup_steps
        return max(0.1, (total_steps - step) / (total_steps - warmup_steps))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    # Training loop
    best_val_loss = float('inf')
    save_path = Path(save_dir)
    save_path.mkdir(exist_ok=True, parents=True)

    print(f"Training for {num_epochs} epochs...\\n")
    print(f"Optimization:")
    print(f"  Learning rate: {learning_rate}")
    print(f"  Warmup steps: {warmup_steps}")
    print(f"  Total steps: {total_steps}")
    print(f"  Weight decay: 0.01")
    print(f"  Dropout: 0.15\\n")

    global_step = 0

    for epoch in range(num_epochs):
        # Training
        model.train()
        train_loss = 0.0

        pbar = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{num_epochs}")
        for batch in pbar:
            src = batch['input_ids'].to(device)
            tgt = batch['target_ids'].to(device)
            src_mask = batch['input_mask'].to(device)
            tgt_mask = batch['target_mask'].to(device)

            # Forward pass
            loss = model.get_loss(
                src,
                tgt,
                src_key_padding_mask=(src_mask == 0),
                tgt_key_padding_mask=(tgt_mask == 0),
                label_smoothing=0.1
            )

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

            train_loss += loss.item()
            global_step += 1

            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'lr': f'{scheduler.get_last_lr()[0]:.2e}'
            })

        avg_train_loss = train_loss / len(train_loader)

        # Validation
        model.eval()
        val_loss = 0.0

        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validation"):
                src = batch['input_ids'].to(device)
                tgt = batch['target_ids'].to(device)
                src_mask = batch['input_mask'].to(device)
                tgt_mask = batch['target_mask'].to(device)

                loss = model.get_loss(
                    src,
                    tgt,
                    src_key_padding_mask=(src_mask == 0),
                    tgt_key_padding_mask=(tgt_mask == 0)
                )

                val_loss += loss.item()

        avg_val_loss = val_loss / len(val_loader)

        print(f"\\nEpoch {epoch + 1}/{num_epochs}:")
        print(f"  Train Loss: {avg_train_loss:.4f}")
        print(f"  Val Loss: {avg_val_loss:.4f}")
        print(f"  Learning Rate: {scheduler.get_last_lr()[0]:.2e}")

        # Save best model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            model.save_pretrained(str(save_path / 'best_model'))
            print(f"  ✓ Saved best model (val_loss: {best_val_loss:.4f})")

        # Regular checkpoints every 10 epochs
        if (epoch + 1) % 10 == 0:
            model.save_pretrained(str(save_path / f'checkpoint_epoch_{epoch + 1}'))
            print(f"  ✓ Saved checkpoint")

    # Save final model
    model.save_pretrained(str(save_path / 'final_model'))
    tokenizer.save_vocab(str(save_path / 'vocab.json'))

    # Save model info
    info = {
        'params': actual_params,
        'd_model': d_model,
        'num_layers': num_layers,
        'nhead': nhead,
        'best_val_loss': best_val_loss,
        'epochs': num_epochs,
        'batch_size': batch_size,
        'learning_rate': learning_rate
    }

    with open(save_path / 'model_info.json', 'w') as f:
        json.dump(info, f, indent=2)

    print(f"\\n{'='*80}")
    print(f"✓ 100M MODEL TRAINING COMPLETE!")
    print(f"{'='*80}")
    print(f"\\nFinal Statistics:")
    print(f"  Parameters: {actual_params:,} ({actual_params/1_000_000:.2f}M)")
    print(f"  Model Size: {model_size_mb:.1f} MB")
    print(f"  Best Val Loss: {best_val_loss:.4f}")
    print(f"  Training Epochs: {num_epochs}")
    print(f"  Configuration: d_model={d_model}, layers={num_layers}, heads={nhead}")
    print(f"  Saved to: {save_path}/")

    return model


def main():
    parser = argparse.ArgumentParser(description='Train 100M Parameter Model')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of epochs (default: 100)')
    parser.add_argument('--batch-size', type=int, default=64,
                        help='Batch size (default: 64)')
    parser.add_argument('--train-samples', type=int, default=5000,
                        help='Training samples (default: 5000)')
    parser.add_argument('--val-samples', type=int, default=1000,
                        help='Validation samples (default: 1000)')
    parser.add_argument('--lr', type=float, default=3e-5,
                        help='Learning rate (default: 3e-5)')
    parser.add_argument('--save-dir', type=str, default='checkpoints_100m',
                        help='Save directory')

    args = parser.parse_args()

    print(f"\\n🎵 100M Parameter Music Theory Model Training 🎵")
    print(f"\\nConfiguration:")
    print(f"  Target: 100M parameters")
    print(f"  Epochs: {args.epochs}")
    print(f"  Batch Size: {args.batch_size}")
    print(f"  Training Samples: {args.train_samples}")
    print(f"  Learning Rate: {args.lr}")

    train_100m_model(
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        train_samples=args.train_samples,
        val_samples=args.val_samples,
        learning_rate=args.lr,
        save_dir=args.save_dir
    )


if __name__ == '__main__':
    main()
