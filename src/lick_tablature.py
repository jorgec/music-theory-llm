"""
Lick Tablature Generator

Converts interval-based licks to guitar tablature with proper phrasing,
tempo, and artist-specific cadence considerations.
"""

from typing import List, Dict, Tuple
from .guitar import GuitarNote, GuitarTablature, STANDARD_TUNING_MIDI
from .theory import Note


# Tempo and beat specifications for different rhythms
RHYTHM_SPECS = {
    # Fast rhythms (16th notes, triplets)
    'fast': {'bpm': 140, 'note_duration': 0.125, 'min_notes': 8, 'typical_notes': 20},
    'shred': {'bpm': 160, 'note_duration': 0.0625, 'min_notes': 12, 'typical_notes': 32},
    'bebop': {'bpm': 200, 'note_duration': 0.125, 'min_notes': 8, 'typical_notes': 24},

    # Medium rhythms (8th notes)
    'syncopated': {'bpm': 90, 'note_duration': 0.25, 'min_notes': 6, 'typical_notes': 12},
    'flowing': {'bpm': 100, 'note_duration': 0.25, 'min_notes': 6, 'typical_notes': 12},
    'melodic-lyrical': {'bpm': 80, 'note_duration': 0.5, 'min_notes': 6, 'typical_notes': 10},

    # Slow/expressive rhythms (quarter notes, half notes)
    'lyrical-vocal': {'bpm': 60, 'note_duration': 0.5, 'min_notes': 6, 'typical_notes': 10},
    'laid-back': {'bpm': 70, 'note_duration': 0.5, 'min_notes': 6, 'typical_notes': 8},
    'smooth': {'bpm': 85, 'note_duration': 0.375, 'min_notes': 6, 'typical_notes': 10},
    'expressive-vocal': {'bpm': 120, 'note_duration': 0.25, 'min_notes': 6, 'typical_notes': 12},

    # Swing/blues rhythms
    'swung': {'bpm': 120, 'note_duration': 0.333, 'min_notes': 8, 'typical_notes': 14},
    'heavy-swung': {'bpm': 90, 'note_duration': 0.333, 'min_notes': 6, 'typical_notes': 12},
    'blues-shuffle': {'bpm': 100, 'note_duration': 0.333, 'min_notes': 8, 'typical_notes': 14},

    # Fusion/technical rhythms
    'fluid-legato': {'bpm': 130, 'note_duration': 0.125, 'min_notes': 8, 'typical_notes': 22},
    'chromatic-fluid': {'bpm': 140, 'note_duration': 0.125, 'min_notes': 8, 'typical_notes': 24},
    'two-hand-tap': {'bpm': 150, 'note_duration': 0.0625, 'min_notes': 8, 'typical_notes': 30},

    # Specialized rhythms
    'cascading-fluid': {'bpm': 120, 'note_duration': 0.125, 'min_notes': 8, 'typical_notes': 20},
    'ambient-atmospheric': {'bpm': 60, 'note_duration': 1.0, 'min_notes': 6, 'typical_notes': 10},
    'modal-sophisticated': {'bpm': 110, 'note_duration': 0.25, 'min_notes': 8, 'typical_notes': 14},
    'chord-tap-melody': {'bpm': 120, 'note_duration': 0.5, 'min_notes': 6, 'typical_notes': 12},

    # Default for unspecified
    'default': {'bpm': 120, 'note_duration': 0.25, 'min_notes': 6, 'typical_notes': 12}
}


def get_rhythm_spec(rhythm: str) -> Dict:
    """Get tempo and duration specs for a rhythm pattern"""
    return RHYTHM_SPECS.get(rhythm, RHYTHM_SPECS['default'])


