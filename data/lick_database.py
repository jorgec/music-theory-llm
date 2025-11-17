"""
Blues and Rock Guitar Lick Database (1960s-1980s)

Curated collection of iconic licks from legendary blues and rock guitarists.
Each lick includes attribution, style markers, and technical details.
"""

import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.theory import Pitch
from src.intelligence.lick_generator import MelodicLick, LickDatabase


class BluesRockLickDatabase(LickDatabase):
    """Extended lick database with authentic blues and rock licks"""

    def __init__(self):
        super().__init__()
        self.licks = []  # Clear default licks
        self._initialize_blues_licks_60s_80s()
        self._initialize_rock_licks_60s_80s()

    def _initialize_blues_licks_60s_80s(self):
        """Initialize authentic blues guitar licks from the golden era"""

        # ============ BB KING STYLE ============

        # BB King signature "butterfly" vibrato lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('G4'),
                Pitch.from_string('Bb4'),  # Bend to B
                Pitch.from_string('Bb4'),  # Release
                Pitch.from_string('G4'),
                Pitch.from_string('F4'),
                Pitch.from_string('G4')
            ],
            name="BB King Butterfly",
            style="blues",
            difficulty=3,
            description="BB King's signature string bend with vibrato on Bb, released to resolve",
            tags=['blues', 'bb-king', 'string-bend', 'vibrato', 'minor-pentatonic'],
            works_over=['G7', 'C7', 'blues']
        ))

        # BB King box position lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('D5'),
                Pitch.from_string('C5'),
                Pitch.from_string('Bb4'),
                Pitch.from_string('G4'),
                Pitch.from_string('Bb4'),
                Pitch.from_string('C5'),
                Pitch.from_string('D5')
            ],
            name="BB King Box Run",
            style="blues",
            difficulty=2,
            description="Classic BB King descending and ascending run in the blues box",
            tags=['blues', 'bb-king', 'box-position', 'minor-pentatonic'],
            works_over=['G7', 'Gm', 'blues']
        ))

        # ============ ALBERT KING STYLE ============

        # Albert King signature bend (upside-down guitar)
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('C4'),
                Pitch.from_string('Eb4'),  # Pre-bend
                Pitch.from_string('D4'),   # Release half-step
                Pitch.from_string('C4'),
                Pitch.from_string('Bb3'),
                Pitch.from_string('G3')
            ],
            name="Albert King Signature Bend",
            style="blues",
            difficulty=4,
            description="Albert King's signature pre-bend and release, powerful and vocal-like",
            tags=['blues', 'albert-king', 'pre-bend', 'release', 'powerful'],
            works_over=['C7', 'blues']
        ))

        # Albert King triplet feel lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('G3'),
                Pitch.from_string('Bb3'),
                Pitch.from_string('C4'),
                Pitch.from_string('Eb4'),
                Pitch.from_string('D4'),
                Pitch.from_string('C4'),
                Pitch.from_string('Bb3'),
                Pitch.from_string('G3')
            ],
            name="Albert King Triplet Run",
            style="blues",
            difficulty=3,
            description="Driving triplet feel run through the minor pentatonic scale",
            tags=['blues', 'albert-king', 'triplets', 'driving', 'minor-pentatonic'],
            works_over=['G7', 'Gm7', 'blues']
        ))

        # ============ MUDDY WATERS / CHICAGO BLUES ============

        # Chicago blues turnaround lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('G4'),
                Pitch.from_string('F4'),
                Pitch.from_string('D4'),
                Pitch.from_string('C4'),
                Pitch.from_string('Bb3'),
                Pitch.from_string('G3')
            ],
            name="Chicago Blues Turnaround",
            style="blues",
            difficulty=2,
            description="Classic Chicago blues turnaround lick, works at end of 12-bar blues",
            tags=['blues', 'chicago', 'turnaround', 'muddy-waters'],
            works_over=['G7', 'blues', 'turnaround']
        ))

        # Slide guitar influenced lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('D4'),
                Pitch.from_string('Eb4'),  # Slide
                Pitch.from_string('F4'),   # Slide
                Pitch.from_string('F#4'),  # Slide
                Pitch.from_string('G4'),
                Pitch.from_string('Bb4'),
                Pitch.from_string('G4')
            ],
            name="Slide Blues Lick",
            style="blues",
            difficulty=3,
            description="Slide guitar-influenced chromatic approach to target notes",
            tags=['blues', 'slide', 'chromatic', 'chicago'],
            works_over=['G7', 'C7', 'blues']
        ))

        # ============ JOHN LEE HOOKER STYLE ============

        # Boogie bass line lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('E2'),
                Pitch.from_string('G2'),
                Pitch.from_string('A2'),
                Pitch.from_string('Bb2'),
                Pitch.from_string('B2'),
                Pitch.from_string('Bb2'),
                Pitch.from_string('A2'),
                Pitch.from_string('G2')
            ],
            name="Boogie Bass Line",
            style="blues",
            difficulty=2,
            description="John Lee Hooker-style boogie bass line with chromatic passing tones",
            tags=['blues', 'boogie', 'john-lee-hooker', 'bass-line', 'chromatic'],
            works_over=['E7', 'A7', 'blues', 'boogie']
        ))

        # ============ T-BONE WALKER STYLE ============

        # Jump blues lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('G4'),
                Pitch.from_string('Bb4'),
                Pitch.from_string('D5'),
                Pitch.from_string('F5'),
                Pitch.from_string('D5'),
                Pitch.from_string('Bb4'),
                Pitch.from_string('G4'),
                Pitch.from_string('F4')
            ],
            name="Jump Blues Arpeggio",
            style="blues",
            difficulty=3,
            description="T-Bone Walker-style jump blues arpeggio, upbeat and swinging",
            tags=['blues', 'jump-blues', 't-bone-walker', 'arpeggio', 'swing'],
            works_over=['G7', 'Gm7', 'blues']
        ))

    def _initialize_rock_licks_60s_80s(self):
        """Initialize authentic rock guitar licks from legendary players"""

        # ============ JIMI HENDRIX ============

        # Hendrix double-stop bend lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('E4'),
                Pitch.from_string('G4'),   # Double stop
                Pitch.from_string('A4'),   # Bend both
                Pitch.from_string('G4'),
                Pitch.from_string('E4'),
                Pitch.from_string('D4'),
                Pitch.from_string('E4')
            ],
            name="Hendrix Double-Stop Bend",
            style="rock",
            difficulty=4,
            description="Jimi Hendrix signature double-stop bend, bluesy and psychedelic",
            tags=['rock', 'hendrix', 'double-stop', 'bend', 'psychedelic', 'blues-rock'],
            works_over=['E7', 'Em', 'A7']
        ))

        # Hendrix octave jump lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('E3'),
                Pitch.from_string('E4'),   # Octave jump
                Pitch.from_string('G4'),
                Pitch.from_string('A4'),
                Pitch.from_string('E4'),
                Pitch.from_string('E3')
            ],
            name="Hendrix Octave Jump",
            style="rock",
            difficulty=3,
            description="Hendrix-style octave jumps with pentatonic fill",
            tags=['rock', 'hendrix', 'octave', 'pentatonic', 'powerful'],
            works_over=['E7', 'Em', 'E']
        ))

        # "Red House" style lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('D4'),
                Pitch.from_string('C4'),
                Pitch.from_string('A3'),
                Pitch.from_string('G3'),
                Pitch.from_string('A3'),
                Pitch.from_string('C4'),
                Pitch.from_string('D4'),
                Pitch.from_string('E4')
            ],
            name="Red House Blues Lick",
            style="rock",
            difficulty=3,
            description="From Hendrix's 'Red House', slow blues with expressive bends",
            tags=['rock', 'hendrix', 'red-house', 'slow-blues', 'expressive'],
            works_over=['A7', 'D7', 'blues']
        ))

        # ============ ERIC CLAPTON ============

        # "Layla" style lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('C5'),
                Pitch.from_string('D5'),
                Pitch.from_string('E5'),
                Pitch.from_string('G5'),
                Pitch.from_string('E5'),
                Pitch.from_string('D5'),
                Pitch.from_string('C5'),
                Pitch.from_string('A4')
            ],
            name="Clapton Layla-Style Run",
            style="rock",
            difficulty=3,
            description="Eric Clapton ascending/descending run in minor pentatonic",
            tags=['rock', 'clapton', 'layla', 'pentatonic', 'fast-run'],
            works_over=['Am', 'C', 'Dm']
        ))

        # Cream-era blues-rock lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('E4'),
                Pitch.from_string('G4'),
                Pitch.from_string('A4'),
                Pitch.from_string('C5'),
                Pitch.from_string('A4'),
                Pitch.from_string('G4'),
                Pitch.from_string('E4')
            ],
            name="Cream Blues-Rock Lick",
            style="rock",
            difficulty=3,
            description="Cream-era Clapton blues-rock pentatonic lick",
            tags=['rock', 'clapton', 'cream', 'blues-rock', 'pentatonic'],
            works_over=['E7', 'A7', 'blues']
        ))

        # ============ JIMMY PAGE / LED ZEPPELIN ============

        # "Whole Lotta Love" style riff lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('E3'),
                Pitch.from_string('E3'),
                Pitch.from_string('G3'),
                Pitch.from_string('E3'),
                Pitch.from_string('E3'),
                Pitch.from_string('A3'),
                Pitch.from_string('Ab3'),
                Pitch.from_string('E3')
            ],
            name="Whole Lotta Love Riff",
            style="rock",
            difficulty=2,
            description="Jimmy Page's iconic heavy riff with chromatic approach",
            tags=['rock', 'led-zeppelin', 'jimmy-page', 'riff', 'heavy', 'chromatic'],
            works_over=['E7', 'E5', 'blues']
        ))

        # "Stairway to Heaven" solo lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('A4'),
                Pitch.from_string('C5'),
                Pitch.from_string('D5'),
                Pitch.from_string('E5'),
                Pitch.from_string('F5'),
                Pitch.from_string('E5'),
                Pitch.from_string('D5'),
                Pitch.from_string('C5')
            ],
            name="Stairway Solo Lick",
            style="rock",
            difficulty=4,
            description="From 'Stairway to Heaven' solo, melodic and soaring",
            tags=['rock', 'led-zeppelin', 'jimmy-page', 'stairway', 'melodic', 'solo'],
            works_over=['Am', 'C', 'D']
        ))

        # ============ CARLOS SANTANA ============

        # Santana signature sustained bend
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('D4'),
                Pitch.from_string('F4'),   # Bend to F#
                Pitch.from_string('F4'),   # Sustain
                Pitch.from_string('F4'),   # Vibrato
                Pitch.from_string('D4'),
                Pitch.from_string('C4'),
                Pitch.from_string('A3')
            ],
            name="Santana Sustained Bend",
            style="rock",
            difficulty=3,
            description="Carlos Santana's vocal-like sustained bend with wide vibrato",
            tags=['rock', 'santana', 'sustained-bend', 'vibrato', 'vocal', 'latin-rock'],
            works_over=['Dm', 'Am', 'C']
        ))

        # Latin rock phrase
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('A3'),
                Pitch.from_string('C4'),
                Pitch.from_string('D4'),
                Pitch.from_string('E4'),
                Pitch.from_string('F4'),
                Pitch.from_string('E4'),
                Pitch.from_string('D4'),
                Pitch.from_string('C4'),
                Pitch.from_string('A3')
            ],
            name="Santana Latin Rock Phrase",
            style="rock",
            difficulty=3,
            description="Santana-style Latin rock phrase with Dorian flavor",
            tags=['rock', 'santana', 'latin-rock', 'dorian', 'melodic'],
            works_over=['Am', 'Am7', 'Dm']
        ))

        # ============ DAVID GILMOUR / PINK FLOYD ============

        # "Comfortably Numb" style bend
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('D5'),
                Pitch.from_string('E5'),   # Full-step bend
                Pitch.from_string('E5'),   # Sustain with vibrato
                Pitch.from_string('D5'),
                Pitch.from_string('B4'),
                Pitch.from_string('D5')
            ],
            name="Gilmour Soaring Bend",
            style="rock",
            difficulty=3,
            description="David Gilmour's signature soaring bend with perfect vibrato",
            tags=['rock', 'pink-floyd', 'gilmour', 'bend', 'vibrato', 'melodic', 'emotional'],
            works_over=['Bm', 'D', 'A']
        ))

        # Atmospheric pentatonic phrase
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('B4'),
                Pitch.from_string('D5'),
                Pitch.from_string('E5'),
                Pitch.from_string('F#5'),
                Pitch.from_string('E5'),
                Pitch.from_string('D5'),
                Pitch.from_string('B4'),
                Pitch.from_string('A4')
            ],
            name="Gilmour Atmospheric Phrase",
            style="rock",
            difficulty=3,
            description="Atmospheric, spacious pentatonic phrase with feeling",
            tags=['rock', 'pink-floyd', 'gilmour', 'atmospheric', 'spacious', 'pentatonic'],
            works_over=['Bm', 'Em', 'A']
        ))

        # ============ JEFF BECK ============

        # Beck whammy bar technique
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('G4'),
                Pitch.from_string('Bb4'),
                Pitch.from_string('A4'),   # Whammy dive
                Pitch.from_string('Bb4'),  # Return
                Pitch.from_string('G4'),
                Pitch.from_string('F4')
            ],
            name="Beck Whammy Bar Lick",
            style="rock",
            difficulty=4,
            description="Jeff Beck's expressive whammy bar technique",
            tags=['rock', 'jeff-beck', 'whammy-bar', 'expressive', 'technical'],
            works_over=['G7', 'Gm', 'C']
        ))

        # ============ EDDIE VAN HALEN (late 70s) ============

        # Tapping lick (simplified)
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('E4'),
                Pitch.from_string('A4'),   # Tap
                Pitch.from_string('E4'),
                Pitch.from_string('A4'),   # Tap
                Pitch.from_string('E4'),
                Pitch.from_string('G4'),
                Pitch.from_string('E4')
            ],
            name="Van Halen Tapping Pattern",
            style="rock",
            difficulty=5,
            description="Eddie Van Halen's revolutionary two-hand tapping technique",
            tags=['rock', 'van-halen', 'tapping', 'technical', 'virtuoso', '80s'],
            works_over=['Am', 'E', 'A']
        ))

        # Fast pentatonic run
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('A3'),
                Pitch.from_string('C4'),
                Pitch.from_string('D4'),
                Pitch.from_string('E4'),
                Pitch.from_string('G4'),
                Pitch.from_string('A4'),
                Pitch.from_string('C5'),
                Pitch.from_string('D5'),
                Pitch.from_string('E5')
            ],
            name="Van Halen Fast Run",
            style="rock",
            difficulty=4,
            description="Blazing fast pentatonic run, Eddie Van Halen style",
            tags=['rock', 'van-halen', 'fast', 'pentatonic', 'virtuoso', 'shred'],
            works_over=['Am', 'C', 'F']
        ))

        # ============ STEVIE RAY VAUGHAN (early 80s) ============

        # SRV Texas blues lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('E3'),
                Pitch.from_string('G3'),
                Pitch.from_string('A3'),
                Pitch.from_string('Bb3'),
                Pitch.from_string('B3'),
                Pitch.from_string('A3'),
                Pitch.from_string('G3'),
                Pitch.from_string('E3')
            ],
            name="SRV Texas Blues Lick",
            style="blues",
            difficulty=3,
            description="Stevie Ray Vaughan's Texas blues with aggressive attack",
            tags=['blues', 'srv', 'texas', 'aggressive', 'powerful', '80s'],
            works_over=['E7', 'A7', 'blues']
        ))

        # SRV chord embellishment lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('E4'),
                Pitch.from_string('G#4'),
                Pitch.from_string('B4'),
                Pitch.from_string('C#5'),
                Pitch.from_string('B4'),
                Pitch.from_string('G#4'),
                Pitch.from_string('E4')
            ],
            name="SRV Chord Embellishment",
            style="blues",
            difficulty=3,
            description="SRV's signature chord tone embellishments",
            tags=['blues', 'srv', 'chord-tones', 'embellishment', 'sophisticated'],
            works_over=['E', 'E7', 'Emaj7']
        ))

        # ============ ANGUS YOUNG / AC/DC ============

        # AC/DC pentatonic rock lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('A3'),
                Pitch.from_string('C4'),
                Pitch.from_string('D4'),
                Pitch.from_string('E4'),
                Pitch.from_string('D4'),
                Pitch.from_string('C4'),
                Pitch.from_string('A3'),
                Pitch.from_string('G3')
            ],
            name="AC/DC Power Lick",
            style="rock",
            difficulty=2,
            description="Angus Young's straightforward, powerful pentatonic lick",
            tags=['rock', 'ac-dc', 'angus-young', 'pentatonic', 'straightforward', 'power'],
            works_over=['A', 'A7', 'D', 'E']
        ))

        # ============ DUANE ALLMAN ============

        # Allman Brothers slide lick
        self.licks.append(MelodicLick(
            pitches=[
                Pitch.from_string('E4'),
                Pitch.from_string('G4'),   # Slide
                Pitch.from_string('A4'),
                Pitch.from_string('B4'),   # Slide
                Pitch.from_string('D5'),
                Pitch.from_string('B4'),
                Pitch.from_string('A4'),
                Pitch.from_string('G4')
            ],
            name="Allman Brothers Slide Lick",
            style="rock",
            difficulty=4,
            description="Duane Allman's southern rock slide guitar lick",
            tags=['rock', 'allman-brothers', 'duane-allman', 'slide', 'southern-rock', 'bottleneck'],
            works_over=['E', 'A', 'B', 'blues']
        ))

    def get_licks_by_guitarist(self, guitarist: str) -> List[MelodicLick]:
        """Get all licks associated with a specific guitarist"""
        guitarist_tags = guitarist.lower().replace(' ', '-')
        return [
            lick for lick in self.licks
            if guitarist_tags in [tag.lower() for tag in lick.tags]
        ]

    def get_licks_by_era(self, decade: str) -> List[MelodicLick]:
        """Get licks from a specific era (60s, 70s, 80s)"""
        era_tags = {
            '60s': ['hendrix', 'clapton', 'cream', 'bb-king', 't-bone-walker'],
            '70s': ['led-zeppelin', 'jimmy-page', 'pink-floyd', 'gilmour', 'jeff-beck', 'santana'],
            '80s': ['van-halen', 'srv', '80s']
        }

        target_tags = era_tags.get(decade, [])
        return [
            lick for lick in self.licks
            if any(tag in [t.lower() for t in lick.tags] for tag in target_tags)
        ]

    def get_technique_licks(self, technique: str) -> List[MelodicLick]:
        """Get licks featuring a specific technique"""
        return [
            lick for lick in self.licks
            if technique.lower() in [tag.lower() for tag in lick.tags]
        ]

    def get_summary(self) -> str:
        """Get summary of the lick database"""
        total = len(self.licks)
        blues_count = len([l for l in self.licks if l.style == 'blues'])
        rock_count = len([l for l in self.licks if l.style == 'rock'])

        guitarists = set()
        for lick in self.licks:
            for tag in lick.tags:
                if any(artist in tag for artist in [
                    'bb-king', 'albert-king', 'hendrix', 'clapton',
                    'jimmy-page', 'santana', 'gilmour', 'jeff-beck',
                    'van-halen', 'srv', 'angus-young', 'duane-allman'
                ]):
                    guitarists.add(tag)

        summary = f"""
Blues & Rock Guitar Lick Database (1960s-1980s)
================================================
Total Licks: {total}
  Blues: {blues_count}
  Rock: {rock_count}

Featured Guitarists: {len(guitarists)}
{', '.join(sorted(guitarists))}

Difficulty Range: 1-5
Techniques: bends, vibrato, slides, double-stops, tapping, whammy bar

Usage:
  db = BluesRockLickDatabase()
  hendrix_licks = db.get_licks_by_guitarist("Hendrix")
  bend_licks = db.get_technique_licks("bend")
  sixties_licks = db.get_licks_by_era("60s")
"""
        return summary


