#!/usr/bin/env python3
"""
Lick Enhancement Utility

Helps enhance existing licks by adding:
- Chromatic approach tones
- Harmonic context
- Target note identification
- Extended techniques

Usage:
    python enhance_licks.py --interactive
    python enhance_licks.py --suggest-chromatic "0,4,7,12"
    python enhance_licks.py --analyze-lick "0,4,7,12" --key C
"""

import argparse
import sys
from typing import List, Dict, Tuple


# Note names
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Chord tone intervals (relative to root)
CHORD_TONES = {
    'major': [0, 4, 7],           # R, 3, 5
    'minor': [0, 3, 7],           # R, b3, 5
    'dominant_7': [0, 4, 7, 10],  # R, 3, 5, b7
    'major_7': [0, 4, 7, 11],     # R, 3, 5, 7
    'minor_7': [0, 3, 7, 10],     # R, b3, 5, b7
}

# Extensions
EXTENSIONS = {
    '9th': 2,
    '11th': 5,
    '13th': 9
}

# Chromatic approach suggestions
CHROMATIC_APPROACHES = {
    'from_below': lambda target: target - 1,
    'from_above': lambda target: target + 1,
    'enclosure_below_above': lambda target: [target - 1, target + 1, target],
    'enclosure_above_below': lambda target: [target + 1, target - 1, target],
}


def analyze_intervals(intervals: List[int]) -> Dict:
    """Analyze interval pattern for complexity and characteristics"""
    if not intervals:
        return {}

    analysis = {
        'length': len(intervals),
        'range': max(intervals) - min(intervals),
        'unique_intervals': len(set(intervals)),
        'chord_tones_detected': [],
        'possible_extensions': [],
        'chromatic_steps': [],
        'large_leaps': []
    }

    # Detect chord tones
    for chord_type, tones in CHORD_TONES.items():
        matches = sum(1 for i in intervals if (i % 12) in tones)
        if matches >= 2:
            analysis['chord_tones_detected'].append(chord_type)

    # Detect extensions
    for ext_name, ext_interval in EXTENSIONS.items():
        if any((i % 12) == ext_interval for i in intervals):
            analysis['possible_extensions'].append(ext_name)

    # Find chromatic steps
    for i in range(1, len(intervals)):
        if abs(intervals[i] - intervals[i-1]) == 1:
            analysis['chromatic_steps'].append((intervals[i-1], intervals[i]))

    # Find large leaps
    for i in range(1, len(intervals)):
        leap = abs(intervals[i] - intervals[i-1])
        if leap >= 7:  # 5th or larger
            analysis['large_leaps'].append((intervals[i-1], intervals[i], leap))

    return analysis


def suggest_chromatic_approaches(intervals: List[int], target_indices: List[int] = None) -> Dict:
    """Suggest chromatic approaches for target notes in the lick"""
    if not intervals:
        return {}

    # If no targets specified, identify likely targets (chord tones, highest/lowest notes)
    if target_indices is None:
        target_indices = []

        # Add first and last notes as targets
        target_indices.extend([0, len(intervals) - 1])

        # Add highest and lowest notes
        max_val = max(intervals)
        min_val = min(intervals)
        target_indices.extend([i for i, v in enumerate(intervals) if v in [max_val, min_val]])

        # Remove duplicates
        target_indices = list(set(target_indices))

    suggestions = {}

    for idx in target_indices:
        if idx >= len(intervals):
            continue

        target_note = intervals[idx]
        note_suggestions = []

        # Single chromatic from below
        approach_below = target_note - 1
        note_suggestions.append({
            'type': 'chromatic_below',
            'approach_note': approach_below,
            'new_pattern': intervals[:idx] + [approach_below, target_note] + intervals[idx+1:],
            'description': f'Add chromatic approach from below ({approach_below} → {target_note})'
        })

        # Single chromatic from above
        approach_above = target_note + 1
        note_suggestions.append({
            'type': 'chromatic_above',
            'approach_note': approach_above,
            'new_pattern': intervals[:idx] + [approach_above, target_note] + intervals[idx+1:],
            'description': f'Add chromatic approach from above ({approach_above} → {target_note})'
        })

        # Enclosure (below-above-target)
        enclosure_ba = [target_note - 1, target_note + 1, target_note]
        note_suggestions.append({
            'type': 'enclosure_below_above',
            'approach_notes': enclosure_ba,
            'new_pattern': intervals[:idx] + enclosure_ba + intervals[idx+1:],
            'description': f'Enclose from below-above ({target_note-1}, {target_note+1}, {target_note})'
        })

        # Diatonic-chromatic approach
        if idx > 0:
            prev_note = intervals[idx - 1]
            # Add chromatic between previous and target
            if abs(target_note - prev_note) > 1:
                chromatic_between = prev_note + 1 if target_note > prev_note else prev_note - 1
                note_suggestions.append({
                    'type': 'diatonic_chromatic',
                    'approach_note': chromatic_between,
                    'new_pattern': intervals[:idx] + [chromatic_between, target_note] + intervals[idx+1:],
                    'description': f'Add chromatic passing tone between {prev_note} and {target_note}'
                })

        suggestions[f'note_{idx}_({target_note})'] = note_suggestions

    return suggestions


