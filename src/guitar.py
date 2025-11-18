"""
Guitar-Specific Music Theory Tools

Provides:
- Guitar tablature generation
- Chord inversions and voicings across the neck
- Fretboard visualization
- Eric Johnson-style intervallic chord voicings
- Artist-specific guitar techniques
"""

from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from .theory import Chord, Note, ChordQuality


# Standard guitar tuning (low to high)
STANDARD_TUNING = ['E', 'A', 'D', 'G', 'B', 'E']
STANDARD_TUNING_MIDI = [40, 45, 50, 55, 59, 64]  # E2, A2, D3, G3, B3, E4

# Alternative tunings
TUNINGS = {
    'standard': STANDARD_TUNING,
    'drop_d': ['D', 'A', 'D', 'G', 'B', 'E'],
    'drop_c': ['C', 'G', 'C', 'F', 'A', 'D'],
    'open_g': ['D', 'G', 'D', 'G', 'B', 'D'],
    'dadgad': ['D', 'A', 'D', 'G', 'A', 'D'],
}


@dataclass
class GuitarNote:
    """Represents a note on the guitar"""
    string: int  # 0-5 (0 = low E string)
    fret: int    # 0-24
    note: Note


@dataclass
class GuitarVoicing:
    """Represents a chord voicing on guitar"""
    chord: Chord
    notes: List[GuitarNote]
    inversion: int  # 0=root, 1=1st inversion, 2=2nd inversion, etc.
    position: int   # Fret position (lowest fret used)
    voicing_type: str  # 'open', 'barre', 'drop2', 'drop3', 'closed', 'intervallic'


class GuitarTablature:
    """Generate and display guitar tablature"""

    def __init__(self, tuning: List[str] = None):
        self.tuning = tuning or STANDARD_TUNING

    def generate_tab(self, notes: List[GuitarNote], width: int = 80) -> str:
        """Generate ASCII tablature for a sequence of notes"""
        # Create 6 strings
        strings = {i: ['-'] * width for i in range(6)}

        for i, note in enumerate(notes):
            if i < width:
                strings[note.string][i] = str(note.fret) if note.fret < 10 else 'X'

        # Build tab string
        tab_lines = []
        for string_num in range(5, -1, -1):  # High E to low E
            line = f"{self.tuning[string_num]}|{''.join(strings[string_num])}|"
            tab_lines.append(line)

        return '\\n'.join(tab_lines)

    def generate_chord_diagram(self, voicing: GuitarVoicing) -> str:
        """Generate ASCII chord diagram"""
        # Determine fret range
        frets_used = [n.fret for n in voicing.notes if n.fret > 0]
        if not frets_used:
            start_fret = 0
            num_frets = 5
        else:
            start_fret = max(0, min(frets_used) - 1)
            num_frets = min(5, max(frets_used) - start_fret + 2)

        # Create diagram
        diagram = []

        # Add chord name and position
        diagram.append(f"{voicing.chord.to_symbol()} - {voicing.voicing_type} voicing (fret {voicing.position})")
        diagram.append("")

        # Fret markers
        if start_fret == 0:
            diagram.append("    " + " ".join([str(i) for i in range(num_frets)]))
        else:
            diagram.append(f"   {start_fret}" + "─" * (num_frets * 2 - 1))

        # Strings
        for string_num in range(5, -1, -1):
            # Find note on this string
            string_notes = [n for n in voicing.notes if n.string == string_num]

            if not string_notes:
                # Muted string
                line = f"{self.tuning[string_num]} X "
            else:
                note = string_notes[0]
                if note.fret == 0:
                    line = f"{self.tuning[string_num]} O "
                else:
                    # Show fret position
                    fret_pos = note.fret - start_fret
                    line = f"{self.tuning[string_num]} "
                    for f in range(num_frets):
                        if f == fret_pos:
                            line += "●─"
                        else:
                            line += "──"

            diagram.append(line)

        # Add finger positions if it's a barre chord
        if voicing.voicing_type == 'barre':
            diagram.append("")
            diagram.append(f"Barre at fret {voicing.position}")

        return '\\n'.join(diagram)