def export_licks_to_json(output_file: str = "data/licks.json"):
    """Export lick database to JSON for training"""
    import json

    db = BluesRockLickDatabase()

    licks_data = []
    for lick in db.licks:
        lick_dict = {
            'name': lick.name,
            'style': lick.style,
            'difficulty': lick.difficulty,
            'description': lick.description,
            'tags': lick.tags,
            'works_over': lick.works_over,
            'pitches': [str(p) for p in lick.pitches],
            'intervals': [
                lick.pitches[i+1].midi_number - lick.pitches[i].midi_number
                for i in range(len(lick.pitches) - 1)
            ]
        }
        licks_data.append(lick_dict)

    with open(output_file, 'w') as f:
        json.dump(licks_data, f, indent=2)

    print(f"Exported {len(licks_data)} licks to {output_file}")


if __name__ == '__main__':
    # Demonstrate the database
    db = BluesRockLickDatabase()
    print(db.get_summary())

    print("\n" + "=" * 60)
    print("EXAMPLE LICKS BY GUITARIST")
    print("=" * 60)

    # Show some examples
    guitarists = ['hendrix', 'bb-king', 'clapton', 'jimmy-page', 'srv']

    for guitarist in guitarists:
        licks = db.get_licks_by_guitarist(guitarist)
        if licks:
            print(f"\n{guitarist.upper()} ({len(licks)} licks):")
            for lick in licks[:2]:  # Show first 2
                print(f"  • {lick.name}")
                print(f"    {lick.description}")
                print(f"    Notes: {' → '.join(str(p) for p in lick.pitches)}")

    # Export to JSON
    print("\n" + "=" * 60)
    export_licks_to_json()