def identify_target_notes(intervals: List[int], chord_type: str = 'major') -> List[Tuple[int, str]]:
    """Identify which notes are chord tones, extensions, etc."""
    chord_tones = CHORD_TONES.get(chord_type, CHORD_TONES['major'])

    targets = []
    for i, interval in enumerate(intervals):
        interval_class = interval % 12

        if interval_class in chord_tones:
            # Identify which chord tone
            if interval_class == 0:
                targets.append((i, 'Root'))
            elif interval_class == chord_tones[1]:
                targets.append((i, '3rd'))
            elif interval_class == chord_tones[2]:
                targets.append((i, '5th'))
            elif len(chord_tones) > 3 and interval_class == chord_tones[3]:
                targets.append((i, '7th'))
        elif interval_class == EXTENSIONS['9th']:
            targets.append((i, '9th (extension)'))
        elif interval_class == EXTENSIONS['11th']:
            targets.append((i, '11th (extension)'))
        elif interval_class == EXTENSIONS['13th']:
            targets.append((i, '13th (extension)'))

    return targets


def format_intervals_as_notes(intervals: List[int], key: str = 'C') -> str:
    """Format intervals as actual note names"""
    try:
        root_idx = NOTE_NAMES.index(key)
    except ValueError:
        root_idx = 0  # Default to C

    notes = []
    for interval in intervals:
        note_idx = (root_idx + interval) % 12
        octave = (root_idx + interval) // 12
        notes.append(f"{NOTE_NAMES[note_idx]}{octave if octave > 0 else ''}")

    return ', '.join(notes)


