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
