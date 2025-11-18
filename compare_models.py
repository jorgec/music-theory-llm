"""
Model Comparison and Evaluation Script

Compares the original model (v1) with the improved model (v2) to demonstrate
the benefits of larger architecture, more data, and longer training.
"""

import torch
import time
from pathlib import Path
from src.models import MusicTheoryTransformer
from src.tokenizer import MusicTheoryTokenizer
from src.theory import Scale, Note, chord_from_scale_degree, ChordProgression


def load_model(checkpoint_path, d_model, num_layers, tokenizer):
    """Load a trained model from checkpoint"""
    vocab_size = len(tokenizer)
    model = MusicTheoryTransformer(
        vocab_size=vocab_size,
        d_model=d_model,
        num_encoder_layers=num_layers,
        num_decoder_layers=num_layers,
        pad_token_id=tokenizer.pad_token_id
    )

    checkpoint = torch.load(checkpoint_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    return model


def evaluate_model(model, test_progressions, tokenizer):
    """Evaluate model on test progressions"""
    total_loss = 0.0
    criterion = torch.nn.CrossEntropyLoss()

    with torch.no_grad():
        for progression in test_progressions:
            tokens = tokenizer.encode_progression(progression)
            input_ids = torch.tensor([tokens])

            # Use same input as target for loss computation
            output = model.forward(
                input_ids,
                input_ids,
                tgt_mask=model.generate_square_subsequent_mask(input_ids.size(1))
            )

            # Flatten for loss calculation
            output_flat = output.view(-1, output.size(-1))
            target_flat = input_ids.view(-1)

            loss = criterion(output_flat, target_flat)
            total_loss += loss.item()

    avg_loss = total_loss / len(test_progressions)
    return avg_loss


def benchmark_inference_speed(model, test_progression, tokenizer, num_runs=100):
    """Benchmark inference speed"""
    tokens = tokenizer.encode_progression(test_progression)
    input_ids = torch.tensor([tokens])

    # Warmup
    with torch.no_grad():
        for _ in range(10):
            _ = model.forward(
                input_ids,
                input_ids,
                tgt_mask=model.generate_square_subsequent_mask(input_ids.size(1))
            )

    # Benchmark
    start_time = time.time()
    with torch.no_grad():
        for _ in range(num_runs):
            _ = model.forward(
                input_ids,
                input_ids,
                tgt_mask=model.generate_square_subsequent_mask(input_ids.size(1))
            )
    end_time = time.time()

    avg_time = (end_time - start_time) / num_runs * 1000  # Convert to ms
    return avg_time


def create_test_progressions():
    """Create diverse test progressions"""
    progressions = []

    # 1. Classic I-IV-V-I in C major
    c_major = Scale.major(Note.from_string('C'))
    prog1 = ChordProgression(
        chords=[
            chord_from_scale_degree(c_major, 1),
            chord_from_scale_degree(c_major, 4),
            chord_from_scale_degree(c_major, 5),
            chord_from_scale_degree(c_major, 1),
        ],
        scale=c_major
    )
    progressions.append(prog1)

    # 2. ii-V-I in G major (jazz)
    g_major = Scale.major(Note.from_string('G'))
    prog2 = ChordProgression(
        chords=[
            chord_from_scale_degree(g_major, 2),
            chord_from_scale_degree(g_major, 5),
            chord_from_scale_degree(g_major, 1),
        ],
        scale=g_major
    )
    progressions.append(prog2)

    # 3. vi-IV-I-V in D major (pop progression)
    d_major = Scale.major(Note.from_string('D'))
    prog3 = ChordProgression(
        chords=[
            chord_from_scale_degree(d_major, 6),
            chord_from_scale_degree(d_major, 4),
            chord_from_scale_degree(d_major, 1),
            chord_from_scale_degree(d_major, 5),
        ],
        scale=d_major
    )
    progressions.append(prog3)

    # 4. I-vi-ii-V in F major
    f_major = Scale.major(Note.from_string('F'))
    prog4 = ChordProgression(
        chords=[
            chord_from_scale_degree(f_major, 1),
            chord_from_scale_degree(f_major, 6),
            chord_from_scale_degree(f_major, 2),
            chord_from_scale_degree(f_major, 5),
        ],
        scale=f_major
    )
    progressions.append(prog4)

    # 5. I-V-vi-IV in A major (very common)
    a_major = Scale.major(Note.from_string('A'))
    prog5 = ChordProgression(
        chords=[
            chord_from_scale_degree(a_major, 1),
            chord_from_scale_degree(a_major, 5),
            chord_from_scale_degree(a_major, 6),
            chord_from_scale_degree(a_major, 4),
        ],
        scale=a_major
    )
    progressions.append(prog5)

    return progressions


def main():
    print("=" * 80)
    print("MUSIC THEORY MODEL COMPARISON")
    print("=" * 80)
    print()

    # Load tokenizer
    tokenizer = MusicTheoryTokenizer()

    # Model v1 configuration
    print("Loading Model v1 (Original)...")
    try:
        tokenizer.load_vocab('checkpoints/vocab.json')
        model_v1 = load_model(
            'checkpoints/best_model/pytorch_model.bin',
            d_model=128,
            num_layers=2,
            tokenizer=tokenizer
        )
        v1_params = sum(p.numel() for p in model_v1.parameters())
        print(f"  ✓ Model v1 loaded: {v1_params:,} parameters")
    except Exception as e:
        print(f"  ✗ Could not load Model v1: {e}")
        model_v1 = None

    # Model v2 configuration
    print("\nLoading Model v2 (Improved)...")
    try:
        tokenizer.load_vocab('checkpoints_v2/vocab.json')
        model_v2 = load_model(
            'checkpoints_v2/best_model/pytorch_model.bin',
            d_model=256,
            num_layers=4,
            tokenizer=tokenizer
        )
        v2_params = sum(p.numel() for p in model_v2.parameters())
        print(f"  ✓ Model v2 loaded: {v2_params:,} parameters")
    except Exception as e:
        print(f"  ✗ Could not load Model v2: {e}")
        model_v2 = None

    if model_v1 is None and model_v2 is None:
        print("\n❌ No models available for comparison!")
        return

    # Create test data
    print("\n" + "-" * 80)
    print("Creating test progressions...")
    test_progressions = create_test_progressions()
    print(f"  ✓ Created {len(test_progressions)} test progressions")

    # Evaluation
    print("\n" + "=" * 80)
    print("EVALUATION RESULTS")
    print("=" * 80)

    # Model v1 evaluation
    if model_v1:
        print("\nModel v1 (Original):")
        print(f"  Architecture: d_model=128, layers=2")
        print(f"  Parameters: {v1_params:,}")
        print(f"  Training: 500 samples, 5 epochs")
        v1_loss = evaluate_model(model_v1, test_progressions, tokenizer)
        print(f"  Test Loss: {v1_loss:.4f}")
        v1_speed = benchmark_inference_speed(model_v1, test_progressions[0], tokenizer)
        print(f"  Inference Speed: {v1_speed:.2f} ms/sample")

    # Model v2 evaluation
    if model_v2:
        print("\nModel v2 (Improved):")
        print(f"  Architecture: d_model=256, layers=4")
        print(f"  Parameters: {v2_params:,}")
        print(f"  Training: 2000 samples, 20 epochs")
        v2_loss = evaluate_model(model_v2, test_progressions, tokenizer)
        print(f"  Test Loss: {v2_loss:.4f}")
        v2_speed = benchmark_inference_speed(model_v2, test_progressions[0], tokenizer)
        print(f"  Inference Speed: {v2_speed:.2f} ms/sample")

    # Comparison
    if model_v1 and model_v2:
        print("\n" + "=" * 80)
        print("COMPARISON")
        print("=" * 80)
        param_increase = (v2_params / v1_params - 1) * 100
        print(f"\nModel Size: {param_increase:+.1f}% ({v2_params/v1_params:.1f}x larger)")

        loss_improvement = (1 - v2_loss / v1_loss) * 100
        if loss_improvement > 0:
            print(f"Performance: {loss_improvement:.1f}% better (lower loss)")
        else:
            print(f"Performance: {abs(loss_improvement):.1f}% worse (higher loss)")

        speed_change = (v2_speed / v1_speed - 1) * 100
        print(f"Inference Speed: {speed_change:+.1f}% ({v2_speed/v1_speed:.2f}x)")

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print("\nThe improved model (v2) shows:")
        print(f"  • {param_increase:.0f}% more parameters for greater capacity")
        print(f"  • Trained on 4x more data (2000 vs 500 samples)")
        print(f"  • 4x longer training (20 vs 5 epochs)")
        if loss_improvement > 0:
            print(f"  • {loss_improvement:.1f}% improvement in test loss")
        print(f"\nTrade-off: {abs(speed_change):.0f}% {'slower' if speed_change > 0 else 'faster'} inference")
        print("  → Worthwhile for production applications needing high accuracy")

    print("\n" + "=" * 80)
    print("✓ Evaluation complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