def interactive_enhance():
    """Interactive mode for enhancing a lick"""
    print("=" * 80)
    print(" LICK ENHANCEMENT UTILITY")
    print("=" * 80)
    print()

    # Get lick intervals
    print("Enter the lick's interval pattern")
    print("Example: 0, 4, 7, 12 (for a major triad)")
    intervals_input = input("Intervals: ").strip()

    try:
        intervals = [int(x.strip()) for x in intervals_input.split(',')]
    except ValueError:
        print("[ERROR] Invalid format. Use comma-separated numbers.")
        return

    # Get key for note names
    key = input("Key (default C): ").strip() or 'C'

    # Analyze the lick
    print("\n" + "=" * 80)
    print(" ANALYSIS")
    print("=" * 80)

    analysis = analyze_intervals(intervals)

    print(f"\nInterval pattern: {intervals}")
    print(f"In key of {key}: {format_intervals_as_notes(intervals, key)}")
    print(f"\nLength: {analysis['length']} notes")
    print(f"Range: {analysis['range']} semitones")
    print(f"Unique intervals: {analysis['unique_intervals']}")

    if analysis['chord_tones_detected']:
        print(f"Possible chord types: {', '.join(analysis['chord_tones_detected'])}")

    if analysis['possible_extensions']:
        print(f"Extensions present: {', '.join(analysis['possible_extensions'])}")

    if analysis['chromatic_steps']:
        print(f"Chromatic steps: {len(analysis['chromatic_steps'])}")

    if analysis['large_leaps']:
        print(f"Large leaps: {len(analysis['large_leaps'])}")

    # Identify target notes
    print("\n" + "=" * 80)
    print(" TARGET NOTES")
    print("=" * 80)

    chord_type = input("\nChord type (major/minor/dominant_7/major_7/minor_7) [major]: ").strip() or 'major'
    targets = identify_target_notes(intervals, chord_type)

    if targets:
        print("\nChord tones and extensions in this lick:")
        for idx, role in targets:
            print(f"  Note {idx}: {intervals[idx]} ({role})")
    else:
        print("\n[INFO] No obvious chord tones detected. Consider adding some!")

    # Suggest chromatic approaches
    print("\n" + "=" * 80)
    print(" CHROMATIC APPROACH SUGGESTIONS")
    print("=" * 80)

    target_indices = [idx for idx, _ in targets] if targets else None
    suggestions = suggest_chromatic_approaches(intervals, target_indices)

    for note_key, note_suggestions in suggestions.items():
        print(f"\n{note_key}:")
        for i, sug in enumerate(note_suggestions[:3], 1):  # Show top 3
            print(f"  {i}. {sug['description']}")
            print(f"     New pattern: {sug['new_pattern']}")

    # Ask if user wants to apply a suggestion
    print("\n" + "=" * 80)
    print(" APPLY ENHANCEMENT?")
    print("=" * 80)

    apply = input("\nWould you like to use one of these suggestions? (y/n): ").strip().lower()

    if apply == 'y':
        print("\nEnter the new interval pattern:")
        new_intervals_input = input("New intervals: ").strip()

        try:
            new_intervals = [int(x.strip()) for x in new_intervals_input.split(',')]
            print(f"\n[OK] Enhanced pattern: {new_intervals}")
            print(f"In key of {key}: {format_intervals_as_notes(new_intervals, key)}")

            # Re-analyze
            new_analysis = analyze_intervals(new_intervals)
            print(f"\nNew length: {new_analysis['length']} notes (+{new_analysis['length'] - analysis['length']})")
            print(f"New chromatic steps: {len(new_analysis['chromatic_steps'])} "
                  f"(+{len(new_analysis['chromatic_steps']) - len(analysis['chromatic_steps'])})")

        except ValueError:
            print("[ERROR] Invalid format.")

    print("\n" + "=" * 80)
    print("Done! Use this enhanced pattern in add_training_data.py")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Enhance licks with chromatic approaches and harmonic context',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python enhance_licks.py --interactive

  # Analyze a lick
  python enhance_licks.py --analyze-lick "0,4,7,12" --key C

  # Get chromatic suggestions
  python enhance_licks.py --suggest-chromatic "0,4,7,12"
        """
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--interactive', action='store_true',
                           help='Interactive enhancement mode')
    mode_group.add_argument('--analyze-lick', type=str, metavar='INTERVALS',
                           help='Analyze a lick (comma-separated intervals)')
    mode_group.add_argument('--suggest-chromatic', type=str, metavar='INTERVALS',
                           help='Suggest chromatic approaches for a lick')

    # Optional arguments
    parser.add_argument('--key', type=str, default='C',
                       help='Musical key for note names (default: C)')
    parser.add_argument('--chord-type', type=str,
                       choices=['major', 'minor', 'dominant_7', 'major_7', 'minor_7'],
                       default='major',
                       help='Chord type for target identification')

    args = parser.parse_args()

    if args.interactive or (not args.analyze_lick and not args.suggest_chromatic):
        interactive_enhance()

    elif args.analyze_lick:
        try:
            intervals = [int(x.strip()) for x in args.analyze_lick.split(',')]
        except ValueError:
            print("[ERROR] Invalid interval format")
            return 1

        print("=" * 80)
        print(" LICK ANALYSIS")
        print("=" * 80)

        analysis = analyze_intervals(intervals)
        print(f"\nInterval pattern: {intervals}")
        print(f"In key of {args.key}: {format_intervals_as_notes(intervals, args.key)}")
        print(f"Length: {analysis['length']} notes")
        print(f"Range: {analysis['range']} semitones")
        print(f"Unique intervals: {analysis['unique_intervals']}")

        if analysis['chord_tones_detected']:
            print(f"Possible chord types: {', '.join(analysis['chord_tones_detected'])}")

        if analysis['chromatic_steps']:
            print(f"Chromatic steps: {len(analysis['chromatic_steps'])}")

        targets = identify_target_notes(intervals, args.chord_type)
        if targets:
            print(f"\nTarget notes ({args.chord_type}):")
            for idx, role in targets:
                print(f"  Note {idx}: {intervals[idx]} ({role})")

    elif args.suggest_chromatic:
        try:
            intervals = [int(x.strip()) for x in args.suggest_chromatic.split(',')]
        except ValueError:
            print("[ERROR] Invalid interval format")
            return 1

        print("=" * 80)
        print(" CHROMATIC APPROACH SUGGESTIONS")
        print("=" * 80)

        suggestions = suggest_chromatic_approaches(intervals)

        for note_key, note_suggestions in suggestions.items():
            print(f"\n{note_key}:")
            for i, sug in enumerate(note_suggestions, 1):
                print(f"  {i}. {sug['description']}")
                print(f"     Pattern: {sug['new_pattern']}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