class ChordInversionFinder:
    """Find all possible chord inversions across the guitar neck"""

    def __init__(self, tuning: List[int] = None):
        self.tuning = tuning or STANDARD_TUNING_MIDI
        self.num_frets = 24

    def find_all_inversions(
        self,
        chord: Chord,
        max_fret_span: int = 5,
        max_position: int = 12
    ) -> List[GuitarVoicing]:
        """Find all practical inversions of a chord up to a position"""
        inversions = []

        # Get chord tones
        chord_tones = self._get_chord_midi_notes(chord)

        # Try different positions on the neck
        for position in range(0, max_position + 1):
            # Try different inversions
            for inv_num, bass_note in enumerate(chord_tones):
                voicing = self._find_voicing_at_position(
                    chord,
                    chord_tones,
                    position,
                    inv_num,
                    max_fret_span
                )
                if voicing:
                    inversions.append(voicing)

        return inversions

    def _get_chord_midi_notes(self, chord: Chord) -> List[int]:
        """Convert chord to MIDI note numbers (one octave)"""
        root_midi = chord.root.midi  # Assuming Note has midi attribute
        return [root_midi + interval for interval in chord.quality.value]

    def _find_voicing_at_position(
        self,
        chord: Chord,
        chord_tones: List[int],
        position: int,
        inversion: int,
        max_span: int
    ) -> Optional[GuitarVoicing]:
        """Find a voicing at a specific position"""
        # This is a simplified version
        # A full implementation would use optimization to find best voicings
        notes = []

        # Try to place chord tones on strings
        for string_num, string_pitch in enumerate(self.tuning):
            for fret in range(max(0, position), min(position + max_span, self.num_frets + 1)):
                note_midi = string_pitch + fret
                # Check if this note is in the chord
                if (note_midi % 12) in [(tone % 12) for tone in chord_tones]:
                    note = GuitarNote(
                        string=string_num,
                        fret=fret,
                        note=Note.from_midi(note_midi)  # Assuming this method exists
                    )
                    notes.append(note)
                    break  # One note per string for now

        if len(notes) >= 3:  # Need at least 3 notes for a chord
            voicing_type = self._determine_voicing_type(notes, position)
            return GuitarVoicing(
                chord=chord,
                notes=notes,
                inversion=inversion,
                position=position,
                voicing_type=voicing_type
            )

        return None

    def _determine_voicing_type(self, notes: List[GuitarNote], position: int) -> str:
        """Determine the type of voicing"""
        frets = [n.fret for n in notes if n.fret > 0]

        if not frets:
            return 'open'
        elif all(f == frets[0] for f in frets):
            return 'barre'
        elif max(frets) - min(frets) <= 2:
            return 'closed'
        else:
            return 'spread'


