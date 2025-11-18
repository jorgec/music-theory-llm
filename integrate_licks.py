#!/usr/bin/env python3
"""
Automatically integrate new advanced licks from NEW_ADVANCED_LICKS.md into src/recommender.py
"""

import re


def parse_licks_from_markdown():
    """Parse lick dictionaries from markdown file"""
    with open('NEW_ADVANCED_LICKS.md', 'r') as f:
        content = f.read()

    # Organize by style based on section headers
    licks_by_style = {
        'blues': [],
        'neo_soul': [],
        'rock_fusion': [],
        'progressive_metal': [],
        'jazz': []
    }

    # Track current style as we read the file
    current_style = None
    pattern = r'```python\n(\{.+?\})\n```'

    # Split into lines and process
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Check for style headers
        if 'ADVANCED BLUES LICKS' in line:
            current_style = 'blues'
        elif 'ADVANCED NEO SOUL LICKS' in line:
            current_style = 'neo_soul'
        elif 'ADVANCED ROCK FUSION LICKS' in line:
            current_style = 'rock_fusion'
        elif 'ADVANCED PROGRESSIVE METAL LICKS' in line:
            current_style = 'progressive_metal'
        elif 'ADVANCED JAZZ LICKS' in line:
            current_style = 'jazz'

    # Now extract licks by searching in each section
    sections = re.split(r'\n## ADVANCED', content)
    for section in sections:
        if 'BLUES LICKS' in section:
            style = 'blues'
        elif 'NEO SOUL LICKS' in section:
            style = 'neo_soul'
        elif 'ROCK FUSION LICKS' in section:
            style = 'rock_fusion'
        elif 'PROGRESSIVE METAL LICKS' in section:
            style = 'progressive_metal'
        elif 'JAZZ LICKS' in section:
            style = 'jazz'
        else:
            continue

        # Extract all licks from this section
        lick_matches = re.findall(pattern, section, re.DOTALL)
        licks_by_style[style].extend(lick_matches)

    return licks_by_style


def integrate_licks_into_recommender(licks_by_style):
    """Integrate licks into src/recommender.py"""
    with open('src/recommender.py', 'r') as f:
        lines = f.readlines()

    # Find insertion points for each style
    insertion_points = {}
    current_style = None

    for i, line in enumerate(lines):
        if "'blues': [" in line:
            current_style = 'blues'
        elif "'neo_soul': [" in line:
            current_style = 'neo_soul'
        elif "'rock_fusion': [" in line:
            current_style = 'rock_fusion'
        elif "'progressive_metal': [" in line:
            current_style = 'progressive_metal'
        elif "'jazz': [" in line:
            current_style = 'jazz'
        elif current_style and line.strip() == '],':
            # Found the end of the current style's list
            insertion_points[current_style] = i
            current_style = None

    print("Found insertion points:")
    for style, line_num in insertion_points.items():
        lick_count = len(licks_by_style.get(style, []))
        print(f"  {style}: line {line_num} ({lick_count} licks to add)")

    # Insert licks in reverse order (from bottom to top) to maintain line numbers
    for style in reversed(list(insertion_points.keys())):
        if style not in licks_by_style or not licks_by_style[style]:
            continue

        insert_line = insertion_points[style]
        lick_texts = licks_by_style[style]

        # Format each lick for insertion
        formatted_licks = []
        for lick_text in lick_texts:
            # Indent the lick properly (16 spaces for dict inside list)
            lick_lines = lick_text.strip().split('\n')
            formatted = ['                ' + line for line in lick_lines]
            formatted_licks.append('\n'.join(formatted) + ',\n')

        # Insert all licks for this style
        insert_text = ''.join(formatted_licks)
        lines.insert(insert_line, insert_text)

    # Write back to file
    with open('src/recommender.py', 'w') as f:
        f.writelines(lines)

    print("\n✅ Integration complete!")

    # Count total licks by style
    total_added = sum(len(licks) for licks in licks_by_style.values())
    print(f"\nTotal licks added: {total_added}")
    for style, licks in licks_by_style.items():
        print(f"  - {style}: {len(licks)} licks")


if __name__ == '__main__':
    print("=" * 80)
    print(" LICK INTEGRATION SCRIPT")
    print("=" * 80)
    print()

    print("Parsing licks from NEW_ADVANCED_LICKS.md...")
    licks_by_style = parse_licks_from_markdown()

    print("\nParsing complete. Licks found:")
    for style, licks in licks_by_style.items():
        print(f"  - {style}: {len(licks)} licks")

    print("\nIntegrating into src/recommender.py...")
    integrate_licks_into_recommender(licks_by_style)

    print("\n" + "=" * 80)
    print("Next steps:")
    print("  1. Verify src/recommender.py syntax")
    print("  2. Run test_lick_quality.py to verify improvement")
    print("  3. Commit and push changes")
    print("=" * 80)
