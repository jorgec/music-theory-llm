#!/usr/bin/env python3
"""
Lick Quality Analysis - Test for complexity, melodic content, and harmonic sophistication

Tests for:
- Overly simple licks (interval range, unique note count)
- Overly repetitive notes/licks (interval repetition, note diversity)
- Basic/beginner licks (complexity score)

Biases for:
- Complexity and mastery (interval variety, range, patterns)
- Melodic content (contour, direction changes)
- Functional harmony (chord tones, extensions, chromatic approach)
"""

import sys
from collections import Counter
from typing import Dict, List, Tuple

from src.recommender import LickRecommender


class LickQualityAnalyzer:
    """Analyze licks for complexity, melodic content, and harmonic sophistication"""

    def __init__(self):
        # Get licks from the recommender
        recommender = LickRecommender()
        self.all_licks = recommender.lick_database

    def analyze_interval_complexity(self, intervals: List[int]) -> Dict:
        """Analyze interval pattern complexity"""
        if not intervals:
            return {'score': 0, 'issues': ['Empty interval list']}

        unique_intervals = len(set(intervals))
        total_intervals = len(intervals)

        # Check for overly simple patterns
        issues = []

        # 1. Interval range (should be > 1 octave for complexity)
        interval_range = max(intervals) - min(intervals)
        if interval_range < 7:  # Less than a 5th
            issues.append(f"Very narrow range: {interval_range} semitones")
        elif interval_range < 12:  # Less than an octave
            issues.append(f"Narrow range: {interval_range} semitones")

        # 2. Unique interval ratio (should be > 0.5 for complexity)
        unique_ratio = unique_intervals / total_intervals
        if unique_ratio < 0.3:
            issues.append(f"Low interval diversity: {unique_ratio:.2%}")

        # 3. Check for excessive repetition
        interval_counts = Counter(intervals)
        most_common_interval, most_common_count = interval_counts.most_common(1)[0]
        repetition_ratio = most_common_count / total_intervals
        if repetition_ratio > 0.4:
            issues.append(f"Excessive repetition of interval {most_common_interval}: {repetition_ratio:.2%}")

        # 4. Check for static/pedal tone patterns
        if intervals.count(0) > len(intervals) * 0.3:
            issues.append(f"Too many repeated notes (0 interval): {intervals.count(0)}/{len(intervals)}")

        # 5. Interval variety (different interval types)
        interval_types = len(set(abs(i) for i in intervals if i != 0))
        if interval_types < 3:
            issues.append(f"Low interval variety: only {interval_types} different interval types")

        # Calculate complexity score (0-100)
        score = 0
        score += min(30, interval_range * 2)  # Range contribution (max 30)
        score += unique_ratio * 30  # Diversity contribution (max 30)
        score += min(20, interval_types * 4)  # Variety contribution (max 20)
        score += min(20, (1 - repetition_ratio) * 40)  # Anti-repetition (max 20)

        return {
            'score': score,
            'interval_range': interval_range,
            'unique_ratio': unique_ratio,
            'interval_types': interval_types,
            'repetition_ratio': repetition_ratio,
            'issues': issues
        }

    def analyze_melodic_content(self, intervals: List[int]) -> Dict:
        """Analyze melodic contour and direction changes"""
        if len(intervals) < 3:
            return {'score': 0, 'issues': ['Too short for melodic analysis']}

        issues = []

        # 1. Direction changes (good melodies have variety)
        direction_changes = 0
        prev_direction = 0
        for i in range(1, len(intervals)):
            curr_direction = 1 if intervals[i] > intervals[i-1] else -1 if intervals[i] < intervals[i-1] else 0
            if curr_direction != 0 and curr_direction != prev_direction and prev_direction != 0:
                direction_changes += 1
            prev_direction = curr_direction

        direction_change_ratio = direction_changes / (len(intervals) - 1)
        if direction_change_ratio < 0.2:
            issues.append(f"Monotonous melodic contour: only {direction_changes} direction changes")

        # 2. Stepwise vs leap ratio (good balance needed)
        steps = sum(1 for i in intervals if abs(i) <= 2 and i != 0)
        leaps = sum(1 for i in intervals if abs(i) > 2)

        if leaps == 0:
            issues.append("No intervallic leaps - purely stepwise motion")

        if steps == 0 and leaps > 0:
            issues.append("No stepwise motion - only leaps")

        # 3. Large interval jumps (indicates advanced playing)
        large_jumps = sum(1 for i in intervals if abs(i) >= 7)  # 5th or larger

        # 4. Chromatic vs diatonic
        chromatic_steps = sum(1 for i in intervals if abs(i) == 1)
        chromatic_ratio = chromatic_steps / len(intervals)

        # Calculate melodic score (0-100)
        score = 0
        score += min(40, direction_change_ratio * 100)  # Contour variety (max 40)
        score += min(30, large_jumps * 6)  # Large intervals (max 30)
        score += min(20, chromatic_ratio * 60)  # Chromaticism (max 20)
        score += 10 if steps > 0 and leaps > 0 else 0  # Balance bonus

        return {
            'score': score,
            'direction_changes': direction_changes,
            'direction_change_ratio': direction_change_ratio,
            'steps': steps,
            'leaps': leaps,
            'large_jumps': large_jumps,
            'chromatic_ratio': chromatic_ratio,
            'issues': issues
        }

    def analyze_harmonic_sophistication(self, intervals: List[int], name: str, description: str) -> Dict:
        """Analyze harmonic sophistication and chord tone usage"""
        issues = []

        # 1. Check for chord tones (3rds, 5ths, 7ths)
        chord_intervals = {0, 3, 4, 7, 10, 11}  # Root, m3, M3, 5th, m7, M7
        chord_tones = sum(1 for i in intervals if (i % 12) in chord_intervals)
        chord_tone_ratio = chord_tones / len(intervals) if intervals else 0

        # 2. Check for extensions (9ths, 11ths, 13ths)
        extensions = {2, 5, 9}  # 9th, 11th, 13th (mod 12)
        extension_notes = sum(1 for i in intervals if (i % 12) in extensions)

        # 3. Check for altered tones (b9, #9, #11, b13)
        altered = {1, 3, 6, 8}  # b9, #9, #11, b13
        altered_notes = sum(1 for i in intervals if (i % 12) in altered)

        # 4. Check for chromatic approach tones
        chromatic_approaches = sum(1 for i in range(1, len(intervals))
                                   if abs(intervals[i] - intervals[i-1]) == 1)

        # 5. Check description for harmonic keywords
        harmonic_keywords = [
            'arpegg', 'chord', 'extension', 'altered', 'chromatic',
            'voice leading', 'progression', 'changes', 'harmonic',
            '9th', '11th', '13th', 'diminished', 'augmented',
            'superimposed', 'outside', 'tension'
        ]
        has_harmonic_context = any(kw in description.lower() or kw in name.lower()
                                   for kw in harmonic_keywords)

        # Check for overly basic patterns
        if chord_tone_ratio > 0.9 and extension_notes == 0:
            issues.append("Only basic chord tones - no extensions or color tones")

        if chromatic_approaches == 0 and len(intervals) > 8:
            issues.append("No chromatic approach tones")

        if not has_harmonic_context:
            issues.append("Description lacks harmonic context")

        # Calculate harmonic sophistication score (0-100)
        score = 0
        score += min(30, chord_tone_ratio * 40)  # Chord tone foundation (max 30)
        score += extension_notes * 10  # Extensions (10 points each)
        score += altered_notes * 12  # Alterations (12 points each)
        score += min(20, chromatic_approaches * 3)  # Chromatic movement (max 20)
        score += 15 if has_harmonic_context else 0  # Context bonus

        return {
            'score': score,
            'chord_tone_ratio': chord_tone_ratio,
            'extension_notes': extension_notes,
            'altered_notes': altered_notes,
            'chromatic_approaches': chromatic_approaches,
            'has_harmonic_context': has_harmonic_context,
            'issues': issues
        }

    def analyze_lick(self, lick: Dict, style: str) -> Dict:
        """Complete analysis of a single lick"""
        intervals = lick['intervals']
        name = lick.get('name', 'Unknown')
        description = lick.get('description', '')

        interval_analysis = self.analyze_interval_complexity(intervals)
        melodic_analysis = self.analyze_melodic_content(intervals)
        harmonic_analysis = self.analyze_harmonic_sophistication(intervals, name, description)

        # Overall complexity score (weighted average)
        overall_score = (
            interval_analysis['score'] * 0.3 +
            melodic_analysis['score'] * 0.35 +
            harmonic_analysis['score'] * 0.35
        )

        # Determine if lick is acceptable
        all_issues = (
            interval_analysis['issues'] +
            melodic_analysis['issues'] +
            harmonic_analysis['issues']
        )

        # Classification
        if overall_score >= 70:
            classification = 'ADVANCED'
        elif overall_score >= 50:
            classification = 'INTERMEDIATE'
        else:
            classification = 'BASIC/BEGINNER'

        return {
            'name': name,
            'style': style,
            'artist': lick.get('artist', 'Unknown'),
            'length': len(intervals),
            'overall_score': overall_score,
            'classification': classification,
            'interval_analysis': interval_analysis,
            'melodic_analysis': melodic_analysis,
            'harmonic_analysis': harmonic_analysis,
            'issues': all_issues,
            'flagged': classification == 'BASIC/BEGINNER' or len(all_issues) >= 3
        }

    def run_full_analysis(self) -> Dict:
        """Analyze all licks across all styles"""
        results = {
            'total_licks': 0,
            'flagged_licks': [],
            'style_scores': {},
            'overall_stats': {
                'advanced': 0,
                'intermediate': 0,
                'basic': 0
            }
        }

        for style, licks in self.all_licks.items():
            style_results = []

            for lick in licks:
                analysis = self.analyze_lick(lick, style)
                style_results.append(analysis)
                results['total_licks'] += 1

                # Count classifications
                if analysis['classification'] == 'ADVANCED':
                    results['overall_stats']['advanced'] += 1
                elif analysis['classification'] == 'INTERMEDIATE':
                    results['overall_stats']['intermediate'] += 1
                else:
                    results['overall_stats']['basic'] += 1

                # Flag problematic licks
                if analysis['flagged']:
                    results['flagged_licks'].append(analysis)

            # Calculate style average
            avg_score = sum(r['overall_score'] for r in style_results) / len(style_results)
            results['style_scores'][style] = {
                'average_score': avg_score,
                'lick_count': len(style_results),
                'licks': style_results
            }

        return results


