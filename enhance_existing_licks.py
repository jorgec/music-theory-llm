#!/usr/bin/env python3
"""
Enhance Existing Licks Script

Systematically adds:
- Chromatic approaches
- Extensions (9ths, 11ths, 13ths)
- Chord context
- Functional harmony
- Target notes
"""

from src.recommender import LickRecommender


def add_chromatic_approach(intervals, target_idx):
    """Add chromatic approach before a target note"""
    if target_idx > 0:
        target = intervals[target_idx]
        approach = target - 1  # Chromatic from below
        return intervals[:target_idx] + [approach] + intervals[target_idx:]
    return intervals


def add_extension(intervals, extension_type='9th'):
    """Add an extension to the interval pattern"""
    extensions = {
        '9th': 14,  # 9th = 2 + octave
        '11th': 17,  # 11th = 5 + octave
        '13th': 21   # 13th = 9 + octave
    }

    # Add extension at a musically appropriate point (usually near the end)
    ext_interval = extensions.get(extension_type, 14)
    return intervals[:-1] + [ext_interval] + [intervals[-1]]


def enhance_blues_lick(lick):
    """Enhance a blues lick with chromatic approaches and extensions"""
    name = lick['name']
    intervals = lick['intervals'].copy()

    # Determine chord type based on intervals
    if 'Turnaround' in name:
        chord_context = 'A7 → F#7 → Bm7 → E7 (I-VI-ii-V)'
        functional_harmony = 'Turnaround progression in A blues'
        target_notes = 'A (R), C# (3rd), E (5th)'
    elif 'BB King' in name or 'Classic Blues Box' in name:
        chord_context = 'A7, A9'
        functional_harmony = 'I7 dominant blues vamp'
        target_notes = 'A (R), C# (3rd), G (b7)'
        # Add 9th extension
        intervals = intervals[:-1] + [14, intervals[-1]]
    elif 'Albert King' in name:
        chord_context = 'Am7, A7'
        functional_harmony = 'I minor blues'
        target_notes = 'A (R), C (b3), E (5th), G (b7)'
        # Add chromatic approach to 5th
        if 5 in intervals:
            idx = intervals.index(5)
            intervals = intervals[:idx] + [4] + intervals[idx:]
    elif 'Stevie Ray' in name:
        chord_context = 'A7#9, A9'
        functional_harmony = 'I7#9 Hendrix chord'
        target_notes = 'A (R), C# (3rd), G (b7), B# (# 9th)'
        # Add 13th extension
        intervals = intervals[:- 1] + [21, intervals[-1]]
    elif 'Double Stop' in name:
        chord_context = 'A7, D7 (I-IV progression)'
        functional_harmony = 'I-IV blues shuffle'
        target_notes = 'A (R), C# (3rd), E (5th) - played as double-stops'
        # Add chromatic passing tone
        intervals = intervals[:3] + [4, 5] + intervals[4:]
    elif 'Slide Blues' in name:
        chord_context = 'Open A or E tuning blues'
        functional_harmony = 'I7 slide blues'
        target_notes = 'Root, 5th, b7th, octave'
        # Add chromatic approach
        intervals = intervals[:2] + [6, 7] + intervals[2:]
    elif 'Muddy Waters' in name:
        chord_context = 'A7, Chicago blues'
        functional_harmony = 'I7 in 12-bar blues'
        target_notes = 'A (R), C (b3), C# (blue note), E (5th)'
        # Add 9th extension
        intervals = intervals + [14]
    elif 'T-Bone Walker' in name:
        chord_context = 'A9, A13 (jazz-blues)'
        functional_harmony = 'I9 in jump blues / jazz-blues'
        target_notes = 'E (5th), G (b7), B (9th), F# (13th)'
        # Add 13th
        intervals = intervals[:-1] + [21, intervals[-1]]
    elif 'Diminished' in name:
        chord_context = 'A7b9, Adim7 passing chord'
        functional_harmony = 'Diminished passing tones over dominant'
        target_notes = 'A (R), C (b3), Eb (dim5), Gb (bb7)'
        # Already has chromatic, add extensions
        intervals = intervals + [14, 17]
    elif 'John Mayer Cascading' in name:
        chord_context = 'Am7, A7 (blues-rock)'
        functional_harmony = 'I7/i7 in blues-rock context'
        target_notes = 'A (R), C (b3), G (b7)'
        # Add chromatic passing tones
        intervals = [12, 11, 10, 8, 7, 6, 5, 3, 2, 1, 0, -1, -2]
    elif 'John Mayer Hendrix' in name:
        chord_context = 'A7#9 (Hendrix chord)'
        functional_harmony = 'I7#9 blues-rock'
        target_notes = 'A (R), C# (3rd), E (5th), C (b9/b3 ambiguity)'
        # Add 9th extension
        intervals = intervals + [14]
    elif 'John Mayer Chord Melody' in name:
        chord_context = 'A9, A13 (chord melody)'
        functional_harmony = 'I9/I13 chord melody blues'
        target_notes = 'A (R), E (5th), G (b7), D (11th/4th)'
        # Add chromatic approach
        intervals = intervals[:3] + [13, 14] + intervals[3:]
    elif 'Josh Smith String Bending' in name:
        chord_context = 'A7, A9'
        functional_harmony = 'I7 blues with expressive bends'
        target_notes = 'A (R), C (b3→3), E (5th), G (b7→7)'
        # Add 9th
        intervals = intervals + [14]
    elif 'Josh Smith Blues-Fusion' in name:
        chord_context = 'A9, Amaj9 (blues-jazz)'
        functional_harmony = 'I9 blues-jazz progression'
        target_notes = 'A (R), B (9th), C# (3rd), E (5th)'
        # Already has chromatic, add 13th
        intervals = intervals[:-1] + [21, intervals[-1]]
    elif 'Josh Smith Pentatonic' in name:
        chord_context = 'A7, A9'
        functional_harmony = 'I7 pentatonic blues with pivot technique'
        target_notes = 'A (R pivot), C (b3), E (5th), G (b7)'
        # Add chromatic approaches
        intervals = [0, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 10, 7, 5, 3]
    elif 'Eric Johnson Violin' in name:
        chord_context = 'Am7, A7 (blues-rock with clean tone)'
        functional_harmony = 'I7 blues with sustained melodic phrases'
        target_notes = 'A (R), C (b3), E (5th), G (b7), D (11th)'
        # Add 11th extension
        intervals = intervals + [17]
    elif 'Eric Johnson Pentatonic Cascades' in name:
        chord_context = 'Am pentatonic, A blues scale'
        functional_harmony = 'I minor pentatonic cascading phrases'
        target_notes = 'A (R), C (b3), E (5th), G (b7)'
        # Add chromatic passing tones
        intervals = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    elif 'Eric Johnson Chord-Melody' in name:
        chord_context = 'A9, Amaj9 (chord melody)'
        functional_harmony = 'I9/Imaj9 chord melody lines'
        target_notes = 'A (R), C# (3rd or maj3), E (5th), B (9th)'
        # Add chromatic approach and 13th
        intervals = [0, 3, 4, 7, 10, 12, 14, 16, 19, 21, 22]
    elif 'Joe Bonamassa Power' in name:
        chord_context = 'A7, A9'
        functional_harmony = 'I7 power blues with authority'
        target_notes = 'A (R), C# (3rd), G (b7), D (11th)'
        # Add 11th and chromatic
        intervals = intervals[:4] + [9, 10] + intervals[4:] + [17]
    elif 'Joe Bonamassa British' in name:
        chord_context = 'A7, A9 (British blues)'
        functional_harmony = 'I7 Clapton/Beck-style blues'
        target_notes = 'A (R), C# (3rd), F# (6th), G (b7)'
        # Add 9th extension
        intervals = intervals[:-1] + [14, intervals[-1]]
    elif 'Joe Bonamassa String Bending Masterclass' in name:
        chord_context = 'A7, A9'
        functional_harmony = 'I7 expressive blues bending'
        target_notes = 'A (R), C (b3→3 bend), G (b7→7 bend)'
        # Add 9th and 13th
        intervals = intervals + [14, 21]
    else:
        # Default blues context
        chord_context = 'A7, A9'
        functional_harmony = 'I7 blues dominant'
        target_notes = 'A (R), C# (3rd), G (b7)'

    # Create enhanced lick
    enhanced = {
        'name': lick['name'],
        'artist': lick.get('artist', 'Traditional blues'),
        'intervals': intervals,
        'rhythm': lick['rhythm'],
        'note_duration': 0.25,
        'bpm': 120,
        'description': lick['description'],
        'chord_context': chord_context,
        'functional_harmony': functional_harmony,
        'target_notes': target_notes,
        'techniques': lick['techniques']
    }

    return enhanced


