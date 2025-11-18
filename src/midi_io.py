"""
MIDI Input/Output Module

Provides comprehensive MIDI reading and writing capabilities:
- Export licks to MIDI files
- Export chord progressions to MIDI files
- Import MIDI files and analyze them
- Convert between music theory representation and MIDI
"""

import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# pretty_midi is optional - only needed for multi-track MIDI
try:
    import pretty_midi
    PRETTY_MIDI_AVAILABLE = True
except ImportError:
    PRETTY_MIDI_AVAILABLE = False
    print("[INFO] pretty_midi not available - multi-track MIDI features disabled")

from .theory import Note, Chord, ChordProgression, ChordQuality
from .guitar import STANDARD_TUNING_MIDI


class MidiWriter:
    """Write music theory elements to MIDI files"""

    def __init__(self, tempo: int = 120):
        self.tempo = tempo
        self.ticks_per_beat = 480

    def lick_to_midi(
        self,
        lick: Dict,
        key: Note,
        output_path: str,
        velocity: int = 80,
        duration_beats: float = 0.25
    ) -> None:
        """
        Convert a lick to MIDI file

        Args:
            lick: Lick dictionary with intervals
            key: Root note
            output_path: Output MIDI file path
            velocity: MIDI velocity (0-127)
            duration_beats: Note duration in beats
        """
        # Create MIDI file
        mid = MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = MidiTrack()
        mid.tracks.append(track)

        # Add tempo
        track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.tempo)))

        # Add track name
        track.append(MetaMessage('track_name', name=lick['name']))

        # Map note names to MIDI numbers
        note_to_midi = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
        }

        # Get root MIDI note
        root_midi = note_to_midi.get(key.name, 0) + 60  # Middle C = 60

        # Convert intervals to MIDI notes
        intervals = lick['intervals']
        ticks_per_note = int(self.ticks_per_beat * duration_beats)

        for interval in intervals:
            midi_note = root_midi + interval

            # Ensure note is in valid MIDI range (0-127)
            midi_note = max(0, min(127, midi_note))

            # Note on
            track.append(Message('note_on', note=midi_note, velocity=velocity, time=0))

            # Note off after duration
            track.append(Message('note_off', note=midi_note, velocity=0, time=ticks_per_note))

        # Save MIDI file
        mid.save(output_path)

    def progression_to_midi(
        self,
        progression: ChordProgression,
        output_path: str,
        velocity: int = 70,
        chord_duration_beats: float = 4.0
    ) -> None:
        """
        Convert chord progression to MIDI file

        Args:
            progression: ChordProgression object
            output_path: Output MIDI file path
            velocity: MIDI velocity (0-127)
            chord_duration_beats: Duration of each chord in beats
        """
        # Create MIDI file
        mid = MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = MidiTrack()
        mid.tracks.append(track)

        # Add tempo
        track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.tempo)))

        # Add track name
        track.append(MetaMessage('track_name', name='Chord Progression'))

        # Map note names to MIDI numbers
        note_to_midi = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
        }

        ticks_per_chord = int(self.ticks_per_beat * chord_duration_beats)

        for chord in progression.chords:
            # Get root note
            root_midi = note_to_midi.get(chord.root.name, 0) + 60

            # Get chord tones based on quality
            chord_tones = self._get_chord_intervals(chord.quality)

            # Create chord notes
            chord_notes = [root_midi + interval for interval in chord_tones]

            # Ensure all notes in valid range
            chord_notes = [max(48, min(84, note)) for note in chord_notes]

            # Play chord (all notes on)
            for note in chord_notes:
                track.append(Message('note_on', note=note, velocity=velocity, time=0))

            # Release chord (all notes off after duration)
            for i, note in enumerate(chord_notes):
                time = ticks_per_chord if i == 0 else 0
                track.append(Message('note_off', note=note, velocity=0, time=time))

        # Save MIDI file
        mid.save(output_path)

    def _get_chord_intervals(self, quality: ChordQuality) -> List[int]:
        """Get intervals for a chord quality"""
        # Basic chord intervals (root, third, fifth, seventh, extensions)
        intervals_map = {
            ChordQuality.MAJOR: [0, 4, 7],
            ChordQuality.MINOR: [0, 3, 7],
            ChordQuality.DIMINISHED: [0, 3, 6],
            ChordQuality.AUGMENTED: [0, 4, 8],
            ChordQuality.DOMINANT_7: [0, 4, 7, 10],
            ChordQuality.MAJOR_7: [0, 4, 7, 11],
            ChordQuality.MINOR_7: [0, 3, 7, 10],
            ChordQuality.DIMINISHED_7: [0, 3, 6, 9],
            ChordQuality.HALF_DIMINISHED_7: [0, 3, 6, 10],
            ChordQuality.MINOR_MAJOR_7: [0, 3, 7, 11],
            ChordQuality.AUGMENTED_7: [0, 4, 8, 10],
        }

        # Try to get intervals, default to major triad
        return intervals_map.get(quality, [0, 4, 7])

    def lick_with_backing_to_midi(
        self,
        lick: Dict,
        key: Note,
        progression: ChordProgression,
        output_path: str
    ) -> None:
        """
        Create MIDI file with lick melody and chord progression backing

        Args:
            lick: Lick dictionary
            key: Root note
            progression: Chord progression for backing
            output_path: Output MIDI file path
        """
        if not PRETTY_MIDI_AVAILABLE:
            raise ImportError(
                "Multi-track MIDI requires pretty_midi. "
                "Install with: pip install pretty_midi"
            )

        # Use pretty_midi for multi-track support
        pm = pretty_midi.PrettyMIDI(initial_tempo=self.tempo)

        # Create melody instrument (lead guitar)
        melody_program = pretty_midi.instrument_name_to_program('Electric Guitar (clean)')
        melody = pretty_midi.Instrument(program=melody_program)

        # Create chord instrument (rhythm guitar)
        chord_program = pretty_midi.instrument_name_to_program('Acoustic Guitar (nylon)')
        chords = pretty_midi.Instrument(program=chord_program)

        # Map note names
        note_to_midi = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
        }

        root_midi = note_to_midi.get(key.name, 0) + 60

        # Add lick notes
        current_time = 0.0
        note_duration = 0.25  # Quarter note

        for interval in lick['intervals']:
            midi_note = root_midi + interval
            midi_note = max(0, min(127, midi_note))

            note = pretty_midi.Note(
                velocity=80,
                pitch=midi_note,
                start=current_time,
                end=current_time + note_duration
            )
            melody.notes.append(note)
            current_time += note_duration

        # Add chord progression
        chord_time = 0.0
        chord_duration = 4.0  # Whole note

        for chord in progression.chords:
            root = note_to_midi.get(chord.root.name, 0) + 60
            chord_tones = self._get_chord_intervals(chord.quality)

            for interval in chord_tones:
                midi_note = root + interval
                midi_note = max(48, min(84, midi_note))

                note = pretty_midi.Note(
                    velocity=60,
                    pitch=midi_note,
                    start=chord_time,
                    end=chord_time + chord_duration
                )
                chords.notes.append(note)

            chord_time += chord_duration

        # Add instruments to MIDI
        pm.instruments.append(melody)
        pm.instruments.append(chords)

        # Write to file
        pm.write(output_path)


