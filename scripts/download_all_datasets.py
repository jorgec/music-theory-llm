#!/usr/bin/env python3
"""
Complete Dataset Downloader and Processor

Downloads and processes training data from multiple sources:
- music21 corpus (built-in, legal)
- McGill Billboard Dataset (requires download)
- Lakh MIDI Dataset (requires download)
- iReal Pro files (requires legal access)
- Hooktheory API (requires subscription)

IMPORTANT: This script respects copyright and terms of service.
Some datasets require you to obtain proper access/subscription first.
"""

import os
import sys
import json
import urllib.request
import tarfile
import zipfile
from pathlib import Path
from typing import List, Dict, Optional
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.data_loaders import TrainingDataLoader


class DatasetDownloader:
    """Downloads and processes datasets from multiple sources"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"

        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        self.loader = TrainingDataLoader(cache_dir=str(self.processed_dir))

    # ============================================================
    # 1. MUSIC21 CORPUS (Built-in, Legal)
    # ============================================================

    def download_music21_corpus(self, limit: int = 1000) -> List:
        """
        Load from music21 built-in corpus.
        This is completely legal and included with music21.
        """
        print("\n" + "=" * 80)
        print("1. MUSIC21 CORPUS")
        print("=" * 80)
        print("\nℹ️  music21 corpus is built-in and legal to use")

        try:
            from music21 import corpus

            print("\nAvailable composers:")
            composers = ['bach', 'handel', 'mozart', 'beethoven', 'chopin']

            all_progressions = []

            for composer in composers:
                print(f"\n  Loading {composer}...")
                try:
                    works = corpus.search(composer, 'composer')
                    progressions = self.loader.load_from_music21_corpus(
                        limit=limit // len(composers),
                        composers=[composer]
                    )
                    all_progressions.extend(progressions)
                    print(f"    ✓ Loaded {len(progressions)} progressions from {composer}")
                except Exception as e:
                    print(f"    ⚠ Error loading {composer}: {e}")

            # Save
            output_file = self.processed_dir / "music21_corpus.json"
            self.loader.save_progressions(all_progressions, str(output_file))

            print(f"\n✓ Total: {len(all_progressions)} progressions saved to {output_file}")
            return all_progressions

        except ImportError:
            print("\n❌ music21 not installed")
            print("   Install with: pip install music21")
            return []

    # ============================================================
    # 2. MCGILL BILLBOARD DATASET
    # ============================================================

    def download_mcgill_billboard(self) -> List:
        """
        Download McGill Billboard Dataset.

        LEGAL ACCESS:
        This dataset is available for research purposes.
        Official source: https://ddmal.music.mcgill.ca/research/billboard
        """
        print("\n" + "=" * 80)
        print("2. MCGILL BILLBOARD DATASET")
        print("=" * 80)

        mcgill_dir = self.raw_dir / "mcgill_billboard"

        # Check if already downloaded
        if mcgill_dir.exists() and len(list(mcgill_dir.glob("*.txt"))) > 0:
            print("\nℹ️  Dataset already downloaded")
            return self._process_mcgill_billboard(mcgill_dir)

        print("\n📥 DOWNLOAD INSTRUCTIONS:")
        print("-" * 80)
        print("The McGill Billboard Dataset is available for research.")
        print()
        print("To download:")
        print("1. Visit: https://ddmal.music.mcgill.ca/research/billboard")
        print("2. Read and accept the terms of use")
        print("3. Download the dataset (McGill-Billboard.zip)")
        print("4. Extract to: data/raw/mcgill_billboard/")
        print()
        print("Expected structure:")
        print("  data/raw/mcgill_billboard/")
        print("    ├── 0000.txt")
        print("    ├── 0001.txt")
        print("    └── ...")
        print()

        # Check if user has downloaded it
        if input("Have you downloaded and extracted the dataset? (y/n): ").lower() == 'y':
            if mcgill_dir.exists():
                return self._process_mcgill_billboard(mcgill_dir)
            else:
                print(f"\n❌ Directory not found: {mcgill_dir}")
                print("   Please extract the dataset to the correct location")

        print("\n⏭️  Skipping McGill Billboard dataset")
        return []

    def _process_mcgill_billboard(self, data_dir: Path) -> List:
        """Process McGill Billboard chord files"""
        print("\n📊 Processing McGill Billboard files...")

        from src.theory import Chord, ChordProgression, Scale, Note

        progressions = []
        files = list(data_dir.glob("*.txt"))

        print(f"Found {len(files)} files to process")

        for i, file_path in enumerate(files[:100]):  # Process first 100
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()

                # Parse chord annotations
                # McGill Billboard format: timestamp, chord
                chords = []
                current_key = None

                for line in lines:
                    line = line.strip()

                    # Look for key
                    if line.startswith('# tonic:'):
                        tonic = line.split(':')[1].strip()
                        try:
                            root = Note.from_string(tonic.split()[0])
                            is_major = 'major' in line.lower()
                            current_key = Scale.major(root) if is_major else Scale.minor(root)
                        except:
                            pass

                    # Look for chords (format: timestamp chord)
                    elif '\t' in line and not line.startswith('#'):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            chord_symbol = parts[1].strip()

                            # Clean up chord symbol
                            chord_symbol = chord_symbol.replace(':maj', '')
                            chord_symbol = chord_symbol.replace(':min', 'm')

                            try:
                                chord = Chord.from_symbol(chord_symbol)
                                chords.append(chord)
                            except:
                                pass

                # Create progression if we have chords
                if len(chords) >= 3:
                    # Deduplicate consecutive chords
                    unique_chords = [chords[0]]
                    for chord in chords[1:]:
                        if str(chord) != str(unique_chords[-1]):
                            unique_chords.append(chord)

                    if len(unique_chords) >= 3:
                        progression = ChordProgression(unique_chords[:16], current_key)
                        progressions.append(progression)

                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{len(files)} files...")

            except Exception as e:
                continue

        # Save
        output_file = self.processed_dir / "mcgill_billboard.json"
        self.loader.save_progressions(progressions, str(output_file))

        print(f"\n✓ Processed {len(progressions)} progressions")
        print(f"  Saved to: {output_file}")

        return progressions

    # ============================================================
    # 3. LAKH MIDI DATASET
    # ============================================================

    def download_lakh_midi(self, subset_only: bool = True) -> List:
        """
        Download Lakh MIDI Dataset.

        LEGAL ACCESS:
        This dataset is publicly available for research.
        Official source: https://colinraffel.com/projects/lmd/
        """
        print("\n" + "=" * 80)
        print("3. LAKH MIDI DATASET")
        print("=" * 80)

        lakh_dir = self.raw_dir / "lakh_midi"

        # Check if already downloaded
        if lakh_dir.exists() and len(list(lakh_dir.rglob("*.mid"))) > 10:
            print("\nℹ️  Dataset already downloaded")
            return self._process_lakh_midi(lakh_dir)

        print("\n📥 DOWNLOAD INSTRUCTIONS:")
        print("-" * 80)
        print("The Lakh MIDI Dataset is publicly available.")
        print()

        if subset_only:
            print("OPTION 1: Clean MIDI Subset (17,000 files, ~3GB)")
            print("  - Cleaner, better quality")
            print("  - Smaller download")
            print("  - Recommended for starting")
            print()
            print("Download from:")
            print("  http://hog.ee.columbia.edu/craffel/lmd/lmd_aligned.tar.gz")
            print()
            print("Extract to: data/raw/lakh_midi/")
        else:
            print("OPTION 2: Full Dataset (176,581 files, ~25GB)")
            print("  - Complete dataset")
            print("  - Much larger")
            print()
            print("Download from:")
            print("  http://hog.ee.columbia.edu/craffel/lmd/lmd_full.tar.gz")
            print()
            print("Extract to: data/raw/lakh_midi/")

        print()
        print("To download using command line:")
        print(f"  cd {self.raw_dir}")
        if subset_only:
            print("  wget http://hog.ee.columbia.edu/craffel/lmd/lmd_aligned.tar.gz")
            print("  tar -xzf lmd_aligned.tar.gz")
            print("  mv lmd_aligned lakh_midi")
        else:
            print("  wget http://hog.ee.columbia.edu/craffel/lmd/lmd_full.tar.gz")
            print("  tar -xzf lmd_full.tar.gz")
            print("  mv lmd_full lakh_midi")
        print()

        if input("Have you downloaded and extracted the dataset? (y/n): ").lower() == 'y':
            if lakh_dir.exists():
                return self._process_lakh_midi(lakh_dir)
            else:
                print(f"\n❌ Directory not found: {lakh_dir}")

        print("\n⏭️  Skipping Lakh MIDI dataset")
        return []

    def _process_lakh_midi(self, data_dir: Path, max_files: int = 500) -> List:
        """Process MIDI files from Lakh dataset"""
        print(f"\n📊 Processing Lakh MIDI files (up to {max_files})...")

        progressions = []
        midi_files = list(data_dir.rglob("*.mid"))[:max_files]

        print(f"Found {len(midi_files)} MIDI files")

        for i, midi_file in enumerate(midi_files):
            try:
                progs = self.loader.load_from_midi(str(midi_file))
                progressions.extend(progs)

                if (i + 1) % 50 == 0:
                    print(f"  Processed {i + 1}/{len(midi_files)} files...")

            except Exception as e:
                continue

        # Save
        output_file = self.processed_dir / "lakh_midi.json"
        self.loader.save_progressions(progressions, str(output_file))

        print(f"\n✓ Processed {len(progressions)} progressions from MIDI files")
        print(f"  Saved to: {output_file}")

        return progressions

    # ============================================================
    # 4. IREAL PRO
    # ============================================================

    def download_ireal_pro(self) -> List:
        """
        Process iReal Pro files.

        LEGAL ACCESS:
        You must have iReal Pro app and export your own playlists.
        DO NOT use files you don't have rights to.

        How to get legal access:
        1. Purchase iReal Pro app
        2. Export playlists to HTML format
        3. Place in data/raw/ireal_pro/
        """
        print("\n" + "=" * 80)
        print("4. IREAL PRO")
        print("=" * 80)

        ireal_dir = self.raw_dir / "ireal_pro"

        print("\n⚠️  LEGAL NOTICE:")
        print("-" * 80)
        print("iReal Pro chord charts may be copyrighted material.")
        print()
        print("To use iReal Pro data legally:")
        print("1. Purchase iReal Pro app")
        print("2. Create or download playlists within the app")
        print("3. Export YOUR playlists to HTML format")
        print("4. Place exported files in: data/raw/ireal_pro/")
        print()
        print("DO NOT use files you don't have rights to use.")
        print()

        if not ireal_dir.exists() or len(list(ireal_dir.glob("*.html"))) == 0:
            print("ℹ️  No iReal Pro files found in data/raw/ireal_pro/")
            print("   Skipping this source")
            return []

        print(f"\n📊 Found iReal Pro files in {ireal_dir}")
        print("\n⚠️  This will only process files YOU have legal rights to use")

        if input("Do you confirm these are YOUR exported playlists? (y/n): ").lower() != 'y':
            print("\n⏭️  Skipping iReal Pro")
            return []

        return self._process_ireal_pro(ireal_dir)

    def _process_ireal_pro(self, data_dir: Path) -> List:
        """
        Process iReal Pro HTML exports.
        Note: This is a simplified parser. Real implementation would need
        full iReal Pro format parsing.
        """
        print("\n📊 Processing iReal Pro files...")
        print("⚠️  Note: This is a basic parser. Some complex charts may not parse correctly.")

        from src.theory import Chord, ChordProgression, Scale, Note

        progressions = []
        html_files = list(data_dir.glob("*.html"))

        if not html_files:
            print("  No .html files found")
            return []

        print(f"Found {len(html_files)} HTML files")

        # Basic chord symbol extraction (simplified)
        # Real iReal Pro format is more complex
        import re

        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract chord symbols (very simplified)
                # Real parser would need to handle iReal Pro's specific format
                chord_pattern = r'\b([A-G][#b]?(?:maj|min|m|7|maj7|m7|dim|aug)?)\b'
                matches = re.findall(chord_pattern, content)

                if len(matches) >= 4:
                    chords = []
                    for match in matches[:16]:  # Limit to 16 chords
                        try:
                            chord = Chord.from_symbol(match)
                            chords.append(chord)
                        except:
                            pass

                    if len(chords) >= 3:
                        # Try to detect key (simplified)
                        scale = Scale.major(Note.from_string('C'))
                        progression = ChordProgression(chords, scale)
                        progressions.append(progression)

            except Exception as e:
                continue

        # Save
        if progressions:
            output_file = self.processed_dir / "ireal_pro.json"
            self.loader.save_progressions(progressions, str(output_file))
            print(f"\n✓ Processed {len(progressions)} progressions")
            print(f"  Saved to: {output_file}")
        else:
            print("\n⚠️  No valid progressions found")
            print("   iReal Pro files may need a more sophisticated parser")

        return progressions

    # ============================================================
    # 5. HOOKTHEORY
    # ============================================================

    def download_hooktheory(self, api_key: Optional[str] = None) -> List:
        """
        Access Hooktheory data via API.

        LEGAL ACCESS:
        Requires Hooktheory subscription and API access.
        DO NOT scrape their website.

        How to get legal access:
        1. Subscribe to Hooktheory Plus
        2. Request API access from Hooktheory
        3. Use the provided API key
        """
        print("\n" + "=" * 80)
        print("5. HOOKTHEORY")
        print("=" * 80)

        print("\n⚠️  LEGAL NOTICE:")
        print("-" * 80)
        print("Hooktheory data requires a subscription.")
        print()
        print("To access Hooktheory data legally:")
        print("1. Subscribe to Hooktheory Plus: https://www.hooktheory.com/plus")
        print("2. Contact Hooktheory to request API access")
        print("3. Use your API key with this script")
        print()
        print("DO NOT scrape their website - this violates their terms of service.")
        print()

        if api_key is None:
            api_key_file = self.raw_dir / "hooktheory_api_key.txt"
            if api_key_file.exists():
                with open(api_key_file, 'r') as f:
                    api_key = f.read().strip()
            else:
                print("ℹ️  No API key found")
                print(f"   To use Hooktheory API, save your key to:")
                print(f"   {api_key_file}")
                print()
                api_key = input("Enter API key (or press Enter to skip): ").strip()

                if not api_key:
                    print("\n⏭️  Skipping Hooktheory")
                    return []

        return self._fetch_hooktheory_data(api_key)

    def _fetch_hooktheory_data(self, api_key: str) -> List:
        """
        Fetch data from Hooktheory API.
        NOTE: This is a placeholder - actual API endpoints would be provided by Hooktheory.
        """
        print("\n📊 Fetching from Hooktheory API...")
        print("⚠️  Note: Actual API endpoints must be provided by Hooktheory")

        # Placeholder - would need real API endpoints
        print("\n❌ Hooktheory API integration not yet implemented")
        print("   Reason: API endpoints not publicly documented")
        print()
        print("   If you have Hooktheory API access, you can:")
        print("   1. Manually export data from Hooktheory")
        print("   2. Save as JSON in data/raw/hooktheory/")
        print("   3. Use TrainingDataLoader.load_from_json() to process")

        return []

    # ============================================================
    # MAIN ORCHESTRATION
    # ============================================================

    def download_all(
        self,
        sources: Optional[List[str]] = None,
        music21_limit: int = 1000,
        lakh_limit: int = 500
    ) -> Dict[str, List]:
        """
        Download and process all available datasets.

        Args:
            sources: List of sources to download (None = all)
            music21_limit: Max pieces from music21
            lakh_limit: Max MIDI files to process

        Returns:
            Dictionary of progressions by source
        """
        if sources is None:
            sources = ['music21', 'mcgill', 'lakh', 'ireal', 'hooktheory']

        results = {}

        print("\n" + "█" * 80)
        print(" " * 20 + "DATASET DOWNLOADER")
        print("█" * 80)
        print()
        print(f"Will attempt to download: {', '.join(sources)}")
        print()
        print("⚠️  IMPORTANT: This script respects copyright and terms of service.")
        print("   Some datasets require manual download or subscription.")
        print()

        input("Press Enter to continue...")

        # 1. music21
        if 'music21' in sources:
            try:
                results['music21'] = self.download_music21_corpus(limit=music21_limit)
            except Exception as e:
                print(f"\n❌ Error with music21: {e}")
                results['music21'] = []

        # 2. McGill Billboard
        if 'mcgill' in sources:
            try:
                results['mcgill'] = self.download_mcgill_billboard()
            except Exception as e:
                print(f"\n❌ Error with McGill: {e}")
                results['mcgill'] = []

        # 3. Lakh MIDI
        if 'lakh' in sources:
            try:
                results['lakh'] = self.download_lakh_midi(subset_only=True)
            except Exception as e:
                print(f"\n❌ Error with Lakh: {e}")
                results['lakh'] = []

        # 4. iReal Pro
        if 'ireal' in sources:
            try:
                results['ireal'] = self.download_ireal_pro()
            except Exception as e:
                print(f"\n❌ Error with iReal Pro: {e}")
                results['ireal'] = []

        # 5. Hooktheory
        if 'hooktheory' in sources:
            try:
                results['hooktheory'] = self.download_hooktheory()
            except Exception as e:
                print(f"\n❌ Error with Hooktheory: {e}")
                results['hooktheory'] = []

        # Summary
        self._print_summary(results)

        return results

    def _print_summary(self, results: Dict[str, List]):
        """Print download summary"""
        print("\n" + "=" * 80)
        print("DOWNLOAD SUMMARY")
        print("=" * 80)

        total = 0
        for source, progs in results.items():
            count = len(progs)
            total += count
            status = "✓" if count > 0 else "⏭️"
            print(f"{status} {source:15s}: {count:5d} progressions")

        print(f"\nTotal: {total} progressions")
        print(f"\nProcessed data saved to: {self.processed_dir}")

        if total > 0:
            print("\n" + "=" * 80)
            print("NEXT STEPS")
            print("=" * 80)
            print()
            print("1. Train a model:")
            print("   python train.py --task progression --epochs 20")
            print()
            print("2. Use statistical analysis:")
            print("   python examples/intelligence_demo.py")
            print()
            print("3. Fine-tune on specific styles:")
            print("   See INTELLIGENCE.md for examples")
        else:
            print("\n⚠️  No data downloaded.")
            print("   Please follow the instructions above to obtain datasets legally.")


def main():
    parser = argparse.ArgumentParser(
        description='Download and process training datasets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all (will prompt for each)
  python scripts/download_all_datasets.py

  # Download specific sources
  python scripts/download_all_datasets.py --sources music21 mcgill

  # Just music21 (fastest, no downloads needed)
  python scripts/download_all_datasets.py --sources music21 --music21-limit 500
        """
    )

    parser.add_argument(
        '--sources',
        nargs='+',
        choices=['music21', 'mcgill', 'lakh', 'ireal', 'hooktheory', 'all'],
        default=['all'],
        help='Which sources to download'
    )

    parser.add_argument(
        '--music21-limit',
        type=int,
        default=1000,
        help='Max pieces from music21 corpus'
    )

    parser.add_argument(
        '--lakh-limit',
        type=int,
        default=500,
        help='Max MIDI files to process from Lakh'
    )

    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Base data directory'
    )

    args = parser.parse_args()

    # Handle 'all' option
    if 'all' in args.sources:
        sources = ['music21', 'mcgill', 'lakh', 'ireal', 'hooktheory']
    else:
        sources = args.sources

    # Create downloader
    downloader = DatasetDownloader(data_dir=args.data_dir)

    # Download all
    results = downloader.download_all(
        sources=sources,
        music21_limit=args.music21_limit,
        lakh_limit=args.lakh_limit
    )


if __name__ == '__main__':
    main()
