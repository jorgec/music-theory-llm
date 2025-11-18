"""
Priority Style Training Script

Trains focused models for the four priority musical styles:
- Neo Soul
- Blues
- Progressive Metal
- Rock Fusion

Uses optimized configurations and extended training for best results.
"""

import torch
import argparse
from pathlib import Path

from train_comprehensive import train_style_model
from src.tokenizer import MusicTheoryTokenizer


PRIORITY_STYLES = ['neo_soul', 'blues', 'progressive_metal', 'rock_fusion']

# Optimized configurations for each priority style
STYLE_CONFIGS = {
    'neo_soul': {
        'd_model': 384,  # Large model for complex extended chords
        'num_layers': 6,
        'epochs': 60,  # More epochs for complex harmony
        'batch_size': 32,
        'learning_rate': 8e-5,
        'description': 'Extended chords, chromatic movement, gospel influences'
    },
    'blues': {
        'd_model': 256,
        'num_layers': 4,
        'epochs': 50,
        'batch_size': 32,
        'learning_rate': 1e-4,
        'description': '12-bar blues, pentatonic patterns, dominant 7ths'
    },
    'progressive_metal': {
        'd_model': 384,
        'num_layers': 6,
        'epochs': 60,
        'batch_size': 32,
        'learning_rate': 8e-5,
        'description': 'Modal progressions, polymodal harmony, technical riffs'
    },
    'rock_fusion': {
        'd_model': 384,
        'num_layers': 6,
        'epochs': 60,
        'batch_size': 32,
        'learning_rate': 8e-5,
        'description': 'Jazz-rock hybrids, complex harmony, modal fusion'
    }
}


def calculate_model_size(vocab_size: int, d_model: int, num_layers: int) -> int:
    """Estimate model parameter count"""
    # Simplified calculation
    embedding_params = vocab_size * d_model * 2
    attention_params = 4 * d_model * d_model
    ffn_params = 2 * d_model * (d_model * 4)
    layer_params = attention_params + ffn_params + (d_model * 4)
    transformer_params = layer_params * num_layers * 2
    output_params = d_model * vocab_size

    total = embedding_params + transformer_params + output_params
    return total


def print_training_plan():
    """Display the complete training plan"""
    tokenizer = MusicTheoryTokenizer()
    vocab_size = len(tokenizer)

    print(f"\n{'='*80}")
    print("PRIORITY STYLES TRAINING PLAN")
    print(f"{'='*80}\n")

    print("Priority Styles: Neo Soul, Blues, Progressive Metal, Rock Fusion\n")
    print("These styles receive optimized configurations for best performance:\n")

    for style in PRIORITY_STYLES:
        config = STYLE_CONFIGS[style]
        params = calculate_model_size(vocab_size, config['d_model'], config['num_layers'])

        print(f"📊 {style.upper().replace('_', ' ')}")
        print(f"   {config['description']}")
        print(f"   Model: {params/1_000_000:.1f}M parameters (d_model={config['d_model']}, layers={config['num_layers']})")
        print(f"   Training: {config['epochs']} epochs, batch_size={config['batch_size']}, lr={config['learning_rate']}")
        print()

    total_params = sum(
        calculate_model_size(vocab_size, STYLE_CONFIGS[s]['d_model'], STYLE_CONFIGS[s]['num_layers'])
        for s in PRIORITY_STYLES
    )

    print(f"Total parameters across all priority models: {total_params/1_000_000:.1f}M")
    print(f"{'='*80}\n")


def train_priority_styles(
    styles: list = None,
    save_dir: str = 'checkpoints_priority',
    dry_run: bool = False
):
    """
    Train models for priority styles

    Args:
        styles: List of styles to train (None = all priority styles)
        save_dir: Base directory for saving checkpoints
        dry_run: If True, only show the plan without training
    """

    if styles is None:
        styles = PRIORITY_STYLES

    # Validate styles
    for style in styles:
        if style not in PRIORITY_STYLES:
            print(f"⚠ Warning: '{style}' is not a priority style")
            print(f"   Priority styles are: {', '.join(PRIORITY_STYLES)}")
            return

    print_training_plan()

    if dry_run:
        print("DRY RUN - No training will be performed")
        return

    print(f"Starting training for {len(styles)} priority style(s)...\n")

    trained_models = {}

    for i, style in enumerate(styles, 1):
        config = STYLE_CONFIGS[style]

        print(f"\n{'='*80}")
        print(f"TRAINING {i}/{len(styles)}: {style.upper().replace('_', ' ')}")
        print(f"{'='*80}\n")

        try:
            model = train_style_model(
                style=style,
                num_epochs=config['epochs'],
                batch_size=config['batch_size'],
                d_model=config['d_model'],
                num_layers=config['num_layers'],
                learning_rate=config['learning_rate'],
                save_dir=save_dir
            )

            trained_models[style] = {
                'model': model,
                'config': config,
                'checkpoint_path': str(Path(save_dir) / style / 'best_model')
            }

            print(f"\n✓ {style} model training complete!")

        except Exception as e:
            print(f"\n❌ Error training {style}: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print(f"\n{'='*80}")
    print("PRIORITY STYLES TRAINING SUMMARY")
    print(f"{'='*80}\n")

    print(f"Successfully trained {len(trained_models)}/{len(styles)} models:\n")

    for style, info in trained_models.items():
        config = info['config']
        print(f"✓ {style.upper().replace('_', ' ')}")
        print(f"  Checkpoint: {info['checkpoint_path']}")
        print(f"  Configuration: {config['d_model']}-dim, {config['num_layers']} layers, {config['epochs']} epochs")
        print()

    print("These models are optimized for the Music Recommendation System")
    print("and can be used for intelligent composition assistance.")
    print(f"\n{'='*80}\n")

    return trained_models


def main():
    parser = argparse.ArgumentParser(
        description='Train models for priority musical styles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Priority Styles:
  neo_soul            - Extended chords, chromatic movement, gospel influences
  blues               - 12-bar blues, pentatonic patterns, dominant 7ths
  progressive_metal   - Modal progressions, polymodal harmony, technical riffs
  rock_fusion         - Jazz-rock hybrids, complex harmony, modal fusion

Examples:
  # Train all priority styles
  python train_priority_styles.py

  # Train only neo soul and blues
  python train_priority_styles.py --styles neo_soul blues

  # Show training plan without training
  python train_priority_styles.py --dry-run

  # Use custom save directory
  python train_priority_styles.py --save-dir my_models
        """
    )

    parser.add_argument(
        '--styles',
        type=str,
        nargs='+',
        choices=PRIORITY_STYLES,
        default=None,
        help='Specific styles to train (default: all priority styles)'
    )

    parser.add_argument(
        '--save-dir',
        type=str,
        default='checkpoints_priority',
        help='Base directory for saving checkpoints (default: checkpoints_priority)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show training plan without actually training'
    )

    args = parser.parse_args()

    # Train
    train_priority_styles(
        styles=args.styles,
        save_dir=args.save_dir,
        dry_run=args.dry_run
    )


if __name__ == '__main__':
    main()
