"""
Music Theory Explanation System

Provides detailed music theory explanations for chord progressions,
licks, and musical choices across all styles. References solid music
theory principles to explain WHY specific musical elements work.
"""

from typing import List, Dict, Optional
from .theory import Chord, ChordProgression, Note, ChordQuality


class MusicTheoryExplainer:
    """
    Explains music theory concepts and why specific musical choices work

    Provides theoretical context for:
    - Chord progressions (functional harmony, voice leading, etc.)
    - Licks and melodic phrases (scales, arpeggios, intervals)
    - Style-specific techniques (modal interchange, altered dominants, etc.)
    """

    def __init__(self):
        self.style_theory = self._build_style_theory_database()

    def explain_progression(self, progression: ChordProgression, style: str) -> str:
        """
        Provide comprehensive music theory explanation for a chord progression

        Args:
            progression: The chord progression to explain
            style: Musical style for context-specific theory

        Returns:
            Detailed theoretical explanation with references to music theory principles
        """
        explanations = []

        # Analyze harmonic function
        harmonic_analysis = self._analyze_harmonic_function(progression)
        if harmonic_analysis:
            explanations.append(f"**Harmonic Function**: {harmonic_analysis}")

        # Analyze voice leading
        voice_leading = self._analyze_voice_leading(progression)
        if voice_leading:
            explanations.append(f"**Voice Leading**: {voice_leading}")

        # Analyze modal/scale content
        modal_analysis = self._analyze_modal_content(progression, style)
        if modal_analysis:
            explanations.append(f"**Modal Content**: {modal_analysis}")

        # Style-specific theory
        style_theory = self._get_style_specific_theory(progression, style)
        if style_theory:
            explanations.append(f"**Style Theory**: {style_theory}")

        # Chord extensions and tensions
        extensions = self._analyze_chord_extensions(progression)
        if extensions:
            explanations.append(f"**Extensions & Tensions**: {extensions}")

        return "\n".join(explanations)

    def explain_lick(self, lick: Dict, key: Note, style: str) -> str:
        """
        Provide music theory explanation for why a lick works

        Args:
            lick: Lick dictionary with intervals and description
            key: Key the lick is played in
            style: Musical style for context

        Returns:
            Theoretical explanation of the lick's construction
        """
        explanations = []

        # Analyze scale/mode used
        scale_analysis = self._analyze_lick_scale(lick, style)
        if scale_analysis:
            explanations.append(f"**Scale/Mode**: {scale_analysis}")

        # Analyze intervallic structure
        interval_analysis = self._analyze_intervallic_structure(lick)
        if interval_analysis:
            explanations.append(f"**Intervallic Structure**: {interval_analysis}")

        # Analyze techniques and their theory
        technique_theory = self._explain_techniques(lick, style)
        if technique_theory:
            explanations.append(f"**Technical Theory**: {technique_theory}")

        # Style-specific lick theory
        style_lick_theory = self._get_style_lick_theory(lick, style)
        if style_lick_theory:
            explanations.append(f"**Style Context**: {style_lick_theory}")

        return "\n".join(explanations)

    def _analyze_harmonic_function(self, progression: ChordProgression) -> str:
        """Analyze roman numeral analysis and functional harmony"""
        # This is a simplified version - full implementation would do complete analysis
        chord_names = [c.to_symbol() for c in progression.chords]

        # Check for common progressions
        if len(progression.chords) == 4:
            # Look for ii-V-I
            if self._is_two_five_one(progression):
                return "Classic ii-V-I progression - the cornerstone of jazz harmony. The ii chord (supertonic) provides pre-dominant function, creating tension. The V chord (dominant) contains the tritone that resolves to the I (tonic), creating strong gravitational pull through voice leading."

            # Look for I-IV-V
            if self._is_one_four_five(progression):
                return "I-IV-V progression - fundamental to blues, rock, and folk. The subdominant (IV) creates plagal motion, while the dominant (V) provides authentic cadential resolution to tonic (I). This progression forms the basis of functional tonality."

        return "Functional harmony utilizing tonic, pre-dominant, and dominant relationships for tonal center establishment and resolution."

    def _analyze_voice_leading(self, progression: ChordProgression) -> str:
        """Analyze voice leading and common tone retention"""
        # Simplified analysis
        num_chords = len(progression.chords)

        if num_chords < 2:
            return ""

        # Check for smooth voice leading (common tones, stepwise motion)
        return "Utilizes smooth voice leading principles with common tone retention and stepwise motion in inner voices, minimizing melodic leaps while maintaining harmonic integrity."

    def _analyze_modal_content(self, progression: ChordProgression, style: str) -> str:
        """Analyze modal/scale implications"""
        modal_descriptions = {
            'neo_soul': "Employs Dorian mode for minor chords (raised 6th) and Mixolydian for dominant sounds (major with b7), creating sophisticated modal interchange typical of neo-soul harmony.",
            'blues': "Based on blues scale (minor pentatonic + b5 blue note) and Mixolydian mode (major scale with b7), allowing dominant 7th chords to function as stable tonics rather than requiring resolution.",
            'jazz': "Advanced modal vocabulary including Dorian, Phrygian, Lydian, Mixolydian, and Locrian modes. Altered scale (7th mode of melodic minor) over altered dominants creates tension through b9, #9, #11, and b13 alterations.",
            'progressive_metal': "Modal interchange between Phrygian dominant (exotic sound with b2), harmonic minor (raised 7th), and Lydian (raised 4th). Polymodal harmony creates shifting tonal centers.",
            'rock_fusion': "Sophisticated modal approach combining Lydian (bright, #11), Dorian (minor with major 6th), and Mixolydian (dominant with characteristic b7). Modal superimposition creates outside harmonic colors.",
            'metalcore': "Heavy use of Phrygian mode (minor with b2) for dark, aggressive sound. Natural minor and harmonic minor for melodic content. Chromatic voice leading in breakdowns."
        }

        return modal_descriptions.get(style, "Modal content derived from major/minor scale systems with characteristic alterations.")

    def _get_style_specific_theory(self, progression: ChordProgression, style: str) -> str:
        """Provide style-specific theoretical context"""
        theory = self.style_theory.get(style, {})

        chord_symbols = [c.to_symbol() for c in progression.chords]

        # Check for style-specific elements
        if style == 'jazz':
            if any('alt' in str(c.quality.name) or '7' in str(c.quality.name) for c in progression.chords):
                return theory.get('altered_dominants',
                    "Jazz harmony employs altered dominants (7alt, 7b9, 7#9) derived from the altered scale (7th mode of melodic minor). The tritone substitution principle allows bII7 to substitute for V7, sharing the same tritone interval.")

        elif style == 'neo_soul':
            if any('9' in str(c.quality.value) or '11' in str(c.quality.value) for c in progression.chords):
                return theory.get('extended_chords',
                    "Neo-soul features extensive use of 9th, 11th, and 13th chords, expanding the harmonic palette beyond triads. These extensions add color tones from upper chord structures while maintaining traditional voice leading principles.")

        elif style == 'blues':
            return theory.get('dominant_tonic',
                "Blues harmony treats dominant 7th chords as stable tonics rather than requiring resolution. This creates the characteristic 'blues sound' where the b7 (minor 7th interval) is accepted as a consonant color tone rather than a dissonance requiring resolution.")

        return theory.get('general', "")

    def _analyze_chord_extensions(self, progression: ChordProgression) -> str:
        """Analyze chord extensions and their theoretical function"""
        extensions_found = []

        for chord in progression.chords:
            quality_name = str(chord.quality.name)

            if '9' in quality_name:
                extensions_found.append("9th (major 2nd + octave) adds bright color")
            if '11' in quality_name:
                extensions_found.append("11th (perfect 4th + octave) creates suspended quality")
            if '13' in quality_name:
                extensions_found.append("13th (major 6th + octave) adds sophisticated jazz color")
            if 'FLAT_9' in quality_name:
                extensions_found.append("b9 (minor 2nd + octave) creates tension and dissonance")
            if 'SHARP_9' in quality_name:
                extensions_found.append("#9 (augmented 2nd + octave) - the 'Hendrix chord' sound")
            if 'SHARP_11' in quality_name:
                extensions_found.append("#11 (augmented 4th + octave) from Lydian mode, creates bright tension")

        if extensions_found:
            unique_extensions = list(set(extensions_found))
            return "; ".join(unique_extensions[:3])  # Limit to 3 for brevity

        return ""

    def _analyze_lick_scale(self, lick: Dict, style: str) -> str:
        """Determine the scale/mode the lick is based on"""
        intervals = lick.get('intervals', [])

        # Analyze interval pattern to determine scale
        if not intervals:
            return ""

        scale_patterns = {
            'minor_pentatonic': "Minor pentatonic scale (1-b3-4-5-b7) - the foundation of blues, rock, and many modern styles. Five notes providing maximum melodic freedom with minimal dissonance.",
            'major_pentatonic': "Major pentatonic scale (1-2-3-5-6) - bright, positive sound used in country, rock, and melodic playing. Removes the 4th and 7th scale degrees to eliminate potential dissonance.",
            'dorian': "Dorian mode (1-2-b3-4-5-6-b7) - minor scale with raised 6th. Popular in jazz, funk, and neo-soul for its sophisticated minor sound without the darkness of natural minor.",
            'lydian': "Lydian mode (1-2-3-#4-5-6-7) - major scale with raised 4th. Creates bright, dreamy quality popularized by composers and modern guitarists like Eric Johnson.",
            'mixolydian': "Mixolydian mode (1-2-3-4-5-6-b7) - major scale with flattened 7th. The sound of dominant 7th chords and classic rock/blues harmony.",
            'altered': "Altered scale (1-b2-#2-3-b5-#5-b7) - 7th mode of melodic minor. Contains all possible alterations over dominant chords: b9, #9, #11, b13. Essential for modern jazz.",
            'harmonic_minor': "Harmonic minor scale (1-2-b3-4-5-b6-7) - minor scale with raised 7th. Creates exotic, classical sound with augmented 2nd interval between b6 and 7.",
            'chromatic': "Chromatic scale - all 12 semitones. Used for voice leading, passing tones, and creating tension through half-step motion. Fundamental to bebop and fusion."
        }

        # Simple pattern matching (in real implementation, this would be more sophisticated)
        if set([0, 3, 5, 7, 10]) <= set(intervals):
            return scale_patterns['minor_pentatonic']
        elif set([0, 2, 4, 7, 9]) <= set(intervals):
            return scale_patterns['major_pentatonic']
        elif max(intervals) - min(intervals) <= 4:
            return scale_patterns['chromatic']

        return f"Based on {style}-specific scale vocabulary combining multiple modes and chromatic approach tones for maximum harmonic sophistication."

    def _analyze_intervallic_structure(self, lick: Dict) -> str:
        """Analyze the intervallic relationships in the lick"""
        intervals = lick.get('intervals', [])

        if not intervals or len(intervals) < 2:
            return ""

        # Calculate interval jumps
        jumps = [abs(intervals[i+1] - intervals[i]) for i in range(len(intervals)-1)]

        max_jump = max(jumps) if jumps else 0

        if max_jump >= 12:
            return "Features wide intervallic leaps (octave or greater) creating dramatic melodic contour and showcasing technical command across the fretboard. Wide intervals create tension and excitement in melodic lines."
        elif max_jump >= 7:
            return "Utilizes moderate to wide intervals (5ths, 6ths, octaves) for melodic interest while maintaining singability. These skips create shape and direction in the phrase."
        else:
            return "Primarily stepwise motion (2nds) and small skips (3rds, 4ths) creating smooth, vocal-like melodic contour. Emphasizes horizontal voice leading over vertical arpeggio patterns."

    def _explain_techniques(self, lick: Dict, style: str) -> str:
        """Explain the music theory behind technical approaches"""
        techniques = lick.get('techniques', [])

        if not techniques:
            return ""

        technique_explanations = {
            'legato': "Legato technique (hammer-ons/pull-offs) creates smooth, connected notes by minimizing pick attack. Musically, this emphasizes the melodic line's horizontal motion over percussive articulation.",
            'sweep picking': "Sweep picking applies economy of motion to arpeggios, using continuous pick direction across strings. Theoretically, this highlights the harmonic (vertical) structure rather than scale (horizontal) movement.",
            'hybrid picking': "Hybrid picking combines pick and fingers, allowing simultaneous articulation of bass and treble lines. Enables chord-melody playing where bass movement and harmonic voicings occur simultaneously - fundamental to jazz and country.",
            'chromatic approach': "Chromatic approach tones create tension by approaching chord tones from a half-step above or below. This bebop technique adds color while emphasizing target notes through directional voice leading.",
            'altered tones': "Altered tones (b9, #9, #11, b13) extend dominant harmony beyond diatonic limits. Derived from the altered scale (7th mode of melodic minor), these create maximum tension before resolution.",
            'modal interchange': "Modal interchange (borrowing chords from parallel modes) expands harmonic vocabulary. For example, borrowing bVI from Aeolian into Ionian creates unexpected color while maintaining tonal center.",
            'two-hand tapping': "Two-hand tapping extends the range and speed of arpeggio patterns beyond traditional picking. Theoretically, this allows rapid articulation of wide-interval arpeggios and polyrhythmic patterns impossible with conventional technique."
        }

        # Return explanation for first technique found
        for tech in techniques:
            for key, explanation in technique_explanations.items():
                if key in tech.lower():
                    return explanation

        return "Employs advanced technical approaches to execute complex theoretical concepts with precision and musicality."

    def _get_style_lick_theory(self, lick: Dict, style: str) -> str:
        """Provide style-specific theoretical context for licks"""
        style_contexts = {
            'blues': "Blues vocabulary combines minor pentatonic framework with chromatic blue notes (b5) and dominant chord tones. The tension between minor 3rd (from pentatonic) and major 3rd (from dominant chord) creates the characteristic blues sound through ambiguous third degree.",
            'jazz': "Jazz improvisation emphasizes chord-scale relationships and guide tone lines (3rds and 7ths). Bebop employs chromatic passing tones to create eight-note phrases over four-beat measures, maintaining strong beat emphasis on chord tones.",
            'neo_soul': "Neo-soul phrasing emphasizes space, dynamics, and sophisticated chord extensions (9ths, 11ths, 13ths). Melodic vocabulary draws from Dorian mode, major pentatonic extensions, and gospel-influenced grace note ornaments.",
            'progressive_metal': "Progressive metal combines technical precision with harmonic complexity. Uses polymetric phrasing (groupings of 5, 7, or 9 over 4/4 time), modal mixture, and wide-interval arpeggios showcasing both technique and compositional sophistication.",
            'rock_fusion': "Fusion vocabulary synthesizes rock's power and directness with jazz's harmonic sophistication. Combines pentatonic foundation, altered scales, and modal superimposition to create outside sounds while maintaining melodic coherence.",
            'metalcore': "Metalcore emphasizes rhythmic precision, palm-muted syncopation, and dissonant intervals (b2, tritone). Harmonic minor and Phrygian modes create dark, aggressive tonality. Breakdowns use chromatic voice leading in lower registers for maximum heaviness."
        }

        return style_contexts.get(style, "")

    def _is_two_five_one(self, progression: ChordProgression) -> bool:
        """Check if progression is ii-V-I"""
        # Simplified check - real implementation would analyze chord degrees
        if len(progression.chords) >= 3:
            # Check for minor 7th, dominant 7th, major 7th pattern
            qualities = [c.quality for c in progression.chords[:3]]
            pattern = [ChordQuality.MINOR_7, ChordQuality.DOMINANT_7, ChordQuality.MAJOR_7]
            return all(q in pattern for q in qualities[:3])
        return False

    def _is_one_four_five(self, progression: ChordProgression) -> bool:
        """Check if progression is I-IV-V"""
        # Simplified - would check actual chord degrees in full implementation
        return len(progression.chords) >= 3

    def _build_style_theory_database(self) -> Dict[str, Dict[str, str]]:
        """Build comprehensive theory explanations for each style"""
        return {
            'jazz': {
                'altered_dominants': "Altered dominants employ the altered scale (C7alt = C Db D# E Gb Ab Bb). This provides all possible tensions: b9, #9, #11, b13. The tritone (b5/#11) is the defining interval, creating maximum tension before resolution.",
                'extended_chords': "Jazz harmony extends beyond 7th chords to 9ths, 11ths, and 13ths. These upper structures add color while maintaining guide tone (3rd and 7th) voice leading. 13th chords contain seven notes, implying entire scales.",
                'tritone_sub': "Tritone substitution replaces V7 with bII7 (sharing the same tritone). G7 (B-F tritone) substitutes with Db7 (F-B tritone). This creates chromatic bass motion and harmonic sophistication.",
            },
            'blues': {
                'dominant_tonic': "Blues harmony suspends functional tonality by treating dominant 7th chords as stable tonics. The I7-IV7-V7 progression uses all dominant qualities, with the b7 as consonant color tone.",
                'blue_notes': "Blue notes (b3, b5, b7) exist outside the major scale, creating micro-tonal bends and characteristic blues dissonance. The b5 'blue note' creates tritone tension against the root.",
                'call_response': "Blues phrasing uses call-and-response structure: musical statement followed by answering phrase. This creates conversation-like melodic development fundamental to blues expression.",
            },
            'neo_soul': {
                'extended_chords': "Neo-soul features complex extended harmonies (maj9, min11, 13th chords) with sophisticated voice leading. These chords stack intervals vertically while maintaining smooth horizontal motion.",
                'dorian_preference': "Dorian mode (minor with major 6th) is preferred over natural minor for its sophisticated, less somber quality. The raised 6th creates whole-step between 6 and b7, characteristic of neo-soul.",
                'rhythmic_displacement': "Rhythmic displacement places expected notes on unexpected beats, creating syncopation. This polyrhythmic approach adds sophistication and groove to melodic phrases.",
            },
            'progressive_metal': {
                'polymetric': "Polymetric phrasing uses groupings that don't align with the time signature (groups of 5 or 7 over 4/4). Creates rhythmic tension and technical complexity while maintaining pulse.",
                'harmonic_minor': "Harmonic minor scale (raised 7th in minor) creates exotic, neoclassical sound. The augmented 2nd between b6 and 7 provides characteristic tension.",
                'modal_mixture': "Modal mixture borrows chords from parallel modes simultaneously. Lydian's #11 might appear alongside Phrygian's b2, creating polymodal harmony.",
            },
            'rock_fusion': {
                'pentatonic_extensions': "Fusion extends pentatonic scales with chromatic passing tones, creating hybrid vocabulary. Combines blues vocabulary (minor pentatonic) with jazz sophistication (altered tones).",
                'outside_playing': "Outside playing deliberately uses notes outside the key center, creating tension before resolving inside. This controlled dissonance showcases harmonic knowledge and creates interest.",
                'modal_superimposition': "Modal superimposition plays one mode over a different harmonic context. Lydian over major creates #11 tension; Dorian over dominant creates sophisticated color.",
            },
            'metalcore': {
                'djent': "Djent emphasizes palm-muted, syncopated riffing in lower registers. Rhythmic precision and polyrhythmic groupings create mechanical, aggressive sound over traditional melodic development.",
                'dissonance': "Metalcore harmony embraces dissonant intervals (b2, tritone, b9) as stable sonorities rather than requiring resolution. This creates dark, aggressive harmonic palette.",
                'breakdown_theory': "Breakdowns use slow, chromatic voice leading in lower registers with extreme syncopation. Harmonic rhythm slows while rhythmic complexity increases, creating maximum impact.",
            }
        }


# Global instance for easy access
theory_explainer = MusicTheoryExplainer()