class MidiReader:
    """Read and analyze MIDI files"""

    def __init__(self):
        self.note_to_name = {
            0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F',
            6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'
        }

    def read_midi_file(self, midi_path: str) -> Dict:
        """
        Read MIDI file and extract musical information

        Args:
            midi_path: Path to MIDI file

        Returns:
            Dictionary with MIDI analysis
        """
        try:
            mid = MidiFile(midi_path)

            analysis = {
                'filename': Path(midi_path).name,
                'ticks_per_beat': mid.ticks_per_beat,
                'tracks': [],
                'tempo': 120,  # Default
                'total_time': 0.0
            }

            for i, track in enumerate(mid.tracks):
                track_info = {
                    'track_number': i,
                    'track_name': 'Untitled',
                    'notes': [],
                    'messages': len(track)
                }

                current_time = 0

                for msg in track:
                    current_time += msg.time

                    if msg.type == 'set_tempo':
                        analysis['tempo'] = mido.tempo2bpm(msg.tempo)

                    elif msg.type == 'track_name':
                        track_info['track_name'] = msg.name

                    elif msg.type == 'note_on' and msg.velocity > 0:
                        note_name = self.note_to_name[msg.note % 12]
                        octave = (msg.note // 12) - 1

                        track_info['notes'].append({
                            'note': msg.note,
                            'note_name': f"{note_name}{octave}",
                            'velocity': msg.velocity,
                            'time': current_time
                        })

                analysis['tracks'].append(track_info)

            # Calculate total time
            analysis['total_time'] = mid.length

            return analysis

        except Exception as e:
            return {
                'error': str(e),
                'filename': Path(midi_path).name
            }

    def extract_melody(self, midi_path: str, track_index: int = 0) -> List[int]:
        """
        Extract melody as interval pattern from MIDI file

        Args:
            midi_path: Path to MIDI file
            track_index: Which track to extract from

        Returns:
            List of semitone intervals from first note
        """
        try:
            mid = MidiFile(midi_path)

            if track_index >= len(mid.tracks):
                return []

            track = mid.tracks[track_index]
            notes = []

            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    notes.append(msg.note)

            if not notes:
                return []

            # Convert to intervals from first note
            root = notes[0]
            intervals = [note - root for note in notes]

            return intervals

        except Exception:
            return []

    def analyze_midi_harmony(self, midi_path: str) -> Dict:
        """
        Analyze harmonic content of MIDI file

        Args:
            midi_path: Path to MIDI file

        Returns:
            Harmonic analysis including detected chords
        """
        if not PRETTY_MIDI_AVAILABLE:
            raise ImportError(
                "Harmony analysis requires pretty_midi. "
                "Install with: pip install pretty_midi"
            )

        try:
            pm = pretty_midi.PrettyMIDI(midi_path)

            analysis = {
                'key_signature': None,
                'time_signature': (4, 4),
                'tempo': pm.estimate_tempo(),
                'instruments': [],
                'total_notes': 0
            }

            for instrument in pm.instruments:
                inst_info = {
                    'name': pretty_midi.program_to_instrument_name(instrument.program),
                    'program': instrument.program,
                    'note_count': len(instrument.notes),
                    'pitch_range': (
                        min(n.pitch for n in instrument.notes) if instrument.notes else 0,
                        max(n.pitch for n in instrument.notes) if instrument.notes else 0
                    )
                }
                analysis['instruments'].append(inst_info)
                analysis['total_notes'] += len(instrument.notes)

            return analysis

        except Exception as e:
            return {'error': str(e)}

    def analyze_midi_with_theory(self, midi_path: str) -> Dict:
        """
        Comprehensive MIDI analysis with music theory explanations

        Args:
            midi_path: Path to MIDI file

        Returns:
            Dictionary with detailed analysis and theory explanations
        """
        from .theory_explainer import MusicTheoryExplainer
        from collections import Counter

        # Read basic MIDI info
        basic_analysis = self.read_midi_file(midi_path)

        # Initialize theory explainer
        explainer = MusicTheoryExplainer()

        # Comprehensive analysis
        analysis = {
            'filename': basic_analysis['filename'],
            'tempo': basic_analysis.get('tempo', 120),
            'ticks_per_beat': basic_analysis.get('ticks_per_beat', 480),
            'total_time': basic_analysis.get('total_time', 0),
            'tracks': basic_analysis.get('tracks', []),
            'track_count': len(basic_analysis.get('tracks', [])),
        }

        # Analyze all notes across all tracks
        all_notes = []
        all_pitches = []

        for track in analysis['tracks']:
            for note in track.get('notes', []):
                all_notes.append(note)
                all_pitches.append(note['midi_note'])

        analysis['total_notes'] = len(all_notes)

        # Pitch analysis
        if all_pitches:
            pitch_counter = Counter(all_pitches)
            most_common_pitches = pitch_counter.most_common(5)

            analysis['pitch_range'] = {
                'lowest': min(all_pitches),
                'highest': max(all_pitches),
                'span': max(all_pitches) - min(all_pitches)
            }

            analysis['most_common_pitches'] = [
                {'pitch': pitch, 'count': count, 'note_name': self._midi_to_note_name(pitch)}
                for pitch, count in most_common_pitches
            ]

            # Detect key from pitch distribution
            detected_key = self._detect_key_from_pitches(all_pitches)
            analysis['detected_key'] = detected_key
        else:
            analysis['pitch_range'] = None
            analysis['most_common_pitches'] = []
            analysis['detected_key'] = None

        # Extract intervals for harmonic analysis
        if len(all_pitches) > 1:
            intervals = []
            for i in range(1, len(all_pitches)):
                intervals.append(all_pitches[i] - all_pitches[i-1])

            interval_counter = Counter(intervals)
            analysis['common_intervals'] = [
                {'semitones': interval, 'count': count}
                for interval, count in interval_counter.most_common(5)
            ]
        else:
            analysis['common_intervals'] = []

        # Generate theory explanation
        analysis['theory_explanation'] = self._generate_midi_theory_explanation(analysis)

        return analysis

    def _detect_key_from_pitches(self, pitches: List[int]) -> Dict:
        """Detect key from MIDI pitches using pitch class distribution"""
        if not pitches:
            return {'key': None, 'mode': None, 'confidence': 0.0}

        # Count pitch classes (0-11)
        pitch_classes = [p % 12 for p in pitches]
        pc_counter = Counter(pitch_classes)

        # Normalize to get distribution
        total = sum(pc_counter.values())
        pc_distribution = [pc_counter.get(i, 0) / total for i in range(12)]

        # Major and minor profiles (Krumhansl-Schmuckler)
        major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
        minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

        # Normalize profiles
        major_sum = sum(major_profile)
        minor_sum = sum(minor_profile)
        major_profile = [x / major_sum for x in major_profile]
        minor_profile = [x / minor_sum for x in minor_profile]

        best_correlation = -1
        best_key = None
        best_mode = None

        # Try all keys and modes
        for tonic in range(12):
            # Rotate distribution to test this tonic
            rotated_dist = pc_distribution[tonic:] + pc_distribution[:tonic]

            # Test major
            major_corr = self._correlation(rotated_dist, major_profile)
            if major_corr > best_correlation:
                best_correlation = major_corr
                best_key = self.note_to_name[tonic]
                best_mode = 'major'

            # Test minor
            minor_corr = self._correlation(rotated_dist, minor_profile)
            if minor_corr > best_correlation:
                best_correlation = minor_corr
                best_key = self.note_to_name[tonic]
                best_mode = 'minor'

        return {
            'key': best_key,
            'mode': best_mode,
            'confidence': best_correlation
        }

    def _correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate correlation between two lists"""
        if len(x) != len(y):
            return 0.0

        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))

        var_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        var_y = sum((y[i] - mean_y) ** 2 for i in range(n))

        if var_x == 0 or var_y == 0:
            return 0.0

        denominator = (var_x * var_y) ** 0.5

        return numerator / denominator if denominator > 0 else 0.0

    def _generate_midi_theory_explanation(self, analysis: Dict) -> str:
        """Generate comprehensive theory explanation for MIDI file"""
        parts = []

        parts.append(f"MUSIC THEORY ANALYSIS: {analysis['filename']}")
        parts.append("=" * 70)
        parts.append("")

        # Basic info
        parts.append("BASIC INFORMATION:")
        parts.append(f"  Duration: {analysis['total_time']:.2f} seconds ({analysis['total_time']/60:.1f} minutes)")
        parts.append(f"  Tempo: {analysis['tempo']:.1f} BPM")
        parts.append(f"  Tracks: {analysis['track_count']}")
        parts.append(f"  Total notes: {analysis['total_notes']}")
        parts.append("")

        # Track breakdown
        if analysis['tracks']:
            parts.append("TRACKS:")
            for track in analysis['tracks']:
                parts.append(f"  Track {track['track_number']}: {track['track_name']}")
                parts.append(f"    Notes: {len(track.get('notes', []))}")
            parts.append("")

        # Key analysis
        detected_key = analysis.get('detected_key')
        if detected_key and detected_key['key']:
            parts.append("KEY AND TONALITY:")
            parts.append(f"  Detected key: {detected_key['key']} {detected_key['mode']}")
            parts.append(f"  Confidence: {detected_key['confidence']:.1%}")
            parts.append("")

            if detected_key['mode'] == 'major':
                parts.append("  Major characteristics:")
                parts.append("  - Bright, happy, resolved tonality")
                parts.append("  - Scale formula: W-W-H-W-W-W-H")
                parts.append("  - Common progressions: I-IV-V, I-V-vi-IV")
            else:
                parts.append("  Minor characteristics:")
                parts.append("  - Darker, melancholic tonality")
                parts.append("  - Scale formula: W-H-W-W-H-W-W (natural minor)")
                parts.append("  - Common progressions: i-iv-v, i-VI-III-VII")
            parts.append("")

        # Pitch range
        pitch_range = analysis.get('pitch_range')
        if pitch_range:
            low_note = self._midi_to_note_name(pitch_range['lowest'])
            high_note = self._midi_to_note_name(pitch_range['highest'])

            parts.append("PITCH RANGE:")
            parts.append(f"  Lowest: {low_note} (MIDI {pitch_range['lowest']})")
            parts.append(f"  Highest: {high_note} (MIDI {pitch_range['highest']})")
            parts.append(f"  Span: {pitch_range['span']} semitones")
            parts.append("")

            # Range context
            if pitch_range['span'] <= 12:
                parts.append("  Range: Narrow (within 1 octave)")
                parts.append("  Suggests: melodic line, single-note solo")
            elif pitch_range['span'] <= 24:
                parts.append("  Range: Moderate (1-2 octaves)")
                parts.append("  Suggests: typical melodic range")
            else:
                parts.append("  Range: Wide (2+ octaves)")
                parts.append("  Suggests: complex arrangement, multiple voices, or virtuosic playing")
            parts.append("")

        # Most common pitches
        common_pitches = analysis.get('most_common_pitches', [])
        if common_pitches:
            parts.append("MOST COMMON PITCHES:")
            for i, pitch_info in enumerate(common_pitches[:5], 1):
                parts.append(f"  {i}. {pitch_info['note_name']} ({pitch_info['count']} occurrences)")
            parts.append("")
            parts.append("  These pitches form the core of the melody/harmony")
            parts.append("")

        # Common intervals
        common_intervals = analysis.get('common_intervals', [])
        if common_intervals:
            interval_names = {
                0: 'Unison/Repeat',
                1: 'Minor 2nd (half step)',
                2: 'Major 2nd (whole step)',
                3: 'Minor 3rd',
                4: 'Major 3rd',
                5: 'Perfect 4th',
                6: 'Tritone',
                7: 'Perfect 5th',
                8: 'Minor 6th',
                9: 'Major 6th',
                10: 'Minor 7th',
                11: 'Major 7th',
                12: 'Octave'
            }

            parts.append("COMMON INTERVALS:")
            for i, interval_info in enumerate(common_intervals[:5], 1):
                semitones = interval_info['semitones']
                abs_semitones = abs(semitones)
                direction = "up" if semitones > 0 else "down" if semitones < 0 else "repeat"
                name = interval_names.get(abs_semitones, f'{abs_semitones} semitones')
                parts.append(f"  {i}. {name} ({direction}) - {interval_info['count']} times")
            parts.append("")

        return '\n'.join(parts)


def export_lick_to_midi(lick: Dict, key: Note, output_path: str, tempo: int = 120) -> str:
    """
    Convenience function to export a lick to MIDI

    Args:
        lick: Lick dictionary
        key: Root note
        output_path: Output file path
        tempo: Tempo in BPM

    Returns:
        Path to created MIDI file
    """
    writer = MidiWriter(tempo=tempo)
    writer.lick_to_midi(lick, key, output_path)
    return output_path


def export_progression_to_midi(
    progression: ChordProgression,
    output_path: str,
    tempo: int = 120
) -> str:
    """
    Convenience function to export progression to MIDI

    Args:
        progression: ChordProgression object
        output_path: Output file path
        tempo: Tempo in BPM

    Returns:
        Path to created MIDI file
    """
    writer = MidiWriter(tempo=tempo)
    writer.progression_to_midi(progression, output_path)
    return output_path


def import_midi_as_lick(midi_path: str, lick_name: str = None) -> Dict:
    """
    Import MIDI file and convert to lick format

    Args:
        midi_path: Path to MIDI file
        lick_name: Optional name for the lick

    Returns:
        Lick dictionary
    """
    reader = MidiReader()
    intervals = reader.extract_melody(midi_path)

    if not intervals:
        return None

    lick = {
        'name': lick_name or Path(midi_path).stem,
        'intervals': intervals,
        'rhythm': 'imported',
        'description': f'Imported from {Path(midi_path).name}',
        'techniques': ['imported-midi']
    }

    return lick
