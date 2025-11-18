"""
Extract Real Music Data from music21 Corpus

This script extracts chord progressions, melodies, and harmonizations
from actual music in the music21 corpus.
"""

import sys
from pathlib import Path
import pickle
import json
from typing import List, Dict, Tuple
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.theory import Note, Chord, ChordProgression, Scale, Pitch
from src.theory.notes import Interval

# Import music21
try:
    from music21 import corpus, converter, chord as m21chord, stream, note, key
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    print("⚠ music21 not available. Install with: pip install music21")


class RealMusicDataExtractor:
    """Extract training data from real music scores"""

    def __init__(self):
        self.progressions = []
        self.melodies = []
        self.harmonizations = []
        self.style_data = defaultdict(list)

    def extract_from_music21(self, limit: int = 100, styles: List[str] = None):
        """Extract data from music21 corpus"""

        if not MUSIC21_AVAILABLE:
            print("❌ music21 not available")
            return

        print(f"\n{'='*60}")
        print("EXTRACTING REAL MUSIC DATA FROM MUSIC21")
        print(f"{'='*60}\n")

        # Get list of works from corpus
        print("1. Discovering available works...")

        # Target different styles
        style_searches = {
            'bach': corpus.search('bach', 'composer'),
            'mozart': corpus.search('mozart', 'composer'),
            'beethoven': corpus.search('beethoven', 'composer'),
            'jazz': corpus.search('jazz'),
            'folk': corpus.search('folk'),
        }

        works_to_process = []
        for style_name, search_results in style_searches.items():
            if search_results:
                count = min(limit // len(style_searches), len(search_results))
                works_to_process.extend([
                    (style_name, search_results[i])
                    for i in range(count)
                ])

        print(f"   Found {len(works_to_process)} works to process\n")

        # Process each work
        print("2. Processing works...")
        processed = 0

        for style, work in works_to_process:
            try:
                print(f"   Processing: {work.metadata.title or 'Untitled'} ({style})")
                score = work.parse()

                # Extract data from this score
                self._extract_from_score(score, style)
                processed += 1

            except Exception as e:
                print(f"   ⚠ Error processing {work}: {e}")
                continue

        print(f"\n✓ Successfully processed {processed} works\n")

        # Print statistics
        print(f"{'='*60}")
        print("EXTRACTION STATISTICS")
        print(f"{'='*60}")
        print(f"Chord progressions: {len(self.progressions)}")
        print(f"Melodies: {len(self.melodies)}")
        print(f"Harmonizations: {len(self.harmonizations)}")
        print(f"\nBy style:")
        for style, data in self.style_data.items():
            print(f"  {style}: {len(data)} items")

    def _extract_from_score(self, score, style: str):
        """Extract musical data from a score"""

        # Try to determine key
        try:
            analyzed_key = score.analyze('key')
            scale_root = Note.from_string(analyzed_key.tonic.name)
            if analyzed_key.mode == 'major':
                music_scale = Scale.major(scale_root)
            else:
                music_scale = Scale.minor(scale_root)
        except:
            # Default to C major if key analysis fails
            music_scale = Scale.major(Note.from_string('C'))

        # Extract chords
        chords_found = []
        for element in score.flatten().getElementsByClass(m21chord.Chord):
            try:
                # Convert music21 chord to our Chord object
                root_name = element.root().name
                root_note = Note.from_string(root_name)

                # Simple chord quality detection
                if element.isMajorTriad():
                    from src.theory.chords import ChordQuality
                    quality = ChordQuality.MAJOR
                elif element.isMinorTriad():
                    quality = ChordQuality.MINOR
                elif element.isDominantSeventh():
                    quality = ChordQuality.DOMINANT_7
                elif element.isMajorSeventh():
                    quality = ChordQuality.MAJOR_7
                elif element.isMinorSeventh():
                    quality = ChordQuality.MINOR_7
                else:
                    quality = ChordQuality.MAJOR  # Default

                our_chord = Chord(root=root_note, quality=quality)
                chords_found.append(our_chord)

            except Exception as e:
                continue

        # Create progression if we found chords
        if len(chords_found) >= 2:
            progression = ChordProgression(
                chords=chords_found[:8],  # Limit to 8 chords
                scale=music_scale,
                style=style
            )
            self.progressions.append(progression)
            self.style_data[style].append({
                'type': 'progression',
                'data': progression
            })

        # Extract melody
        melody_notes = []
        for part in score.parts:
            for element in part.flatten().notes:
                if isinstance(element, note.Note):
                    try:
                        pitch = Pitch(
                            pitch_class=element.pitch.pitchClass,
                            octave=element.pitch.octave
                        )
                        melody_notes.append({
                            'pitch': pitch,
                            'duration': float(element.quarterLength)
                        })
                    except:
                        continue

            # Only take first part for melody
            if melody_notes:
                break

        if melody_notes:
            self.melodies.append({
                'notes': melody_notes[:32],  # Limit length
                'scale': music_scale,
                'style': style
            })
            self.style_data[style].append({
                'type': 'melody',
                'data': melody_notes[:32]
            })

        # Create harmonization pairs (melody + chords)
        if melody_notes and chords_found:
            self.harmonizations.append({
                'melody': melody_notes[:32],
                'chords': chords_found[:8],
                'scale': music_scale,
                'style': style
            })

    def save_data(self, output_dir: str = 'data/real_music'):
        """Save extracted data"""

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*60}")
        print("SAVING EXTRACTED DATA")
        print(f"{'='*60}\n")

        # Save progressions
        if self.progressions:
            prog_file = output_path / 'progressions.pkl'
            with open(prog_file, 'wb') as f:
                pickle.dump(self.progressions, f)
            print(f"✓ Saved {len(self.progressions)} progressions to {prog_file}")

        # Save melodies
        if self.melodies:
            melody_file = output_path / 'melodies.pkl'
            with open(melody_file, 'wb') as f:
                pickle.dump(self.melodies, f)
            print(f"✓ Saved {len(self.melodies)} melodies to {melody_file}")

        # Save harmonizations
        if self.harmonizations:
            harm_file = output_path / 'harmonizations.pkl'
            with open(harm_file, 'wb') as f:
                pickle.dump(self.harmonizations, f)
            print(f"✓ Saved {len(self.harmonizations)} harmonizations to {harm_file}")

        # Save style-specific data
        if self.style_data:
            style_file = output_path / 'style_data.pkl'
            with open(style_file, 'wb') as f:
                pickle.dump(dict(self.style_data), f)
            print(f"✓ Saved style-specific data to {style_file}")

        print(f"\n✓ All data saved to {output_dir}/")


def main():
    """Main extraction function"""

    if not MUSIC21_AVAILABLE:
        print("❌ music21 is required. Install with: pip install music21")
        return

    extractor = RealMusicDataExtractor()

    # Extract from music21 corpus
    print("Starting extraction from music21 corpus...")
    extractor.extract_from_music21(limit=100)

    # Save the data
    extractor.save_data()

    print(f"\n{'='*60}")
    print("✓ EXTRACTION COMPLETE!")
    print(f"{'='*60}")
    print("\nYou can now train on real music data:")
    print("  python train.py --task progression --epochs 30 \\")
    print("    --train-samples 3000 --d-model 256 --num-layers 4")


if __name__ == '__main__':
    main()
