"""
Train Extra-Large Music Theory Model (20M+ Parameters)

Configuration for maximum capacity:
- d_model: 384 (1.5x larger)
- Layers: 6 (1.5x deeper)
- Parameters: ~20M
- Extended training: 50 epochs
- Large batch size: 64
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import argparse
from pathlib import Path
from tqdm import tqdm
import pickle

from src.models import MusicTheoryTransformer
from src.tokenizer import MusicTheoryTokenizer
from data.datasets import get_dataloader


def calculate_model_params(vocab_size, d_model, num_layers):
    """Estimate model parameters"""
    # Rough calculation
    embedding_params = vocab_size * d_model * 2  # src + tgt embeddings

    # Per transformer layer
    attention_params = 4 * d_model * d_model  # Q, K, V, O projections
    ffn_params = 2 * d_model * (d_model * 4)  # Two linear layers in FFN
    layer_params = attention_params + ffn_params + (d_model * 4)  # + layer norms

    transformer_params = layer_params * num_layers * 2  # encoder + decoder
    output_params = d_model * vocab_size

    total = embedding_params + transformer_params + output_params
    return total


def find_optimal_config(target_params=20_000_000, vocab_size=101):
    """Find model config closest to target parameters"""

    configs = []
    for d_model in [256, 384, 512, 640]:
        for num_layers in [4, 5, 6, 7, 8]:
            params = calculate_model_params(vocab_size, d_model, num_layers)
            configs.append({
                'd_model': d_model,
                'num_layers': num_layers,
                'params': params,
                'diff': abs(params - target_params)
            })

    # Sort by closeness to target
    configs.sort(key=lambda x: x['diff'])
    return configs[0]


def train_xl_model(
    num_epochs: int = 50,
    batch_size: int = 64,
    train_samples: int = 3000,
    val_samples: int = 600,
    learning_rate: float = 1e-4,
    save_dir: str = 'checkpoints_xl',
    target_params: int = 20_000_000
):
    """Train extra-large model"""

    print(f"\n{'='*80}")
    print(f"TRAINING EXTRA-LARGE MUSIC THEORY MODEL")
    print(f"Target: {target_params/1_000_000:.1f}M Parameters")
    print(f"{'='*80}\n")

    # Find optimal config
    print("Finding optimal model configuration...")
    config = find_optimal_config(target_params)

    d_model = config['d_model']
    num_layers = config['num_layers']
    estimated_params = config['params']

    print(f"✓ Optimal config found:")
    print(f"  d_model: {d_model}")
    print(f"  num_layers: {num_layers}")
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
    print(f"✓ Created datasets ({train_samples} train, {val_samples} val)\n")

    # Create XL model
    print(f"Creating XL model...")
    model = MusicTheoryTransformer(
        vocab_size=vocab_size,
        d_model=d_model,
        num_encoder_layers=num_layers,
        num_decoder_layers=num_layers,
        nhead=8,
        dim_feedforward=d_model * 4,  # Standard 4x expansion
        pad_token_id=tokenizer.pad_token_id
    )

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)

    actual_params = sum(p.numel() for p in model.parameters())
    print(f"✓ Model created!")
    print(f"  Actual parameters: {actual_params:,} ({actual_params/1_000_000:.2f}M)")
    print(f"  Device: {device}")
    print(f"  Memory footprint: ~{actual_params * 4 / 1024**2:.0f} MB\n")

    # Optimizer and scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=10, T_mult=2
    )

    # Training loop
    best_val_loss = float('inf')
    save_path = Path(save_dir)
    save_path.mkdir(exist_ok=True, parents=True)

    print(f"Training for {num_epochs} epochs with batch size {batch_size}...\n")

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
            scheduler.step(epoch + batch['input_ids'].size(0) / len(train_loader))

            train_loss += loss.item()
            pbar.set_postfix({'loss': f'{loss.item():.4f}', 'lr': f'{scheduler.get_last_lr()[0]:.2e}'})

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

        print(f"\nEpoch {epoch + 1}/{num_epochs}:")
        print(f"  Train Loss: {avg_train_loss:.4f}")
        print(f"  Val Loss: {avg_val_loss:.4f}")
        print(f"  Learning Rate: {scheduler.get_last_lr()[0]:.2e}")

        # Save best model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            model.save_pretrained(str(save_path / 'best_model'))
            print(f"  ✓ Saved best model (val_loss: {best_val_loss:.4f})")

        # Regular checkpoints
        if (epoch + 1) % 10 == 0:
            model.save_pretrained(str(save_path / f'checkpoint_epoch_{epoch + 1}'))
            print(f"  ✓ Saved checkpoint")

    # Save final model and tokenizer
    model.save_pretrained(str(save_path / 'final_model'))
    tokenizer.save_vocab(str(save_path / 'vocab.json'))

    # Save training info
    info = {
        'params': actual_params,
        'd_model': d_model,
        'num_layers': num_layers,
        'best_val_loss': best_val_loss,
        'epochs': num_epochs,
        'batch_size': batch_size
    }

    import json
    with open(save_path / 'model_info.json', 'w') as f:
        json.dump(info, f, indent=2)

    print(f"\n{'='*80}")
    print(f"✓ XL MODEL TRAINING COMPLETE!")
    print(f"{'='*80}")
    print(f"\nModel Statistics:")
    print(f"  Parameters: {actual_params:,} ({actual_params/1_000_000:.2f}M)")
    print(f"  Best Val Loss: {best_val_loss:.4f}")
    print(f"  Training Epochs: {num_epochs}")
    print(f"  Saved to: {save_path}/")

    return model


def main():
    parser = argparse.ArgumentParser(description='Train XL Music Theory Model')
    parser.add_argument('--epochs', type=int, default=50,
                        help='Number of epochs (default: 50)')
    parser.add_argument('--batch-size', type=int, default=64,
                        help='Batch size (default: 64)')
    parser.add_argument('--train-samples', type=int, default=3000,
                        help='Number of training samples (default: 3000)')
    parser.add_argument('--val-samples', type=int, default=600,
                        help='Number of validation samples (default: 600)')
    parser.add_argument('--lr', type=float, default=1e-4,
                        help='Learning rate (default: 1e-4)')
    parser.add_argument('--target-params', type=int, default=20_000_000,
                        help='Target parameter count (default: 20M)')
    parser.add_argument('--save-dir', type=str, default='checkpoints_xl',
                        help='Save directory')

    args = parser.parse_args()

    print(f"\n🎵 Music Theory XL Model Training 🎵")
    print(f"\nConfiguration:")
    print(f"  Target Parameters: {args.target_params/1_000_000:.0f}M")
    print(f"  Epochs: {args.epochs}")
    print(f"  Batch Size: {args.batch_size}")
    print(f"  Training Samples: {args.train_samples}")
    print(f"  Learning Rate: {args.lr}")

    train_xl_model(
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        train_samples=args.train_samples,
        val_samples=args.val_samples,
        learning_rate=args.lr,
        save_dir=args.save_dir,
        target_params=args.target_params
    )


if __name__ == '__main__':
    main()
