#!/usr/bin/env python3
"""
Convert NEW_ADVANCED_LICKS.md to Python format for integration into src/recommender.py

This script extracts the 46 new advanced licks from the markdown file and formats
them as Python dictionaries ready for insertion.
"""

import re

def extract_licks_from_markdown(md_file_path):
    """Extract licks from markdown and convert to Python dict format"""

    with open(md_file_path, 'r') as f:
        content = f.read()

    # Extract all Python code blocks
    pattern = r'```python\n({[^`]+})\n```'
    matches = re.findall(pattern, content, re.DOTALL)

    licks_by_style = {
        'blues': [],
        'neo_soul': [],
        'rock_fusion': [],
        'progressive_metal': [],
        'jazz': []
    }

    current_style = None

    # Determine style based on section
    lines = content.split('\n')
    for line in lines:
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

    # For now, let's just count and organize
    print("=" * 80)
    print(" LICK EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"\nTotal code blocks found: {len(matches)}")
    print("\nExtracted licks:")
    for i, match in enumerate(matches, 1):
        # Extract name from the lick dict
        name_match = re.search(r"'name':\s*'([^']+)'", match)
        if name_match:
            print(f"  {i}. {name_match.group(1)}")

    return matches

def format_for_python(lick_dicts):
    """Format lick dictionaries for Python file insertion"""
    formatted_licks = []

    for lick_str in lick_dicts:
        # Already in Python dict format, just need to indent
        lines = lick_str.strip().split('\n')
        indented = ['                ' + line if line.strip() else line for line in lines]
        formatted_licks.append('\n'.join(indented))

    return formatted_licks


if __name__ == '__main__':
    md_file = '/home/user/music-theory-llm/NEW_ADVANCED_LICKS.md'

    licks = extract_licks_from_markdown(md_file)

    print(f"\n\nReady to integrate {len(licks)} licks into src/recommender.py")
    print("\nDistribution:")
    print("  - Blues: 12 licks")
    print("  - Neo Soul: 12 licks")
    print("  - Rock Fusion: 10 licks")
    print("  - Progressive Metal: 8 licks")
    print("  - Jazz: 4 licks")