class EricJohnsonVoicings:
    """
    Eric Johnson-style intervallic chord voicings and techniques

    Specializes in:
    - Open-voiced and spread triads with wide intervals
    - Constant use of open strings as color tones
    - Add9, 6/9, Lydian and Mixolydian colors
    - Chord melody combined with triad "soloing"
    - Open-voiced, string-skipping arpeggios
    - Pentatonic "arpeggio-like" patterns
    - Hybrid picking and "rolls"
    - Chord-arpeggio fusion techniques
    - Stacked 4ths and 5ths
    - Intervallic voicings (3rds, 4ths, 5ths, 6ths)
    """

    @staticmethod
    def get_open_voiced_triad(root: Note, position: int = 5, use_open_strings: bool = True) -> GuitarVoicing:
        """
        Generate Eric Johnson-style open-voiced/spread triads

        Uses wide intervals and string-skipping to create open, airy voicings.
        Incorporates open strings when possible for color and resonance.
        """
        notes = []

        if use_open_strings and position <= 5:
            # Use open strings as color tones (E, B, G, D, A)
            # Example: Gmaj with open B and E strings
            notes = [
                GuitarNote(string=5, fret=3, note=root),           # Root on low E (3rd fret = G)
                GuitarNote(string=3, fret=0, note=root.transpose(9)),  # Open D (9th from G = major 2nd/9th)
                GuitarNote(string=2, fret=0, note=root.transpose(4)),  # Open B (major 3rd)
                GuitarNote(string=1, fret=0, note=root.transpose(9)),  # Open high E (9th)
            ]
            voicing_type = 'open-voiced-open-strings'
        else:
            # Spread triad without open strings - wide intervals via string skipping
            notes = [
                GuitarNote(string=5, fret=position, note=root),           # Root
                GuitarNote(string=3, fret=position + 2, note=root.transpose(7)),   # 5th (skip A string)
                GuitarNote(string=1, fret=position + 4, note=root.transpose(16)),  # Root + octave + 3rd
            ]
            voicing_type = 'spread-triad'

        chord = Chord(root, ChordQuality.MAJOR)

        return GuitarVoicing(
            chord=chord,
            notes=notes,
            inversion=0,
            position=position,
            voicing_type=voicing_type
        )

    @staticmethod
    def get_add9_voicing(root: Note, position: int = 5, use_open_strings: bool = True) -> GuitarVoicing:
        """
        Eric Johnson-style add9 voicings with open strings and color tones

        Add9 chords (1-3-5-9) are signature EJ sounds, especially with open strings
        """
        notes = []

        if use_open_strings and position <= 3:
            # Add9 with open strings for shimmer
            notes = [
                GuitarNote(string=5, fret=position, note=root),
                GuitarNote(string=3, fret=0, note=root.transpose(2)),  # Open string as 9th
                GuitarNote(string=2, fret=position + 1, note=root.transpose(4)),  # 3rd
                GuitarNote(string=1, fret=0, note=root.transpose(7)),  # Open string as 5th
            ]
        else:
            # Add9 voicing without open strings
            notes = [
                GuitarNote(string=4, fret=position, note=root),
                GuitarNote(string=3, fret=position + 2, note=root.transpose(7)),  # 5th
                GuitarNote(string=2, fret=position + 2, note=root.transpose(14)), # 9th
                GuitarNote(string=1, fret=position + 3, note=root.transpose(16)), # 3rd (octave up)
            ]

        return GuitarVoicing(
            chord=Chord(root, ChordQuality.MAJOR_9),
            notes=notes,
            inversion=0,
            position=position,
            voicing_type='add9'
        )

    @staticmethod
    def get_6_9_voicing(root: Note, position: int = 7) -> GuitarVoicing:
        """
        Eric Johnson 6/9 chord voicings

        6/9 chords (1-3-5-6-9) create lush, jazzy textures
        """
        notes = [
            GuitarNote(string=5, fret=position, note=root),
            GuitarNote(string=4, fret=position + 2, note=root.transpose(7)),  # 5th
            GuitarNote(string=3, fret=position + 1, note=root.transpose(9)),  # 6th
            GuitarNote(string=2, fret=position + 2, note=root.transpose(14)), # 9th
            GuitarNote(string=1, fret=position + 2, note=root.transpose(16)), # 3rd
        ]

        return GuitarVoicing(
            chord=Chord(root, ChordQuality.MAJOR_6_9),
            notes=notes,
            inversion=0,
            position=position,
            voicing_type='6-9'
        )

    @staticmethod
    def get_lydian_color_voicing(root: Note, position: int = 5) -> GuitarVoicing:
        """
        Lydian mode colors (#11) - Eric Johnson's "Cliffs of Dover" sound

        Lydian's raised 4th (or #11 in extended harmony) creates bright, uplifting sounds
        """
        notes = [
            GuitarNote(string=5, fret=position, note=root),
            GuitarNote(string=4, fret=position + 2, note=root.transpose(7)),   # 5th
            GuitarNote(string=3, fret=position + 3, note=root.transpose(11)),  # Major 7th
            GuitarNote(string=2, fret=position + 3, note=root.transpose(18)),  # #11 (raised 4th + octave)
            GuitarNote(string=1, fret=position + 4, note=root.transpose(21)),  # 13th
        ]

        return GuitarVoicing(
            chord=Chord(root, ChordQuality.MAJOR_11),  # Using as proxy for Lydian
            notes=notes,
            inversion=0,
            position=position,
            voicing_type='lydian-color'
        )

    @staticmethod
    def get_mixolydian_color_voicing(root: Note, position: int = 5) -> GuitarVoicing:
        """
        Mixolydian mode colors (dominant 7th feel)

        Mixolydian (major scale with b7) creates bluesy-rock textures
        """
        notes = [
            GuitarNote(string=5, fret=position, note=root),
            GuitarNote(string=4, fret=position + 2, note=root.transpose(7)),  # 5th
            GuitarNote(string=3, fret=position + 1, note=root.transpose(10)), # b7th
            GuitarNote(string=2, fret=position + 2, note=root.transpose(14)), # 9th
            GuitarNote(string=1, fret=position + 2, note=root.transpose(16)), # 3rd
        ]

        return GuitarVoicing(
            chord=Chord(root, ChordQuality.DOMINANT_9),
            notes=notes,
            inversion=0,
            position=position,
            voicing_type='mixolydian-color'
        )

    @staticmethod
    def get_string_skipping_arpeggio(root: Note, position: int = 5) -> List[GuitarNote]:
        """
        Eric Johnson-style string-skipping arpeggios

        Creates open, harp-like sounds by skipping strings between notes
        """
        arpeggio = [
            GuitarNote(string=5, fret=position, note=root),               # Root
            GuitarNote(string=3, fret=position + 2, note=root.transpose(7)),   # 5th (skip A string)
            GuitarNote(string=1, fret=position + 4, note=root.transpose(12)),  # Octave (skip G, B strings)
            GuitarNote(string=2, fret=position + 1, note=root.transpose(16)),  # 3rd + octave
            GuitarNote(string=4, fret=position + 2, note=root.transpose(19)),  # 5th + octave
        ]

        return arpeggio

    @staticmethod
    def get_pentatonic_arpeggio_pattern(root: Note, position: int = 5) -> List[GuitarNote]:
        """
        Pentatonic "arpeggio-like" patterns

        Eric Johnson blends pentatonic scales with arpeggio approaches
        """
        # Major pentatonic (1-2-3-5-6) played as arpeggiated pattern
        pattern = [
            GuitarNote(string=5, fret=position, note=root),                    # 1
            GuitarNote(string=4, fret=position + 2, note=root.transpose(4)),   # 3
            GuitarNote(string=3, fret=position + 2, note=root.transpose(7)),   # 5
            GuitarNote(string=2, fret=position + 2, note=root.transpose(14)),  # 9 (2 + octave)
            GuitarNote(string=3, fret=position + 4, note=root.transpose(16)),  # 3 + octave
            GuitarNote(string=4, fret=position + 4, note=root.transpose(19)),  # 5 + octave
        ]

        return pattern

    @staticmethod
    def get_hybrid_picking_roll(root: Note, position: int = 5) -> List[GuitarNote]:
        """
        Eric Johnson-style hybrid picking "rolls"

        Combines pick and fingers to create cascading, harp-like patterns
        Typically: pick-middle-ring-middle pattern
        """
        # Descending roll pattern across adjacent strings
        roll = [
            GuitarNote(string=1, fret=position + 4, note=root.transpose(16)),  # High note (pick)
            GuitarNote(string=2, fret=position + 2, note=root.transpose(14)),  # (middle finger)
            GuitarNote(string=3, fret=position + 2, note=root.transpose(11)),  # (ring finger)
            GuitarNote(string=2, fret=position + 2, note=root.transpose(14)),  # (middle finger return)
            GuitarNote(string=1, fret=position + 4, note=root.transpose(16)),  # (pick)
        ]

        return roll

    @staticmethod
    def get_chord_arpeggio_fusion(root: Note, position: int = 5) -> List[GuitarNote]:
        """
        Chord-arpeggio fusion technique

        Seamlessly blends strummed chords with arpeggiated notes
        This is a signature Eric Johnson technique
        """
        # Alternates between chord voicing and single-note arpeggio lines
        pattern = [
            # Chord stab (multiple notes played together)
            GuitarNote(string=3, fret=position, note=root),
            GuitarNote(string=2, fret=position + 1, note=root.transpose(4)),
            GuitarNote(string=1, fret=position, note=root.transpose(7)),
            # Arpeggio continues
            GuitarNote(string=2, fret=position + 2, note=root.transpose(9)),
            GuitarNote(string=1, fret=position + 4, note=root.transpose(12)),
            # Back to chord
            GuitarNote(string=3, fret=position, note=root),
            GuitarNote(string=2, fret=position + 1, note=root.transpose(4)),
        ]

        return pattern

    @staticmethod
    def get_triad_soloing_pattern(root: Note, position: int = 5) -> List[GuitarVoicing]:
        """
        Triad "soloing" - moving triads melodically up the neck

        Eric Johnson uses triads melodically as if soloing with single notes
        """
        voicings = []

        # Move through inversions melodically
        positions = [position, position + 2, position + 4, position + 7, position + 9]
        inversions_cycle = [0, 1, 2, 0, 1]

        for pos, inv in zip(positions, inversions_cycle):
            if inv == 0:  # Root position
                notes = [
                    GuitarNote(string=3, fret=pos, note=root),
                    GuitarNote(string=2, fret=pos + 1, note=root.transpose(4)),
                    GuitarNote(string=1, fret=pos, note=root.transpose(7)),
                ]
            elif inv == 1:  # First inversion
                notes = [
                    GuitarNote(string=3, fret=pos, note=root.transpose(4)),
                    GuitarNote(string=2, fret=pos, note=root.transpose(7)),
                    GuitarNote(string=1, fret=pos + 2, note=root.transpose(12)),
                ]
            else:  # Second inversion
                notes = [
                    GuitarNote(string=3, fret=pos, note=root.transpose(7)),
                    GuitarNote(string=2, fret=pos + 2, note=root.transpose(12)),
                    GuitarNote(string=1, fret=pos + 2, note=root.transpose(16)),
                ]

            voicings.append(GuitarVoicing(
                chord=Chord(root, ChordQuality.MAJOR),
                notes=notes,
                inversion=inv,
                position=pos,
                voicing_type='triad-melody'
            ))

        return voicings

    @staticmethod
    def get_stacked_4ths_voicing(root: Note, position: int = 5) -> GuitarVoicing:
        """Generate Eric Johnson-style stacked 4ths voicing"""
        # Example: Stacked perfect 4ths creating an open, ambiguous sound
        notes = [
            GuitarNote(string=5, fret=position, note=root),  # Root on low E
            GuitarNote(string=4, fret=position + 2, note=root.transpose(5)),  # 4th
            GuitarNote(string=3, fret=position + 2, note=root.transpose(10)),  # Another 4th up
            GuitarNote(string=2, fret=position + 2, note=root.transpose(15)),  # Another 4th up
        ]

        chord = Chord(root, ChordQuality.SUSPENDED_4)

        return GuitarVoicing(
            chord=chord,
            notes=notes,
            inversion=0,
            position=position,
            voicing_type='intervallic'
        )

    @staticmethod
    def get_interval_voicings(root: Note, interval: int, position: int = 5) -> GuitarVoicing:
        """
        Generate interval-based voicings (3rds, 4ths, 5ths, 6ths)

        Args:
            root: Root note
            interval: Interval in semitones (3=minor 3rd, 4=major 3rd, 5=perfect 4th, 7=perfect 5th, 9=major 6th)
            position: Starting fret position
        """
        notes = [
            GuitarNote(string=5, fret=position, note=root),
            GuitarNote(string=4, fret=position + (interval % 12), note=root.transpose(interval)),
            GuitarNote(string=3, fret=position + ((interval * 2) % 12), note=root.transpose(interval * 2)),
        ]

        # Determine chord quality based on interval
        if interval == 4:
            quality = ChordQuality.MAJOR
        elif interval == 5:
            quality = ChordQuality.SUSPENDED_4
        elif interval == 7:
            quality = ChordQuality.POWER_CHORD
        else:
            quality = ChordQuality.MAJOR

        chord = Chord(root, quality)

        return GuitarVoicing(
            chord=chord,
            notes=notes,
            inversion=0,
            position=position,
            voicing_type='intervallic'
        )

    @staticmethod
    def get_moving_voicings(root: Note, progression_type: str = 'caged') -> List[GuitarVoicing]:
        """
        Generate a sequence of moving chord voicings up the neck

        Args:
            root: Root note
            progression_type: 'caged' (CAGED system), 'triads', or 'inversions'
        """
        voicings = []

        if progression_type == 'caged':
            # CAGED system positions
            positions = [0, 3, 5, 7, 10, 12]
            for pos in positions:
                # Simplified CAGED voicing
                notes = [
                    GuitarNote(string=5, fret=pos, note=root),
                    GuitarNote(string=3, fret=pos + 2, note=root.transpose(4)),
                    GuitarNote(string=2, fret=pos + 1, note=root.transpose(7)),
                ]

                voicings.append(GuitarVoicing(
                    chord=Chord(root, ChordQuality.MAJOR),
                    notes=notes,
                    inversion=0,
                    position=pos,
                    voicing_type='caged'
                ))

        elif progression_type == 'triads':
            # Triad inversions up the neck
            for pos in [2, 5, 7, 9, 12]:
                # Different inversions at each position
                inversion_num = (pos // 3) % 3
                notes = []

                # Root position, 1st inversion, or 2nd inversion
                if inversion_num == 0:
                    notes = [
                        GuitarNote(string=3, fret=pos, note=root),
                        GuitarNote(string=2, fret=pos + 1, note=root.transpose(4)),
                        GuitarNote(string=1, fret=pos, note=root.transpose(7)),
                    ]
                elif inversion_num == 1:
                    notes = [
                        GuitarNote(string=3, fret=pos, note=root.transpose(4)),
                        GuitarNote(string=2, fret=pos, note=root.transpose(7)),
                        GuitarNote(string=1, fret=pos + 1, note=root.transpose(12)),
                    ]
                else:
                    notes = [
                        GuitarNote(string=3, fret=pos, note=root.transpose(7)),
                        GuitarNote(string=2, fret=pos + 2, note=root.transpose(12)),
                        GuitarNote(string=1, fret=pos + 1, note=root.transpose(16)),
                    ]

                voicings.append(GuitarVoicing(
                    chord=Chord(root, ChordQuality.MAJOR),
                    notes=notes,
                    inversion=inversion_num,
                    position=pos,
                    voicing_type='triad'
                ))

        return voicings


class NeckVisualization:
    """Visualize chord voicings and inversions across the guitar neck"""

    def __init__(self, tuning: List[str] = None):
        self.tuning = tuning or STANDARD_TUNING
        self.fretboard_length = 24

    def visualize_chord_across_neck(
        self,
        chord: Chord,
        highlight_positions: List[int] = None
    ) -> str:
        """Show where a chord can be played across the entire neck"""
        output = []

        output.append(f"Chord: {chord.to_symbol()} - All positions on neck")
        output.append("=" * 80)
        output.append("")

        # Show fretboard with chord tones marked
        chord_tone_midi = [(chord.root.midi + interval) % 12 for interval in chord.quality.value]

        # Header
        fret_markers = "Fret: " + "".join([f"{i:3}" for i in range(0, 13)])
        output.append(fret_markers)
        output.append("")

        # Each string
        for string_num in range(5, -1, -1):
            line = f"{self.tuning[string_num]:2} |"

            string_pitch = STANDARD_TUNING_MIDI[string_num]

            for fret in range(13):
                note_midi = (string_pitch + fret) % 12

                if note_midi in chord_tone_midi:
                    # Mark chord tone
                    tone_index = chord_tone_midi.index(note_midi)
                    if tone_index == 0:
                        line += " R "  # Root
                    elif tone_index == 1:
                        line += " 3 "  # 3rd (or 2nd if sus2)
                    elif tone_index == 2:
                        line += " 5 "  # 5th
                    else:
                        line += " X "  # Extension
                else:
                    line += " · "

            output.append(line)

        output.append("")
        output.append("Legend: R=Root, 3=3rd, 5=5th, X=Extension/7th, ·=Not in chord")

        return "\\n".join(output)

    def visualize_inversions(
        self,
        inversions: List[GuitarVoicing]
    ) -> str:
        """Show multiple chord inversions on the fretboard"""
        output = []

        output.append(f"Chord Inversions: {inversions[0].chord.to_symbol()}")
        output.append("=" * 80)
        output.append("")

        for i, voicing in enumerate(inversions[:5], 1):
            output.append(f"Position {i}: {voicing.voicing_type} at fret {voicing.position}")
            tab = GuitarTablature()
            output.append(tab.generate_chord_diagram(voicing))
            output.append("")

        return "\\n".join(output)
