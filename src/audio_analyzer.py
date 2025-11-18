"""
Audio Analysis Module

Analyzes audio files (WAV, MP3, etc.) to extract musical information:
- Tempo detection (BPM)
- Key detection
- Chord detection
- Music theory explanations
"""

import warnings
warnings.filterwarnings('ignore')

try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("[WARNING] librosa not available. Install with: pip install librosa")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from typing import Dict, List, Tuple, Optional
from pathlib import Path

from .theory_explainer import MusicTheoryExplainer


# Musical note mappings
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
KEY_PROFILES = {
    'major': [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88],
    'minor': [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
}


class AudioAnalyzer:
    """Analyze audio files for musical content"""

    def __init__(self):
        if not LIBROSA_AVAILABLE:
            raise ImportError(
                "Audio analysis requires librosa. "
                "Install with: pip install librosa soundfile"
            )

        self.theory_explainer = MusicTheoryExplainer()

    def analyze_audio_file(self, audio_path: str) -> Dict:
        """
        Comprehensive audio analysis

        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)

        Returns:
            Dictionary with tempo, key, chords, and theory analysis
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"Loading audio file: {audio_path.name}")

        # Load audio
        try:
            y, sr = librosa.load(str(audio_path), sr=None)
        except Exception as e:
            raise RuntimeError(f"Failed to load audio file: {e}")

        duration = librosa.get_duration(y=y, sr=sr)
        print(f"Duration: {duration:.2f} seconds")
        print("Analyzing...")

        analysis = {
            'filename': audio_path.name,
            'duration': duration,
            'sample_rate': sr,
        }

        # Tempo detection
        print("  - Detecting tempo...")
        tempo_info = self._detect_tempo(y, sr)
        analysis.update(tempo_info)

        # Key detection
        print("  - Detecting key...")
        key_info = self._detect_key(y, sr)
        analysis.update(key_info)

        # Chord detection (basic)
        print("  - Analyzing harmonic content...")
        harmonic_info = self._analyze_harmony(y, sr)
        analysis.update(harmonic_info)

        # Generate theory explanation
        print("  - Generating theory explanation...")
        theory_explanation = self._generate_theory_explanation(analysis)
        analysis['theory_explanation'] = theory_explanation

        return analysis

    def _detect_tempo(self, y, sr) -> Dict:
        """Detect tempo and beat information"""
        try:
            # Onset strength
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)

            # Tempo detection
            tempo, beats = librosa.beat.beat_track(
                onset_envelope=onset_env,
                sr=sr
            )

            # Convert beats to time
            beat_times = librosa.frames_to_time(beats, sr=sr)

            # Confidence estimate based on beat regularity
            if len(beat_times) > 2:
                beat_intervals = np.diff(beat_times)
                tempo_confidence = 1.0 - (np.std(beat_intervals) / np.mean(beat_intervals))
                tempo_confidence = max(0.0, min(1.0, tempo_confidence))
            else:
                tempo_confidence = 0.5

            # Tempo range (slow, medium, fast)
            if tempo < 90:
                tempo_range = 'slow'
            elif tempo < 140:
                tempo_range = 'medium'
            else:
                tempo_range = 'fast'

            return {
                'tempo': float(tempo),
                'tempo_confidence': float(tempo_confidence),
                'tempo_range': tempo_range,
                'beat_count': len(beats),
                'beat_times': beat_times.tolist() if len(beat_times) < 100 else []
            }

        except Exception as e:
            print(f"    [WARNING] Tempo detection failed: {e}")
            return {
                'tempo': None,
                'tempo_confidence': 0.0,
                'tempo_range': 'unknown',
                'beat_count': 0,
                'beat_times': []
            }

    def _detect_key(self, y, sr) -> Dict:
        """Detect musical key using chromagram analysis"""
        try:
            # Compute chromagram
            chromagram = librosa.feature.chroma_cqt(y=y, sr=sr)

            # Average chroma over time
            chroma_mean = np.mean(chromagram, axis=1)

            # Normalize
            chroma_mean = chroma_mean / np.sum(chroma_mean)

            # Compare with key profiles
            best_correlation = -1
            best_key = None
            best_mode = None

            for key_idx in range(12):
                for mode_name, profile in KEY_PROFILES.items():
                    # Rotate profile to match key
                    rotated_profile = np.roll(profile, key_idx)
                    rotated_profile = np.array(rotated_profile) / np.sum(rotated_profile)

                    # Correlation
                    correlation = np.corrcoef(chroma_mean, rotated_profile)[0, 1]

                    if correlation > best_correlation:
                        best_correlation = correlation
                        best_key = NOTE_NAMES[key_idx]
                        best_mode = mode_name

            # Confidence based on correlation
            key_confidence = (best_correlation + 1) / 2  # Map [-1, 1] to [0, 1]

            return {
                'key': best_key,
                'mode': best_mode,
                'key_confidence': float(key_confidence),
                'chroma_profile': chroma_mean.tolist()
            }

        except Exception as e:
            print(f"    [WARNING] Key detection failed: {e}")
            return {
                'key': None,
                'mode': None,
                'key_confidence': 0.0,
                'chroma_profile': []
            }

    def _analyze_harmony(self, y, sr) -> Dict:
        """Analyze harmonic content"""
        try:
            # Chromagram for harmonic analysis
            chromagram = librosa.feature.chroma_cqt(y=y, sr=sr)

            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)

            # Harmonic-percussive separation
            y_harmonic, y_percussive = librosa.effects.hpss(y)

            # Energy ratio
            harmonic_energy = np.sum(y_harmonic ** 2)
            percussive_energy = np.sum(y_percussive ** 2)
            total_energy = harmonic_energy + percussive_energy

            harmonic_ratio = harmonic_energy / total_energy if total_energy > 0 else 0.5

            # Identify prominent pitches
            chroma_mean = np.mean(chromagram, axis=1)
            prominent_pitches = []
            threshold = np.mean(chroma_mean) + np.std(chroma_mean)

            for i, value in enumerate(chroma_mean):
                if value > threshold:
                    prominent_pitches.append(NOTE_NAMES[i])

            return {
                'harmonic_ratio': float(harmonic_ratio),
                'prominent_pitches': prominent_pitches,
                'spectral_centroid_mean': float(np.mean(spectral_centroid)),
                'spectral_rolloff_mean': float(np.mean(spectral_rolloff))
            }

        except Exception as e:
            print(f"    [WARNING] Harmonic analysis failed: {e}")
            return {
                'harmonic_ratio': 0.5,
                'prominent_pitches': [],
                'spectral_centroid_mean': 0.0,
                'spectral_rolloff_mean': 0.0
            }

    def _generate_theory_explanation(self, analysis: Dict) -> str:
        """Generate music theory explanation for audio analysis"""
        explanation_parts = []

        # Title
        explanation_parts.append(f"MUSIC THEORY ANALYSIS: {analysis['filename']}")
        explanation_parts.append("=" * 70)
        explanation_parts.append("")

        # Tempo analysis
        if analysis.get('tempo'):
            tempo = analysis['tempo']
            tempo_range = analysis.get('tempo_range', 'unknown')
            confidence = analysis.get('tempo_confidence', 0.0)

            explanation_parts.append("TEMPO:")
            explanation_parts.append(f"  BPM: {tempo:.1f}")
            explanation_parts.append(f"  Feel: {tempo_range.capitalize()}")
            explanation_parts.append(f"  Confidence: {confidence:.1%}")
            explanation_parts.append("")

            # Tempo context
            if tempo < 70:
                explanation_parts.append("  Context: Very slow tempo, typical of ballads and")
                explanation_parts.append("           ambient music. Emphasizes space and phrasing.")
            elif tempo < 90:
                explanation_parts.append("  Context: Slow to moderate tempo, common in blues,")
                explanation_parts.append("           soul, and emotional pieces.")
            elif tempo < 120:
                explanation_parts.append("  Context: Medium tempo, versatile for most genres")
                explanation_parts.append("           including rock, pop, and jazz.")
            elif tempo < 140:
                explanation_parts.append("  Context: Moderate to fast, typical of upbeat rock,")
                explanation_parts.append("           funk, and some jazz fusion.")
            else:
                explanation_parts.append("  Context: Fast tempo, common in punk, metal, bebop,")
                explanation_parts.append("           and technical virtuoso playing.")
            explanation_parts.append("")

        # Key analysis
        if analysis.get('key'):
            key = analysis['key']
            mode = analysis.get('mode', 'unknown')
            confidence = analysis.get('key_confidence', 0.0)

            explanation_parts.append("KEY AND TONALITY:")
            explanation_parts.append(f"  Key: {key} {mode.capitalize()}")
            explanation_parts.append(f"  Confidence: {confidence:.1%}")
            explanation_parts.append("")

            # Mode explanation
            if mode == 'major':
                explanation_parts.append("  Mode Characteristics:")
                explanation_parts.append("  - Major tonality: bright, happy, resolved")
                explanation_parts.append("  - Scale degrees: 1, 2, 3, 4, 5, 6, 7")
                explanation_parts.append("  - Common in: pop, rock, country, upbeat music")
            elif mode == 'minor':
                explanation_parts.append("  Mode Characteristics:")
                explanation_parts.append("  - Minor tonality: darker, melancholic, introspective")
                explanation_parts.append("  - Scale degrees: 1, 2, b3, 4, 5, b6, b7")
                explanation_parts.append("  - Common in: blues, metal, emotional pieces")
            explanation_parts.append("")

            # Diatonic chords
            if mode in ['major', 'minor']:
                explanation_parts.append(f"  Diatonic Chords in {key} {mode}:")
                if mode == 'major':
                    roman_numerals = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']
                    qualities = ['maj', 'min', 'min', 'maj', 'maj', 'min', 'dim']
                else:  # minor
                    roman_numerals = ['i', 'ii°', 'III', 'iv', 'v', 'VI', 'VII']
                    qualities = ['min', 'dim', 'maj', 'min', 'min', 'maj', 'maj']

                # Calculate chord roots
                key_idx = NOTE_NAMES.index(key)
                scale_intervals = [0, 2, 4, 5, 7, 9, 11] if mode == 'major' else [0, 2, 3, 5, 7, 8, 10]

                chord_line = "  "
                for i, (numeral, quality) in enumerate(zip(roman_numerals, qualities)):
                    chord_root = NOTE_NAMES[(key_idx + scale_intervals[i]) % 12]
                    chord_line += f"{numeral} ({chord_root}{quality})  "
                explanation_parts.append(chord_line)
                explanation_parts.append("")

        # Harmonic content
        prominent_pitches = analysis.get('prominent_pitches', [])
        if prominent_pitches:
            explanation_parts.append("PROMINENT PITCHES:")
            explanation_parts.append(f"  Detected: {', '.join(prominent_pitches)}")
            explanation_parts.append("")
            explanation_parts.append("  These pitches appear frequently in the audio,")
            explanation_parts.append("  suggesting they are important to the melody,")
            explanation_parts.append("  harmony, or both.")
            explanation_parts.append("")

        # Harmonic ratio
        harmonic_ratio = analysis.get('harmonic_ratio', 0.5)
        if harmonic_ratio > 0:
            explanation_parts.append("TEXTURE:")
            if harmonic_ratio > 0.7:
                explanation_parts.append("  Predominantly harmonic/melodic content")
                explanation_parts.append("  Suggests: sustained notes, pads, melodic lines")
            elif harmonic_ratio > 0.5:
                explanation_parts.append("  Balanced harmonic and rhythmic content")
                explanation_parts.append("  Suggests: typical band/ensemble texture")
            else:
                explanation_parts.append("  Predominantly rhythmic/percussive content")
                explanation_parts.append("  Suggests: emphasis on drums, rhythm guitar, or percussion")
            explanation_parts.append("")

        # Duration context
        duration = analysis.get('duration', 0)
        if duration > 0:
            explanation_parts.append("STRUCTURE:")
            explanation_parts.append(f"  Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)")

            if duration < 30:
                explanation_parts.append("  Length: Short excerpt or intro")
            elif duration < 120:
                explanation_parts.append("  Length: Short song/section")
            elif duration < 300:
                explanation_parts.append("  Length: Standard song length")
            else:
                explanation_parts.append("  Length: Extended piece or multiple sections")
            explanation_parts.append("")

        return '\n'.join(explanation_parts)


def analyze_audio(audio_path: str) -> Dict:
    """
    Convenience function to analyze an audio file

    Args:
        audio_path: Path to audio file

    Returns:
        Analysis dictionary with tempo, key, and theory explanation
    """
    analyzer = AudioAnalyzer()
    return analyzer.analyze_audio_file(audio_path)
