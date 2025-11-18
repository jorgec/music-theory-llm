#!/usr/bin/env python3
"""
Music Theory LLM - Master Run Script

Interactive menu for accessing all features:
- Lick recommendations
- Chord progression recommendations
- Tablature generation
- MIDI export
- MIDI analysis
- Audio analysis

Usage:
    python run.py
"""

import sys


MENU = """
================================================================================
 MUSIC THEORY LLM - MAIN MENU
================================================================================

RECOMMENDATIONS:
  1. Get lick recommendations
  2. Get chord progression recommendations

GENERATION:
  3. Generate tablature
  4. Export to MIDI

ANALYSIS:
  5. Analyze MIDI file
  6. Analyze audio file (WAV/MP3)

DEMOS:
  7. Run complete artist showcase
  8. Run MIDI I/O demo
  9. Run tablature demo

HELP:
  h. Show script usage examples
  q. Quit

================================================================================
"""

USAGE_EXAMPLES = """
================================================================================
 USAGE EXAMPLES
================================================================================

LICK RECOMMENDATIONS:
  python run_lick_recommender.py --style rock_fusion --key E --num 5
  python run_lick_recommender.py --style jazz --key C --show-tablature
  python run_lick_recommender.py --style blues --key A --export-midi

CHORD PROGRESSION RECOMMENDATIONS:
  python run_progression_recommender.py --style jazz --num 5
  python run_progression_recommender.py --style neo_soul --export-midi
  python run_progression_recommender.py --style blues --licks-for-progression

TABLATURE GENERATION:
  python run_tablature.py --style rock_fusion --key E
  python run_tablature.py --style jazz --key C --num 3
  python run_tablature.py --style blues --key A --save-to-file

MIDI EXPORT:
  python run_midi_export.py --lick --style rock_fusion --key E
  python run_midi_export.py --progression --style jazz --key C
  python run_midi_export.py --lick --style blues --key A --tempo 90

MIDI ANALYSIS:
  python run_midi_analyzer.py --file song.mid
  python run_midi_analyzer.py --file lick.mid --show-detailed
  python run_midi_analyzer.py --file progression.mid --save-report

AUDIO ANALYSIS:
  python run_audio_analyzer.py --file song.wav
  python run_audio_analyzer.py --file guitar_solo.mp3 --show-detailed
  python run_audio_analyzer.py --file track.wav --save-report

AVAILABLE STYLES:
  rock_fusion, neo_soul, blues, jazz, prog_metal, metalcore

AVAILABLE KEYS:
  C, C#, D, D#, E, F, F#, G, G#, A, A#, B (and flats: Db, Eb, Gb, Ab, Bb)

================================================================================
"""


def main():
    """Main interactive menu"""
    while True:
        print(MENU)
        choice = input("Enter your choice: ").strip().lower()

        if choice == '1':
            # Lick recommendations
            print("\n" + "=" * 80)
            print(" LICK RECOMMENDATIONS")
            print("=" * 80)
            style = input("Style (rock_fusion/neo_soul/blues/jazz/prog_metal/metalcore): ").strip()
            key = input("Key (C, D, E, F, G, A, B, C#, etc.): ").strip()
            num = input("Number of recommendations [5]: ").strip() or "5"

            cmd = f"python run_lick_recommender.py --style {style} --key {key} --num {num}"
            print(f"\nRunning: {cmd}\n")
            import subprocess
            subprocess.run(cmd, shell=True)

        elif choice == '2':
            # Chord progression recommendations
            print("\n" + "=" * 80)
            print(" CHORD PROGRESSION RECOMMENDATIONS")
            print("=" * 80)
            style = input("Style (rock_fusion/neo_soul/blues/jazz/prog_metal/metalcore): ").strip()
            num = input("Number of recommendations [5]: ").strip() or "5"

            cmd = f"python run_progression_recommender.py --style {style} --num {num}"
            print(f"\nRunning: {cmd}\n")
            import subprocess
            subprocess.run(cmd, shell=True)

        elif choice == '3':
            # Generate tablature
            print("\n" + "=" * 80)
            print(" TABLATURE GENERATION")
            print("=" * 80)
            style = input("Style (rock_fusion/neo_soul/blues/jazz/prog_metal/metalcore): ").strip()
            key = input("Key (C, D, E, F, G, A, B, C#, etc.): ").strip()
            num = input("Number of licks [1]: ").strip() or "1"

            cmd = f"python run_tablature.py --style {style} --key {key} --num {num}"
            print(f"\nRunning: {cmd}\n")
            import subprocess
            subprocess.run(cmd, shell=True)

        elif choice == '4':
            # Export to MIDI
            print("\n" + "=" * 80)
            print(" MIDI EXPORT")
            print("=" * 80)
            mode = input("Export (lick/progression): ").strip().lower()
            style = input("Style (rock_fusion/neo_soul/blues/jazz/prog_metal/metalcore): ").strip()

            if mode == 'lick':
                key = input("Key (C, D, E, F, G, A, B, C#, etc.): ").strip()
                cmd = f"python run_midi_export.py --lick --style {style} --key {key}"
            else:
                cmd = f"python run_midi_export.py --progression --style {style}"

            print(f"\nRunning: {cmd}\n")
            import subprocess
            subprocess.run(cmd, shell=True)

        elif choice == '5':
            # Analyze MIDI file
            print("\n" + "=" * 80)
            print(" MIDI FILE ANALYSIS")
            print("=" * 80)
            file_path = input("MIDI file path: ").strip()

            cmd = f"python run_midi_analyzer.py --file {file_path}"
            print(f"\nRunning: {cmd}\n")
            import subprocess
            subprocess.run(cmd, shell=True)

        elif choice == '6':
            # Analyze audio file
            print("\n" + "=" * 80)
            print(" AUDIO FILE ANALYSIS")
            print("=" * 80)
            file_path = input("Audio file path (WAV/MP3/FLAC): ").strip()

            cmd = f"python run_audio_analyzer.py --file {file_path}"
            print(f"\nRunning: {cmd}\n")
            import subprocess
            subprocess.run(cmd, shell=True)

        elif choice == '7':
            # Run complete artist showcase
            print("\nRunning complete artist showcase...\n")
            import subprocess
            subprocess.run("python demo_complete_artist_showcase.py", shell=True)

        elif choice == '8':
            # Run MIDI I/O demo
            print("\nRunning MIDI I/O demo...\n")
            import subprocess
            subprocess.run("python demo_midi_io.py", shell=True)

        elif choice == '9':
            # Run tablature demo
            print("\nRunning tablature demo...\n")
            import subprocess
            subprocess.run("python demo_tablature_generation.py", shell=True)

        elif choice == 'h':
            # Show usage examples
            print(USAGE_EXAMPLES)
            input("\nPress Enter to continue...")

        elif choice == 'q':
            # Quit
            print("\nGoodbye!")
            sys.exit(0)

        else:
            print(f"\n[ERROR] Invalid choice: {choice}")
            print("Please enter a number (1-9), 'h' for help, or 'q' to quit\n")
            input("Press Enter to continue...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)