def validate_lick_length(lick: Dict) -> Tuple[bool, str]:
    """
    Validate that a lick has appropriate length for its rhythm

    Returns: (is_valid, message)
    """
    rhythm = lick.get('rhythm', 'default')
    intervals = lick.get('intervals', [])
    spec = get_rhythm_spec(rhythm)

    note_count = len(intervals)
    min_notes = spec['min_notes']
    typical_notes = spec['typical_notes']

    if note_count < min_notes:
        return False, f"Too short: {note_count} notes (min {min_notes} for {rhythm})"
    elif note_count < typical_notes:
        return True, f"Acceptable: {note_count} notes (typical {typical_notes} for {rhythm})"
    else:
        return True, f"Good length: {note_count} notes for {rhythm} at {spec['bpm']} BPM"


def intervals_to_guitar_notes(
    intervals: List[int],
    key: Note,
    start_string: int = 2,
    start_fret: int = 5
) -> List[GuitarNote]:
    """
    Convert interval pattern to guitar notes on the fretboard

    Uses intelligent string selection for playable, musical fingerings.
    Prioritizes staying in position and on adjacent strings.

    Args:
        intervals: Semitone intervals from root
        key: Root note
        start_string: Starting string (0-5, where 0 is low E)
        start_fret: Starting fret position

    Returns:
        List of GuitarNote objects
    """
    guitar_notes = []

    # Map note names to MIDI offsets from C
    note_to_midi = {
        'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
    }

    # Get MIDI value of root note (default to middle C octave)
    root_midi = note_to_midi.get(key.name, 0) + 48  # C3 = 48

    current_string = start_string
    current_fret = start_fret

    # Track position range for this lick (stay within 4-5 frets when possible)
    position_min = start_fret
    position_max = start_fret + 4

    for i, interval in enumerate(intervals):
        # Calculate target MIDI note
        target_midi = root_midi + interval

        # Determine interval direction if not first note
        going_up = False
        if i > 0:
            going_up = interval > intervals[i-1]

        # Find best string/fret combination
        # Priority order:
        # 1. Same string, within position (most playable)
        # 2. Adjacent string, within position
        # 3. Same string, extend position by 1-2 frets
        # 4. Find any playable option

        best_option = None
        best_score = -1

        # Check current string and adjacent strings only (±1)
        for string_offset in [0, -1, 1]:
            test_string = current_string + string_offset

            # Skip invalid strings
            if not (0 <= test_string <= 5):
                continue

            # Calculate fret on this string
            open_string_midi = STANDARD_TUNING_MIDI[test_string]
            fret = target_midi - open_string_midi

            # Skip if fret is out of reasonable range
            if not (0 <= fret <= 19):
                continue

            # Score this option (higher is better)
            score = 0

            # Prefer same string
            if string_offset == 0:
                score += 50
            # Prefer adjacent string over jumping
            elif abs(string_offset) == 1:
                score += 30

            # Prefer staying in current position
            if position_min <= fret <= position_max:
                score += 40
            # Slight extension of position is ok
            elif position_min - 2 <= fret <= position_max + 2:
                score += 20
            # Penalize large position shifts
            else:
                score -= abs(fret - current_fret) * 5

            # Prefer small fret changes
            fret_distance = abs(fret - current_fret)
            if fret_distance <= 2:
                score += 25
            elif fret_distance <= 4:
                score += 10
            else:
                score -= fret_distance * 2

            # For ascending passages, prefer higher strings; for descending, prefer lower
            if going_up and string_offset > 0:
                score += 5
            elif not going_up and string_offset < 0:
                score += 5

            # Keep best option
            if score > best_score:
                best_score = score
                best_option = (test_string, fret)

        # Use best option found
        if best_option:
            test_string, fret = best_option

            guitar_notes.append(GuitarNote(
                string=test_string,
                fret=fret,
                note=key
            ))

            # Update position
            current_string = test_string
            current_fret = fret

            # Adjust position window if needed (move position with the lick)
            if fret < position_min:
                position_min = max(0, fret)
                position_max = position_min + 4
            elif fret > position_max:
                position_max = min(19, fret)
                position_min = max(0, position_max - 4)
        else:
            # Fallback: use current string and clamp fret
            open_string_midi = STANDARD_TUNING_MIDI[current_string]
            fret = max(0, min(19, target_midi - open_string_midi))

            guitar_notes.append(GuitarNote(
                string=current_string,
                fret=fret,
                note=key
            ))
            current_fret = fret

    return guitar_notes


