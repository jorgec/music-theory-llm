"""
Style-Specific Music Data Generators

Generates training data for different musical styles:
- Jazz (ii-V-I, turnarounds, extended chords)
- Blues (12-bar blues, blues progressions)
- Progressive Metal (complex time signatures, modal progressions)
- Rock Fusion (jazz-rock hybrids, sophisticated harmony)
"""

import random
from typing import List, Tuple
from dataclasses import dataclass

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.theory import Note, Chord, ChordProgression, Scale, Pitch, ChordQuality
from src.theory.chords import chord_from_scale_degree


class JazzGenerator:
    """Generate jazz progressions and patterns"""

    @staticmethod
    def generate_ii_v_i(key_root: Note, num_variations: int = 10) -> List[ChordProgression]:
        """Generate ii-V-I progressions (the heart of jazz)"""
        progressions = []
        scale = Scale.major(key_root)

        for _ in range(num_variations):
            # Basic ii-V-I
            chords = [
                Chord(scale.notes[1], ChordQuality.MINOR_7),    # ii7
                Chord(scale.notes[4], ChordQuality.DOMINANT_7),  # V7
                Chord(scale.notes[0], ChordQuality.MAJOR_7),     # Imaj7
            ]

            progressions.append(ChordProgression(
                chords=chords,
                scale=scale,
                style='jazz'
            ))

        return progressions

    @staticmethod
    def generate_turnarounds(key_root: Note, num_variations: int = 10) -> List[ChordProgression]:
        """Generate jazz turnarounds"""
        progressions = []
        scale = Scale.major(key_root)

        turnaround_patterns = [
            # I-vi-ii-V
            [
                Chord(scale.notes[0], ChordQuality.MAJOR_7),
                Chord(scale.notes[5], ChordQuality.MINOR_7),
                Chord(scale.notes[1], ChordQuality.MINOR_7),
                Chord(scale.notes[4], ChordQuality.DOMINANT_7),
            ],
            # I-VI7-ii-V (with secondary dominant)
            [
                Chord(scale.notes[0], ChordQuality.MAJOR_7),
                Chord(scale.notes[5], ChordQuality.DOMINANT_7),
                Chord(scale.notes[1], ChordQuality.MINOR_7),
                Chord(scale.notes[4], ChordQuality.DOMINANT_7),
            ],
            # Imaj7-bIIImaj7-iim7-V7 (chromatic)
            [
                Chord(scale.notes[0], ChordQuality.MAJOR_7),
                Chord(scale.notes[2], ChordQuality.MAJOR_7),
                Chord(scale.notes[1], ChordQuality.MINOR_7),
                Chord(scale.notes[4], ChordQuality.DOMINANT_7),
            ],
        ]

        for pattern in turnaround_patterns:
            for _ in range(num_variations // len(turnaround_patterns)):
                progressions.append(ChordProgression(
                    chords=pattern,
                    scale=scale,
                    style='jazz'
                ))

        return progressions

    @staticmethod
    def generate_modal_jazz(num_variations: int = 10) -> List[ChordProgression]:
        """Generate modal jazz progressions (ala Miles Davis)"""
        progressions = []

        # D Dorian vamp
        d_note = Note.from_string('D')
        for _ in range(num_variations // 2):
            chords = [
                Chord(d_note, ChordQuality.MINOR_7),
                Chord(Note.from_string('E'), ChordQuality.MINOR_7),
            ]
            progressions.append(ChordProgression(
                chords=chords * 2,  # Repeat the vamp
                scale=Scale.major(Note.from_string('C')),  # D Dorian is C major starting on D
                style='jazz_modal'
            ))

        return progressions


class BluesGenerator:
    """Generate blues progressions"""

    @staticmethod
    def generate_12_bar_blues(key_root: Note, num_variations: int = 10) -> List[ChordProgression]:
        """Generate 12-bar blues progressions"""
        progressions = []
        scale = Scale.major(key_root)

        for variation in range(num_variations):
            # Classic 12-bar blues with variations
            if variation % 3 == 0:
                # Basic blues
                chords = [
                    Chord(scale.notes[0], ChordQuality.DOMINANT_7),  # I7
                    Chord(scale.notes[0], ChordQuality.DOMINANT_7),  # I7
                    Chord(scale.notes[0], ChordQuality.DOMINANT_7),  # I7
                    Chord(scale.notes[0], ChordQuality.DOMINANT_7),  # I7
                    Chord(scale.notes[3], ChordQuality.DOMINANT_7),  # IV7
                    Chord(scale.notes[3], ChordQuality.DOMINANT_7),  # IV7
                    Chord(scale.notes[0], ChordQuality.DOMINANT_7),  # I7
                    Chord(scale.notes[0], ChordQuality.DOMINANT_7),  # I7
                ]
            elif variation % 3 == 1:
                # Quick change blues
                chords = [
                    Chord(scale.notes[0], ChordQuality.DOMINANT_7),  # I7
                    Chord(scale.notes[3], ChordQuality.DOMINANT_7),  # IV7 (quick change)
                    Chord(scale.notes[0], ChordQuality.DOMINANT_7),  # I7
                    Chord(scale.notes[0], ChordQuality.DOMINANT_7),  # I7
                    Chord(scale.notes[3], ChordQuality.DOMINANT_7),  # IV7
                    Chord(scale.notes[3], ChordQuality.DOMINANT_7),  # IV7
                    Chord(scale.notes[0], ChordQuality.DOMINANT_7),  # I7
                    Chord(scale.notes[0], ChordQuality.DOMINANT_7),  # I7
                ]
            else:
                # Jazz blues
                chords = [
                    Chord(scale.notes[0], ChordQuality.MAJOR_7),     # Imaj7
                    Chord(scale.notes[3], ChordQuality.DOMINANT_7),  # IV7
                    Chord(scale.notes[0], ChordQuality.MAJOR_7),     # Imaj7
                    Chord(scale.notes[0], ChordQuality.DOMINANT_7),  # I7
                    Chord(scale.notes[3], ChordQuality.DOMINANT_7),  # IV7
                    Chord(scale.notes[3], ChordQuality.DOMINANT_7),  # IV7
                    Chord(scale.notes[0], ChordQuality.MAJOR_7),     # Imaj7
                    Chord(scale.notes[5], ChordQuality.MINOR_7),     # vi7
                ]

            progressions.append(ChordProgression(
                chords=chords,
                scale=scale,
                style='blues'
            ))

        return progressions

    @staticmethod
    def generate_minor_blues(key_root: Note, num_variations: int = 10) -> List[ChordProgression]:
        """Generate minor blues progressions"""
        progressions = []
        scale = Scale.minor(key_root)

        for _ in range(num_variations):
            chords = [
                Chord(scale.notes[0], ChordQuality.MINOR_7),
                Chord(scale.notes[0], ChordQuality.MINOR_7),
                Chord(scale.notes[3], ChordQuality.MINOR_7),
                Chord(scale.notes[3], ChordQuality.MINOR_7),
                Chord(scale.notes[0], ChordQuality.MINOR_7),
                Chord(scale.notes[0], ChordQuality.MINOR_7),
            ]

            progressions.append(ChordProgression(
                chords=chords,
                scale=scale,
                style='blues_minor'
            ))

        return progressions


class ProgressiveMetalGenerator:
    """Generate progressive metal progressions"""

    @staticmethod
    def generate_modal_metal(num_variations: int = 10) -> List[ChordProgression]:
        """Generate modal metal progressions (Phrygian, Locrian)"""
        progressions = []

        # E Phrygian (dark, Spanish sound)
        e_note = Note.from_string('E')
        c_major = Scale.major(Note.from_string('C'))  # E Phrygian is C major mode

        for _ in range(num_variations // 2):
            chords = [
                Chord(e_note, ChordQuality.MINOR),
                Chord(Note.from_string('F'), ChordQuality.MAJOR),
                Chord(Note.from_string('G'), ChordQuality.MAJOR),
                Chord(e_note, ChordQuality.MINOR),
            ]

            progressions.append(ChordProgression(
                chords=chords,
                scale=c_major,
                style='progressive_metal'
            ))

        # Lydian progressions (Dream Theater style)
        for _ in range(num_variations // 2):
            g_note = Note.from_string('G')
            d_major = Scale.major(Note.from_string('D'))  # G Lydian

            chords = [
                Chord(g_note, ChordQuality.MAJOR),
                Chord(Note.from_string('A'), ChordQuality.MAJOR),
                Chord(Note.from_string('B'), ChordQuality.MINOR),
                Chord(g_note, ChordQuality.MAJOR),
            ]

            progressions.append(ChordProgression(
                chords=chords,
                scale=d_major,
                style='progressive_metal'
            ))

        return progressions

    @staticmethod
    def generate_polymodal(num_variations: int = 10) -> List[ChordProgression]:
        """Generate polymodal/complex progressions"""
        progressions = []

        keys = [Note.from_string(n) for n in ['E', 'F#', 'A', 'C']]

        for _ in range(num_variations):
            root = random.choice(keys)
            scale = Scale.major(root)

            # Use power chords and suspended chords (common in metal)
            chords = [
                Chord(scale.notes[0], ChordQuality.POWER_CHORD),
                Chord(scale.notes[1], ChordQuality.POWER_CHORD),
                Chord(scale.notes[6], ChordQuality.DIMINISHED),
                Chord(scale.notes[0], ChordQuality.POWER_CHORD),
            ]

            progressions.append(ChordProgression(
                chords=chords,
                scale=scale,
                style='progressive_metal'
            ))

        return progressions


class RockFusionGenerator:
    """Generate rock fusion progressions (jazz-rock hybrid)"""

    @staticmethod
    def generate_jazz_rock(key_root: Note, num_variations: int = 10) -> List[ChordProgression]:
        """Generate jazz-rock fusion progressions"""
        progressions = []
        scale = Scale.major(key_root)

        patterns = [
            # Steely Dan style
            [
                Chord(scale.notes[0], ChordQuality.MAJOR_7),
                Chord(scale.notes[2], ChordQuality.MINOR_7),
                Chord(scale.notes[3], ChordQuality.MAJOR_7),
                Chord(scale.notes[1], ChordQuality.MINOR_7),
            ],
            # Weather Report style
            [
                Chord(scale.notes[0], ChordQuality.MAJOR_9),
                Chord(scale.notes[4], ChordQuality.DOMINANT_9),
                Chord(scale.notes[5], ChordQuality.MINOR_7),
                Chord(scale.notes[0], ChordQuality.MAJOR_9),
            ],
        ]

        for pattern in patterns:
            for _ in range(num_variations // len(patterns)):
                progressions.append(ChordProgression(
                    chords=pattern,
                    scale=scale,
                    style='rock_fusion'
                ))

        return progressions

    @staticmethod
    def generate_modal_fusion(num_variations: int = 10) -> List[ChordProgression]:
        """Generate modal fusion progressions"""
        progressions = []

        # Mixolydian (rock-friendly mode)
        for _ in range(num_variations):
            g_note = Note.from_string('G')
            c_major = Scale.major(Note.from_string('C'))  # G Mixolydian

            chords = [
                Chord(g_note, ChordQuality.DOMINANT_7),
                Chord(Note.from_string('F'), ChordQuality.MAJOR),
                Chord(Note.from_string('C'), ChordQuality.MAJOR),
                Chord(g_note, ChordQuality.DOMINANT_7),
            ]

            progressions.append(ChordProgression(
                chords=chords,
                scale=c_major,
                style='rock_fusion'
            ))

        return progressions


class NeoSoulGenerator:
    """Generate neo soul progressions (R&B with jazz influences)"""

    @staticmethod
    def generate_extended_chords(key_root: Note, num_variations: int = 10) -> List[ChordProgression]:
        """Generate neo soul progressions with extended chords"""
        progressions = []
        scale = Scale.major(key_root)

        patterns = [
            # Imaj9-Vim9-IIm9-V13 (D'Angelo style)
            [
                Chord(scale.notes[0], ChordQuality.MAJOR_9),
                Chord(scale.notes[5], ChordQuality.MINOR_9),
                Chord(scale.notes[1], ChordQuality.MINOR_9),
                Chord(scale.notes[4], ChordQuality.DOMINANT_9),
            ],
            # IIIm7-VIm9-IIm9-Vmaj7
            [
                Chord(scale.notes[2], ChordQuality.MINOR_7),
                Chord(scale.notes[5], ChordQuality.MINOR_9),
                Chord(scale.notes[1], ChordQuality.MINOR_9),
                Chord(scale.notes[4], ChordQuality.MAJOR_7),
            ],
            # Imaj7-IV9-IIm7-V9 (Erykah Badu style)
            [
                Chord(scale.notes[0], ChordQuality.MAJOR_7),
                Chord(scale.notes[3], ChordQuality.DOMINANT_9),
                Chord(scale.notes[1], ChordQuality.MINOR_7),
                Chord(scale.notes[4], ChordQuality.DOMINANT_9),
            ],
        ]

        for pattern in patterns:
            for _ in range(num_variations // len(patterns)):
                progressions.append(ChordProgression(
                    chords=pattern,
                    scale=scale,
                    style='neo_soul'
                ))

        return progressions


class MathRockGenerator:
    """Generate math rock progressions (complex, angular)"""

    @staticmethod
    def generate_angular_progressions(num_variations: int = 10) -> List[ChordProgression]:
        """Generate math rock progressions with unusual intervals"""
        progressions = []

        keys = [Note.from_string(n) for n in ['E', 'F#', 'A', 'B']]

        for _ in range(num_variations):
            root = random.choice(keys)
            scale = Scale.major(root)

            # Use unexpected chord movements
            chords = [
                Chord(scale.notes[0], ChordQuality.MAJOR),
                Chord(scale.notes[2], ChordQuality.SUSPENDED_4),  # Unusual
                Chord(scale.notes[5], ChordQuality.MAJOR),
                Chord(scale.notes[1], ChordQuality.MINOR),
                Chord(scale.notes[6], ChordQuality.DIMINISHED),  # Tension
                Chord(scale.notes[0], ChordQuality.MAJOR),
            ]

            progressions.append(ChordProgression(
                chords=chords,
                scale=scale,
                style='math_rock'
            ))

        return progressions


class PostRockGenerator:
    """Generate post rock progressions (atmospheric, building)"""

    @staticmethod
    def generate_atmospheric(num_variations: int = 10) -> List[ChordProgression]:
        """Generate atmospheric post rock progressions"""
        progressions = []

        keys = [Note.from_string(n) for n in ['D', 'E', 'A', 'G']]

        for _ in range(num_variations):
            root = random.choice(keys)
            scale = Scale.major(root)

            # Slow, building progressions with pedal tones
            chords = [
                Chord(scale.notes[0], ChordQuality.MAJOR),
                Chord(scale.notes[0], ChordQuality.SUSPENDED_2),  # Add texture
                Chord(scale.notes[4], ChordQuality.MAJOR),
                Chord(scale.notes[5], ChordQuality.MINOR),
                Chord(scale.notes[3], ChordQuality.MAJOR),
                Chord(scale.notes[0], ChordQuality.MAJOR),  # Return home
            ]

            progressions.append(ChordProgression(
                chords=chords,
                scale=scale,
                style='post_rock'
            ))

        return progressions


class ShoegazeGenerator:
    """Generate shoegaze progressions (dreamy, dissonant)"""

    @staticmethod
    def generate_dreamy(num_variations: int = 10) -> List[ChordProgression]:
        """Generate dreamy shoegaze progressions"""
        progressions = []

        keys = [Note.from_string(n) for n in ['E', 'A', 'D', 'C']]

        for _ in range(num_variations):
            root = random.choice(keys)
            scale = Scale.major(root)

            # Heavy use of suspended and added chords
            chords = [
                Chord(scale.notes[0], ChordQuality.SUSPENDED_4),
                Chord(scale.notes[5], ChordQuality.MINOR),
                Chord(scale.notes[3], ChordQuality.MAJOR_7),
                Chord(scale.notes[1], ChordQuality.SUSPENDED_2),
                Chord(scale.notes[4], ChordQuality.MAJOR),
            ]

            progressions.append(ChordProgression(
                chords=chords,
                scale=scale,
                style='shoegaze'
            ))

        return progressions


class MetalcoreGenerator:
    """Generate metalcore progressions (breakdowns, power chords)"""

    @staticmethod
    def generate_breakdowns(num_variations: int = 10) -> List[ChordProgression]:
        """Generate metalcore breakdown progressions"""
        progressions = []

        # Metalcore often uses drop tunings
        keys = [Note.from_string(n) for n in ['C', 'D', 'E', 'F']]

        for _ in range(num_variations):
            root = random.choice(keys)
            scale = Scale.minor(root)  # Often minor

            # Power chords and chromatic movement
            chords = [
                Chord(scale.notes[0], ChordQuality.POWER_CHORD),
                Chord(scale.notes[1], ChordQuality.POWER_CHORD),
                Chord(scale.notes[3], ChordQuality.POWER_CHORD),
                Chord(scale.notes[0], ChordQuality.POWER_CHORD),
                Chord(scale.notes[6], ChordQuality.DIMINISHED),  # Tension
            ]

            progressions.append(ChordProgression(
                chords=chords,
                scale=scale,
                style='metalcore'
            ))

        return progressions


class RnBGenerator:
    """Generate R&B progressions (smooth, extended chords)"""

    @staticmethod
    def generate_smooth_progressions(key_root: Note, num_variations: int = 10) -> List[ChordProgression]:
        """Generate smooth R&B progressions"""
        progressions = []
        scale = Scale.major(key_root)

        patterns = [
            # Classic R&B: Imaj7-IVmaj7-IIm7-V7
            [
                Chord(scale.notes[0], ChordQuality.MAJOR_7),
                Chord(scale.notes[3], ChordQuality.MAJOR_7),
                Chord(scale.notes[1], ChordQuality.MINOR_7),
                Chord(scale.notes[4], ChordQuality.DOMINANT_7),
            ],
            # Gospel-influenced: Imaj7-IIIm7-VIm7-IIm7-V7
            [
                Chord(scale.notes[0], ChordQuality.MAJOR_7),
                Chord(scale.notes[2], ChordQuality.MINOR_7),
                Chord(scale.notes[5], ChordQuality.MINOR_7),
                Chord(scale.notes[1], ChordQuality.MINOR_7),
                Chord(scale.notes[4], ChordQuality.DOMINANT_7),
            ],
        ]

        for pattern in patterns:
            for _ in range(num_variations // len(patterns)):
                progressions.append(ChordProgression(
                    chords=pattern,
                    scale=scale,
                    style='rnb'
                ))

        return progressions


def generate_style_dataset(style: str, num_samples: int = 100) -> List[ChordProgression]:
    """Generate dataset for a specific style"""

    progressions = []
    keys = [Note.from_string(n) for n in ['C', 'D', 'E', 'F', 'G', 'A', 'B']]

    if style == 'jazz':
        for key in keys:
            progressions.extend(JazzGenerator.generate_ii_v_i(key, num_samples // (len(keys) * 3)))
            progressions.extend(JazzGenerator.generate_turnarounds(key, num_samples // (len(keys) * 3)))
        progressions.extend(JazzGenerator.generate_modal_jazz(num_samples // 3))

    elif style == 'blues':
        for key in keys:
            progressions.extend(BluesGenerator.generate_12_bar_blues(key, num_samples // (len(keys) * 2)))
            progressions.extend(BluesGenerator.generate_minor_blues(key, num_samples // (len(keys) * 2)))

    elif style == 'progressive_metal':
        progressions.extend(ProgressiveMetalGenerator.generate_modal_metal(num_samples // 2))
        progressions.extend(ProgressiveMetalGenerator.generate_polymodal(num_samples // 2))

    elif style == 'rock_fusion':
        for key in keys:
            progressions.extend(RockFusionGenerator.generate_jazz_rock(key, num_samples // (len(keys) * 2)))
        progressions.extend(RockFusionGenerator.generate_modal_fusion(num_samples // 2))

    elif style == 'neo_soul':
        for key in keys:
            progressions.extend(NeoSoulGenerator.generate_extended_chords(key, num_samples // len(keys)))

    elif style == 'math_rock':
        progressions.extend(MathRockGenerator.generate_angular_progressions(num_samples))

    elif style == 'post_rock':
        progressions.extend(PostRockGenerator.generate_atmospheric(num_samples))

    elif style == 'shoegaze':
        progressions.extend(ShoegazeGenerator.generate_dreamy(num_samples))

    elif style == 'metalcore':
        progressions.extend(MetalcoreGenerator.generate_breakdowns(num_samples))

    elif style == 'rnb':
        for key in keys:
            progressions.extend(RnBGenerator.generate_smooth_progressions(key, num_samples // len(keys)))

    else:
        raise ValueError(f"Unknown style: {style}")

    return progressions


def main():
    """Generate datasets for all styles"""
    import pickle

    # Priority styles first (as requested by user)
    styles = [
        'neo_soul',
        'blues',
        'progressive_metal',
        'rock_fusion',
        'jazz',
        'math_rock',
        'post_rock',
        'shoegaze',
        'metalcore',
        'rnb'
    ]

    print(f"{'='*60}")
    print("GENERATING STYLE-SPECIFIC DATASETS")
    print(f"{'='*60}")
    print("\nPriority styles: neo_soul, blues, progressive_metal, rock_fusion")
    print(f"Total styles: {len(styles)}\n")

    for style in styles:
        print(f"Generating {style} dataset...")
        progressions = generate_style_dataset(style, num_samples=200)
        print(f"  ✓ Generated {len(progressions)} progressions")

        # Save
        output_path = Path(f'data/styles/{style}_progressions.pkl')
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            pickle.dump(progressions, f)
        print(f"  ✓ Saved to {output_path}\n")

    print(f"{'='*60}")
    print("✓ ALL STYLE DATASETS GENERATED!")
    print(f"{'='*60}")
    print("\nYou can now train style-specific models:")
    for style in styles:
        print(f"  python train_style.py --style {style} --epochs 20")


if __name__ == '__main__':
    main()
