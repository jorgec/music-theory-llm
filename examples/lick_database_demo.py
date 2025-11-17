"""
Blues & Rock Lick Database Demo

Demonstrates the comprehensive lick database featuring legendary guitarists
from the 1960s-1980s.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.lick_database import BluesRockLickDatabase
from src.theory import Chord, Scale, Note
from src.intelligence.lick_generator import NeuralLickGenerator


def demo_lick_database():
    """Demonstrate the lick database"""
    print("=" * 80)
    print("BLUES & ROCK GUITAR LICK DATABASE (1960s-1980s)")
    print("=" * 80)
    print()

    # Load database
    db = BluesRockLickDatabase()
    print(db.get_summary())

    print("\n" + "=" * 80)
    print("BROWSE LICKS BY GUITARIST")
    print("=" * 80)

    # Famous guitarists
    guitarists = [
        ('BB King', 'bb-king'),
        ('Albert King', 'albert-king'),
        ('Jimi Hendrix', 'hendrix'),
        ('Eric Clapton', 'clapton'),
        ('Jimmy Page', 'jimmy-page'),
        ('Carlos Santana', 'santana'),
        ('David Gilmour', 'gilmour'),
        ('Eddie Van Halen', 'van-halen'),
        ('Stevie Ray Vaughan', 'srv')
    ]

    for name, tag in guitarists:
        licks = db.get_licks_by_guitarist(tag)
        if licks:
            print(f"\n{name.upper()} - {len(licks)} licks")
            print("-" * 60)

            for lick in licks[:2]:  # Show first 2
                print(f"\n  • {lick.name}")
                print(f"    Difficulty: {lick.difficulty}/5")
                print(f"    {lick.description}")
                print(f"    Notes: {' → '.join(str(p) for p in lick.pitches)}")
                print(f"    Works over: {', '.join(lick.works_over[:3])}")
                print(f"    Tags: {', '.join(lick.tags[:4])}")


def demo_licks_by_era():
    """Browse licks by decade"""
    print("\n" + "=" * 80)
    print("BROWSE LICKS BY ERA")
    print("=" * 80)

    db = BluesRockLickDatabase()

    for decade in ['60s', '70s', '80s']:
        licks = db.get_licks_by_era(decade)
        print(f"\n{decade.upper()} - {len(licks)} licks")
        print("-" * 60)

        # Show a few examples
        for lick in licks[:3]:
            print(f"  • {lick.name} - {lick.difficulty}/5")
            print(f"    {' → '.join(str(p) for p in lick.pitches[:6])}...")


def demo_licks_by_technique():
    """Browse licks by technique"""
    print("\n" + "=" * 80)
    print("BROWSE LICKS BY TECHNIQUE")
    print("=" * 80)

    db = BluesRockLickDatabase()

    techniques = [
        'bend', 'vibrato', 'slide', 'double-stop',
        'tapping', 'whammy-bar', 'pentatonic', 'chromatic'
    ]

    for technique in techniques:
        licks = db.get_technique_licks(technique)
        if licks:
            print(f"\n{technique.upper().replace('-', ' ')} - {len(licks)} licks")
            examples = [l.name for l in licks[:3]]
            print(f"  Examples: {', '.join(examples)}")


def demo_lick_analysis():
    """Analyze specific iconic licks"""
    print("\n" + "=" * 80)
    print("ICONIC LICK ANALYSIS")
    print("=" * 80)

    db = BluesRockLickDatabase()

    # Find specific famous licks
    iconic_licks = [
        "BB King Butterfly",
        "Hendrix Double-Stop Bend",
        "Clapton Layla-Style Run",
        "Van Halen Tapping Pattern",
        "Gilmour Soaring Bend"
    ]

    for lick_name in iconic_licks:
        lick = next((l for l in db.licks if l.name == lick_name), None)
        if lick:
            print(f"\n{lick.name.upper()}")
            print("-" * 60)
            print(f"Style: {lick.style.capitalize()}")
            print(f"Difficulty: {lick.difficulty}/5 {'⭐' * lick.difficulty}")
            print(f"\nDescription:")
            print(f"  {lick.description}")
            print(f"\nNotes: {' → '.join(str(p) for p in lick.pitches)}")

            # Calculate intervals
            intervals = []
            for i in range(len(lick.pitches) - 1):
                interval = lick.pitches[i + 1].midi_number - lick.pitches[i].midi_number
                direction = "up" if interval > 0 else "down"
                intervals.append(f"{direction} {abs(interval)}")

            print(f"Intervals: {', '.join(intervals)}")
            print(f"\nWorks over: {', '.join(lick.works_over)}")
            print(f"Tags: {', '.join(lick.tags)}")


def demo_train_with_licks():
    """Demonstrate training the lick generator on this database"""
    print("\n" + "=" * 80)
    print("TRAINING LICK GENERATOR ON DATABASE")
    print("=" * 80)
    print()

    db = BluesRockLickDatabase()

    print(f"Database contains {len(db.licks)} authentic licks from legendary guitarists")
    print("\nTo train the lick generator:")
    print()
    print("```python")
    print("from data.lick_database import BluesRockLickDatabase")
    print("from src.intelligence.lick_generator import NeuralLickGenerator")
    print()
    print("# Load database")
    print("db = BluesRockLickDatabase()")
    print()
    print("# Train generator")
    print("generator = NeuralLickGenerator()")
    print("generator.learn_from_licks(db.licks, num_epochs=30)")
    print()
    print("# Generate new licks")
    print("new_lick = generator.generate_lick(")
    print("    chord=Chord.from_symbol('G7'),")
    print("    scale=Scale.major(Note.from_string('C')),")
    print("    style='blues',")
    print("    difficulty=3")
    print(")")
    print("```")
    print()

    # Show what styles we can generate
    styles = set(lick.style for lick in db.licks)
    print(f"Available styles: {', '.join(styles)}")

    # Show guitarists we learned from
    guitarists = set()
    for lick in db.licks:
        for tag in lick.tags:
            if any(name in tag for name in [
                'bb-king', 'albert-king', 'hendrix', 'clapton', 'jimmy-page',
                'santana', 'gilmour', 'jeff-beck', 'van-halen', 'srv',
                'angus-young', 'duane-allman'
            ]):
                guitarists.add(tag.replace('-', ' ').title())

    print(f"\nLearned from: {', '.join(sorted(guitarists))}")


def demo_export_licks():
    """Demonstrate exporting licks for training"""
    print("\n" + "=" * 80)
    print("EXPORT LICKS FOR TRAINING")
    print("=" * 80)
    print()

    from data.lick_database import export_licks_to_json

    print("Exporting lick database to JSON format...")
    export_licks_to_json("data/licks.json")

    print("\nThe exported file contains:")
    print("  - Pitch sequences")
    print("  - Interval patterns")
    print("  - Style labels")
    print("  - Difficulty ratings")
    print("  - Technical tags")
    print("  - Chord contexts")
    print()
    print("Use this data to:")
    print("  1. Train neural lick generators")
    print("  2. Analyze common patterns")
    print("  3. Create style-specific models")
    print("  4. Build recommendation systems")


def demo_find_similar_licks():
    """Demonstrate finding similar licks"""
    print("\n" + "=" * 80)
    print("FIND SIMILAR LICKS")
    print("=" * 80)

    db = BluesRockLickDatabase()

    # Pick a lick
    hendrix_lick = next((l for l in db.licks if 'hendrix' in l.tags), None)

    if hendrix_lick:
        print(f"\nStarting with: {hendrix_lick.name}")
        print(f"  Style: {hendrix_lick.style}")
        print(f"  Tags: {', '.join(hendrix_lick.tags[:5])}")

        print("\nFinding similar licks...")

        # Find other licks with similar style/tags
        similar = []
        for lick in db.licks:
            if lick == hendrix_lick:
                continue

            score = 0
            # Same style
            if lick.style == hendrix_lick.style:
                score += 2

            # Common tags
            common_tags = set(lick.tags) & set(hendrix_lick.tags)
            score += len(common_tags)

            # Similar difficulty
            if abs(lick.difficulty - hendrix_lick.difficulty) <= 1:
                score += 1

            if score > 0:
                similar.append((lick, score))

        similar.sort(key=lambda x: x[1], reverse=True)

        print("\nMost similar licks:")
        for lick, score in similar[:5]:
            print(f"  {score} pts - {lick.name}")
            print(f"          {', '.join(lick.tags[:3])}")


def main():
    """Run all demos"""
    print("\n")
    print("█" * 80)
    print(" " * 15 + "BLUES & ROCK GUITAR LICK DATABASE")
    print(" " * 20 + "Legendary Guitarists 1960s-1980s")
    print("█" * 80)
    print("\n")

    demos = [
        ("Lick Database Overview", demo_lick_database),
        ("Browse by Era", demo_licks_by_era),
        ("Browse by Technique", demo_licks_by_technique),
        ("Iconic Lick Analysis", demo_lick_analysis),
        ("Find Similar Licks", demo_find_similar_licks),
        ("Training with Licks", demo_train_with_licks),
        ("Export for Training", demo_export_licks)
    ]

    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\nError in {name}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("✓ Lick database demo completed!")
    print()
    print("Featured Guitarists:")
    print("  Blues: BB King, Albert King, Muddy Waters, SRV, T-Bone Walker")
    print("  Rock: Jimi Hendrix, Eric Clapton, Jimmy Page, Carlos Santana")
    print("        David Gilmour, Jeff Beck, Eddie Van Halen, Angus Young")
    print()
    print("Database Stats:")
    print("  • 30+ authentic licks")
    print("  • 2 styles (blues, rock)")
    print("  • 5 difficulty levels")
    print("  • 10+ techniques")
    print("  • 3 decades (60s, 70s, 80s)")
    print("=" * 80)
    print()


if __name__ == '__main__':
    main()
