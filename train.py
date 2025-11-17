"""
Training script for Music Theory ML Model
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import argparse
from pathlib import Path
from tqdm import tqdm
import json

from src.models import MusicTheoryTransformer, MusicTheoryEncoder
from src.tokenizer import MusicTheoryTokenizer
from data.datasets import get_dataloader


def train_seq2seq(
    model: MusicTheoryTransformer,
    train_loader: DataLoader,
    val_loader: DataLoader,
    num_epochs: int = 10,
    learning_rate: float = 1e-4,
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
    save_dir: str = 'checkpoints'
):
    """
    Train sequence-to-sequence model (e.g., for progression prediction).
    """
    print(f"Training on device: {device}")
    model = model.to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=2, verbose=True
    )

    best_val_loss = float('inf')
    save_path = Path(save_dir)
    save_path.mkdir(exist_ok=True, parents=True)

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

            # Create padding masks
            src_padding_mask = (src_mask == 0)
            tgt_padding_mask = (tgt_mask == 0)

            # Forward pass and compute loss
            loss = model.get_loss(
                src,
                tgt,
                src_key_padding_mask=src_padding_mask,
                tgt_key_padding_mask=tgt_padding_mask,
                label_smoothing=0.1
            )

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            train_loss += loss.item()
            pbar.set_postfix({'loss': loss.item()})

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

                src_padding_mask = (src_mask == 0)
                tgt_padding_mask = (tgt_mask == 0)

                loss = model.get_loss(
                    src,
                    tgt,
                    src_key_padding_mask=src_padding_mask,
                    tgt_key_padding_mask=tgt_padding_mask
                )

                val_loss += loss.item()

        avg_val_loss = val_loss / len(val_loader)

        print(f"\nEpoch {epoch + 1}:")
        print(f"  Train Loss: {avg_train_loss:.4f}")
        print(f"  Val Loss: {avg_val_loss:.4f}")

        # Learning rate scheduling
        scheduler.step(avg_val_loss)

        # Save best model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            model.save_pretrained(str(save_path / 'best_model'))
            print(f"  Saved best model (val_loss: {best_val_loss:.4f})")

        # Save checkpoint
        if (epoch + 1) % 5 == 0:
            model.save_pretrained(str(save_path / f'checkpoint_epoch_{epoch + 1}'))

    print(f"\nTraining complete! Best validation loss: {best_val_loss:.4f}")


def train_classification(
    model: MusicTheoryEncoder,
    train_loader: DataLoader,
    val_loader: DataLoader,
    num_epochs: int = 10,
    learning_rate: float = 1e-4,
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
    save_dir: str = 'checkpoints'
):
    """
    Train classification model (e.g., for chord quality classification).
    """
    print(f"Training on device: {device}")
    model = model.to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=2, verbose=True
    )

    best_val_acc = 0.0
    save_path = Path(save_dir)
    save_path.mkdir(exist_ok=True, parents=True)

    for epoch in range(num_epochs):
        # Training
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        pbar = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{num_epochs}")
        for batch in pbar:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            # Forward pass
            logits = model(input_ids, attention_mask)
            loss = criterion(logits, labels)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            # Track metrics
            train_loss += loss.item()
            predictions = torch.argmax(logits, dim=-1)
            train_correct += (predictions == labels).sum().item()
            train_total += labels.size(0)

            pbar.set_postfix({'loss': loss.item(), 'acc': train_correct / train_total})

        avg_train_loss = train_loss / len(train_loader)
        train_acc = train_correct / train_total

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validation"):
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)

                logits = model(input_ids, attention_mask)
                loss = criterion(logits, labels)

                val_loss += loss.item()
                predictions = torch.argmax(logits, dim=-1)
                val_correct += (predictions == labels).sum().item()
                val_total += labels.size(0)

        avg_val_loss = val_loss / len(val_loader)
        val_acc = val_correct / val_total

        print(f"\nEpoch {epoch + 1}:")
        print(f"  Train Loss: {avg_train_loss:.4f}, Train Acc: {train_acc:.4f}")
        print(f"  Val Loss: {avg_val_loss:.4f}, Val Acc: {val_acc:.4f}")

        # Learning rate scheduling
        scheduler.step(avg_val_loss)

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            model.save_pretrained(str(save_path / 'best_model'))
            print(f"  Saved best model (val_acc: {best_val_acc:.4f})")

    print(f"\nTraining complete! Best validation accuracy: {best_val_acc:.4f}")


def main():
    parser = argparse.ArgumentParser(description='Train Music Theory Model')
    parser.add_argument('--task', type=str, default='progression',
                        choices=['progression', 'scale', 'quality'],
                        help='Training task')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    parser.add_argument('--epochs', type=int, default=20, help='Number of epochs')
    parser.add_argument('--lr', type=float, default=1e-4, help='Learning rate')
    parser.add_argument('--train-samples', type=int, default=10000, help='Number of training samples')
    parser.add_argument('--val-samples', type=int, default=2000, help='Number of validation samples')
    parser.add_argument('--d-model', type=int, default=256, help='Model dimension')
    parser.add_argument('--num-layers', type=int, default=4, help='Number of layers')
    parser.add_argument('--save-dir', type=str, default='checkpoints', help='Save directory')

    args = parser.parse_args()

    # Create tokenizer
    tokenizer = MusicTheoryTokenizer()
    vocab_size = len(tokenizer)

    # Create dataloaders
    print(f"Creating datasets for task: {args.task}")
    train_loader = get_dataloader(
        dataset_type=args.task,
        batch_size=args.batch_size,
        num_samples=args.train_samples,
        shuffle=True
    )

    val_loader = get_dataloader(
        dataset_type=args.task,
        batch_size=args.batch_size,
        num_samples=args.val_samples,
        shuffle=False
    )

    # Create model
    if args.task == 'quality':
        # Classification task
        print(f"Creating encoder model (d_model={args.d_model}, layers={args.num_layers})")
        model = MusicTheoryEncoder(
            vocab_size=vocab_size,
            d_model=args.d_model,
            num_layers=args.num_layers,
            num_classes=7,  # 7 chord qualities
            pad_token_id=tokenizer.pad_token_id
        )

        train_classification(
            model,
            train_loader,
            val_loader,
            num_epochs=args.epochs,
            learning_rate=args.lr,
            save_dir=args.save_dir
        )
    else:
        # Sequence-to-sequence task
        print(f"Creating transformer model (d_model={args.d_model}, layers={args.num_layers})")
        model = MusicTheoryTransformer(
            vocab_size=vocab_size,
            d_model=args.d_model,
            num_encoder_layers=args.num_layers,
            num_decoder_layers=args.num_layers,
            pad_token_id=tokenizer.pad_token_id
        )

        train_seq2seq(
            model,
            train_loader,
            val_loader,
            num_epochs=args.epochs,
            learning_rate=args.lr,
            save_dir=args.save_dir
        )

    # Save tokenizer
    tokenizer.save_vocab(str(Path(args.save_dir) / 'vocab.json'))
    print(f"Saved tokenizer vocabulary to {args.save_dir}/vocab.json")


if __name__ == '__main__':
    main()
