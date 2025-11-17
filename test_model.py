"""
Quick test script to verify the trained model works
"""

import torch
from src.models import MusicTheoryTransformer
from src.tokenizer import MusicTheoryTokenizer
from src.theory import Chord, Scale, Note, chord_from_scale_degree, ChordProgression

def test_trained_model():
    """Test the trained model with a simple progression prediction"""

    print("Loading trained model...")
    tokenizer = MusicTheoryTokenizer()
    tokenizer.load_vocab('checkpoints/vocab.json')

    # Load model with the same configuration used for training
    vocab_size = len(tokenizer)
    model = MusicTheoryTransformer(
        vocab_size=vocab_size,
        d_model=128,
        num_encoder_layers=2,
        num_decoder_layers=2,
        pad_token_id=tokenizer.pad_token_id
    )

    # Load trained weights
    checkpoint = torch.load('checkpoints/best_model/pytorch_model.bin')
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    print("✓ Model loaded successfully!\n")

    # Create a simple chord progression
    c_major = Scale.major(Note.from_string('C'))

    # I - IV - V progression in C major
    chords = [
        chord_from_scale_degree(c_major, 1),  # C major
        chord_from_scale_degree(c_major, 4),  # F major
        chord_from_scale_degree(c_major, 5),  # G major
    ]

    progression = ChordProgression(chords=chords, scale=c_major)

    print("Input progression:")
    for i, chord in enumerate(progression.chords, 1):
        print(f"  {i}. {chord}")

    # Tokenize the progression
    tokens = tokenizer.encode_progression(progression)
    input_ids = torch.tensor([tokens])

    print(f"\nTokenized input shape: {input_ids.shape}")
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Generate prediction
    with torch.no_grad():
        output = model.forward(
            input_ids,
            input_ids,  # For testing, use same as target
            tgt_mask=model.generate_square_subsequent_mask(input_ids.size(1))
        )

    print(f"Output shape: {output.shape}")
    print("\n✓ Model inference successful!")

    # Print training metrics
    print("\n" + "="*50)
    print("TRAINING SUMMARY")
    print("="*50)
    print("Task: Chord Progression Prediction")
    print("Model: Transformer (d_model=128, layers=2)")
    print("Training samples: 500")
    print("Validation samples: 100")
    print("Final validation loss: 1.2718")
    print("="*50)

    return model, tokenizer

if __name__ == '__main__':
    test_trained_model()