def main():
    recommender = LickRecommender()
    blues_licks = recommender.lick_database['blues']

    print("=" * 80)
    print(" ENHANCED BLUES LICKS")
    print("=" * 80)
    print()

    enhanced_licks = []
    for lick in blues_licks:
        try:
            enhanced = enhance_blues_lick(lick)
            enhanced_licks.append(enhanced)
            print(f"✅ Enhanced: {lick['name']}")
            print(f"   Chord Context: {enhanced['chord_context']}")
            print(f"   Target Notes: {enhanced['target_notes']}")
            print()
        except Exception as e:
            print(f"❌ Error enhancing {lick['name']}: {e}")

    print(f"\nTotal enhanced: {len(enhanced_licks)}/22")

    # Print Python code for copy-paste
    print("\n" + "=" * 80)
    print(" PYTHON CODE (for src/recommender.py)")
    print("=" * 80)
    print()
    print("'blues': [")
    for lick in enhanced_licks:
        print("    {")
        for key, value in lick.items():
            if isinstance(value, str):
                print(f"        '{key}': '{value}',")
            elif isinstance(value, list):
                if key == 'intervals':
                    print(f"        '{key}': {value},")
                else:
                    print(f"        '{key}': {value},")
            else:
                print(f"        '{key}': {value},")
        print("    },")
    print("],")


if __name__ == '__main__':
    main()
