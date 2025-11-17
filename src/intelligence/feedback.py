"""Feedback Collection and Model Improvement System"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class UserFeedback:
    """User feedback on a suggestion or generation"""
    feedback_id: str
    user_id: str
    timestamp: datetime
    item_type: str  # 'chord', 'progression', 'melody', 'lick'
    item_data: Dict
    rating: int  # 1-5 stars
    comments: Optional[str] = None
    was_used: bool = False  # Did user actually use the suggestion?


class FeedbackSystem:
    """Collects and analyzes user feedback for model improvement"""

    def __init__(self):
        self.feedback_log = []

    def record_feedback(
        self,
        user_id: str,
        item_type: str,
        item_data: Dict,
        rating: int,
        comments: Optional[str] = None,
        was_used: bool = False
    ) -> str:
        """Record user feedback"""
        import uuid
        feedback_id = str(uuid.uuid4())[:8]

        feedback = UserFeedback(
            feedback_id=feedback_id,
            user_id=user_id,
            timestamp=datetime.now(),
            item_type=item_type,
            item_data=item_data,
            rating=rating,
            comments=comments,
            was_used=was_used
        )

        self.feedback_log.append(feedback)
        return feedback_id

    def get_feedback_summary(self) -> Dict:
        """Get summary of collected feedback"""
        if not self.feedback_log:
            return {'total': 0}

        ratings = [f.rating for f in self.feedback_log]
        by_type = {}

        for f in self.feedback_log:
            if f.item_type not in by_type:
                by_type[f.item_type] = {'count': 0, 'avg_rating': 0, 'used_count': 0}
            by_type[f.item_type]['count'] += 1
            by_type[f.item_type]['avg_rating'] += f.rating
            if f.was_used:
                by_type[f.item_type]['used_count'] += 1

        # Calculate averages
        for item_type in by_type:
            count = by_type[item_type]['count']
            by_type[item_type]['avg_rating'] /= count
            by_type[item_type]['usage_rate'] = by_type[item_type]['used_count'] / count

        return {
            'total': len(self.feedback_log),
            'avg_rating': sum(ratings) / len(ratings),
            'by_type': by_type,
            'high_rated': len([r for r in ratings if r >= 4]),
            'low_rated': len([r for r in ratings if r <= 2])
        }


class ModelImprover:
    """Uses feedback to improve model suggestions"""

    def __init__(self, feedback_system: FeedbackSystem):
        self.feedback_system = feedback_system
        self.improvement_log = []

    def analyze_feedback_patterns(self) -> List[str]:
        """Analyze feedback to identify improvement opportunities"""
        recommendations = []
        summary = self.feedback_system.get_feedback_summary()

        if not summary.get('by_type'):
            return ["Collect more feedback to generate recommendations"]

        for item_type, stats in summary['by_type'].items():
            if stats['avg_rating'] < 3.0:
                recommendations.append(
                    f"Low ratings for {item_type} ({stats['avg_rating']:.1f}/5) - review generation algorithm"
                )

            if stats.get('usage_rate', 0) < 0.3:
                recommendations.append(
                    f"Low usage rate for {item_type} ({stats['usage_rate']*100:.0f}%) - suggestions may not be practical"
                )

        return recommendations

    def get_high_quality_examples(self, item_type: str, min_rating: int = 4) -> List[Dict]:
        """Get highly-rated examples for fine-tuning"""
        high_quality = [
            f.item_data for f in self.feedback_system.feedback_log
            if f.item_type == item_type and f.rating >= min_rating and f.was_used
        ]

        return high_quality