def generate_lick_tablature(lick: Dict, key: Note) -> str:
    """
    Generate guitar tablature for a lick

    Args:
        lick: Lick dictionary with intervals and rhythm
        key: Root note

    Returns:
        ASCII tablature string
    """
    # Convert intervals to guitar notes
    intervals = lick['intervals']
    guitar_notes = intervals_to_guitar_notes(intervals, key)

    # Generate tablature
    tab = GuitarTablature()
    tablature = tab.generate_tab(guitar_notes, width=len(intervals) + 5)

    # Get rhythm specs
    rhythm = lick.get('rhythm', 'default')
    spec = get_rhythm_spec(rhythm)

    # Add header with rhythm info
    header = [
        f"Lick: {lick['name']}",
        f"Rhythm: {rhythm} ({spec['bpm']} BPM)",
        f"Note Duration: {spec['note_duration']} beats",
        f"Total Notes: {len(intervals)}",
        ""
    ]

    return '\n'.join(header) + '\n' + tablature


def generate_lick_tablature_with_timing(lick: Dict, key: Note) -> str:
    """
    Generate tablature with timing markers

    Shows where beats fall in the lick
    """
    intervals = lick['intervals']
    guitar_notes = intervals_to_guitar_notes(intervals, key)
    rhythm = lick.get('rhythm', 'default')
    spec = get_rhythm_spec(rhythm)

    # Create tablature strings (use wider format for double-digit frets)
    strings_data = {i: [] for i in range(6)}

    # Add timing markers (1, 2, 3, 4 for beat numbers)
    timing_line = []
    beat_counter = 1
    accumulated_time = 0

    for i, note in enumerate(guitar_notes):
        # Format fret number - always use consistent width with separator
        # Use 3 characters per fret: "0--", "5--", "10-", "12-", etc.
        if note.fret < 10:
            fret_str = str(note.fret) + '--'
        else:
            fret_str = str(note.fret) + '-'

        # Add note to appropriate string
        for s in range(6):
            if s == note.string:
                strings_data[s].append(fret_str)
            else:
                strings_data[s].append('---')

        # Add timing marker (3 chars to match fret spacing)
        accumulated_time += spec['note_duration']
        if accumulated_time >= 1.0:
            timing_line.append(str(beat_counter % 10) + '  ')
            beat_counter += 1
            accumulated_time -= 1.0
        else:
            timing_line.append('   ')

    # Build output
    output = []
    output.append(f"Lick: {lick['name']}")
    output.append(f"Tempo: {spec['bpm']} BPM | Rhythm: {rhythm}")
    output.append("")
    output.append("Timing: " + ''.join(timing_line))
    output.append("")

    # Add string lines (high to low)
    tuning = ['E', 'A', 'D', 'G', 'B', 'E']
    for string_num in range(5, -1, -1):
        line = f"{tuning[string_num]}|{''.join(strings_data[string_num])}|"
        output.append(line)

    return '\n'.join(output)


def validate_all_licks(lick_database: Dict[str, List[Dict]]) -> Dict[str, List[str]]:
    """
    Validate all licks in database for appropriate length

    Returns: Dictionary of style -> list of validation messages
    """
    results = {}

    for style, licks in lick_database.items():
        style_results = []
        for lick in licks:
            is_valid, message = validate_lick_length(lick)
            status = "[OK]" if is_valid else "[WARNING]"
            style_results.append(f"{status} {lick['name']}: {message}")

        results[style] = style_results

    return results