def print_separator(char='=', length=80):
    print(char * length)


def main():
    print_separator()
    print(" LICK QUALITY ANALYSIS - Complexity & Harmonic Sophistication Test")
    print_separator()
    print()

    analyzer = LickQualityAnalyzer()
    results = analyzer.run_full_analysis()

    # Overall statistics
    print("OVERALL STATISTICS:")
    print_separator('-')
    print(f"Total licks analyzed: {results['total_licks']}")
    print()

    print("Classification Distribution:")
    print(f"  ADVANCED:      {results['overall_stats']['advanced']:3d} "
          f"({results['overall_stats']['advanced']/results['total_licks']*100:.1f}%)")
    print(f"  INTERMEDIATE:  {results['overall_stats']['intermediate']:3d} "
          f"({results['overall_stats']['intermediate']/results['total_licks']*100:.1f}%)")
    print(f"  BASIC/BEGINNER: {results['overall_stats']['basic']:3d} "
          f"({results['overall_stats']['basic']/results['total_licks']*100:.1f}%)")
    print()

    # Style-by-style scores
    print("STYLE AVERAGE SCORES:")
    print_separator('-')
    for style, data in sorted(results['style_scores'].items(),
                             key=lambda x: x[1]['average_score'], reverse=True):
        print(f"{style:15s}: {data['average_score']:5.1f}/100 ({data['lick_count']} licks)")
    print()

    # Flagged licks
    if results['flagged_licks']:
        print(f"FLAGGED LICKS (Total: {len(results['flagged_licks'])}):")
        print_separator('-')
        print("These licks may be overly simple, repetitive, or lack harmonic sophistication")
        print()

        for lick in sorted(results['flagged_licks'], key=lambda x: x['overall_score']):
            print(f"[{lick['classification']}] {lick['name']}")
            print(f"  Artist: {lick['artist']}")
            print(f"  Style: {lick['style']}")
            print(f"  Overall Score: {lick['overall_score']:.1f}/100")
            print(f"  Length: {lick['length']} notes")
            print(f"  Scores: Interval={lick['interval_analysis']['score']:.1f}, "
                  f"Melodic={lick['melodic_analysis']['score']:.1f}, "
                  f"Harmonic={lick['harmonic_analysis']['score']:.1f}")

            if lick['issues']:
                print(f"  Issues:")
                for issue in lick['issues']:
                    print(f"    - {issue}")
            print()
    else:
        print("NO FLAGGED LICKS - All licks meet quality standards!")
        print()

    # Summary recommendations
    print_separator()
    print("SUMMARY & RECOMMENDATIONS:")
    print_separator('-')

    basic_count = results['overall_stats']['basic']
    advanced_count = results['overall_stats']['advanced']

    if basic_count == 0:
        print("[OK] No basic/beginner licks detected")
    else:
        print(f"[WARNING] {basic_count} basic/beginner licks detected")
        print("  Recommendation: Review and enhance flagged licks with:")
        print("  - More interval variety and wider range")
        print("  - Chromatic approach tones")
        print("  - Chord extensions (9ths, 11ths, 13ths)")
        print("  - More complex melodic contours")

    print()

    if advanced_count >= results['total_licks'] * 0.7:
        print(f"[EXCELLENT] {advanced_count/results['total_licks']*100:.1f}% of licks are ADVANCED")
    elif advanced_count >= results['total_licks'] * 0.5:
        print(f"[GOOD] {advanced_count/results['total_licks']*100:.1f}% of licks are ADVANCED")
    else:
        print(f"[NEEDS IMPROVEMENT] Only {advanced_count/results['total_licks']*100:.1f}% of licks are ADVANCED")
        print("  Recommendation: Add more sophisticated licks with:")
        print("  - Extended harmonies and altered tones")
        print("  - Wide interval leaps and angular melodies")
        print("  - Clear functional harmony context")

    print()
    print_separator()

    # Return exit code based on results
    if basic_count > results['total_licks'] * 0.1:  # More than 10% basic
        print("RESULT: FAILED - Too many basic/beginner licks")
        return 1
    elif advanced_count < results['total_licks'] * 0.5:  # Less than 50% advanced
        print("RESULT: WARNING - Could use more advanced licks")
        return 0
    else:
        print("RESULT: PASSED - Strong complexity and sophistication")
        return 0


if __name__ == '__main__':
    sys.exit(main())
