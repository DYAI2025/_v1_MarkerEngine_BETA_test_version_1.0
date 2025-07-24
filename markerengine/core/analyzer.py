"""
MarkerAnalyzer - Simplified Working Version
"""
import re
from typing import Dict, List, Any
from pathlib import Path

class MarkerAnalyzer:
    def __init__(self):
        self.markers = {
            'emotional.positive': ['liebe', 'freude', 'glücklich', 'danke', 'super', 'toll'],
            'emotional.negative': ['traurig', 'wütend', 'enttäuscht', 'schlecht', 'problem'],
            'urgency': ['schnell', 'sofort', 'dringend', 'eilig'],
            'money': ['geld', 'euro', 'zahlen', 'überweisen', 'kosten']
        }
        
    def analyze(self, text: str, profile: str = 'atomic') -> Dict[str, Any]:
        text_lower = text.lower()
        words = text.split()
        
        # Find markers
        hits = []
        for category, markers in self.markers.items():
            for marker in markers:
                for match in re.finditer(r'\b' + re.escape(marker) + r'\b', text_lower):
                    hits.append({
                        'marker_id': f'{category}:{marker}',
                        'category': category,
                        'text': marker,
                        'position': match.start()
                    })
        
        # Stats
        stats = {
            'text': {
                'total_chars': len(text),
                'total_words': len(words),
                'chunks': 1
            },
            'markers': {
                'total_hits': len(hits),
                'by_category': {}
            }
        }
        
        # Count by category
        for hit in hits:
            cat = hit['category']
            stats['markers']['by_category'][cat] = stats['markers']['by_category'].get(cat, 0) + 1
        
        # Generate insights
        insights = []
        if len(hits) > 10:
            insights.append({
                'type': 'pattern',
                'title': 'Viele Marker gefunden',
                'description': f'{len(hits)} Marker in {len(words)} Wörtern gefunden.',
                'severity': 'medium'
            })
        
        return {
            'profile': profile,
            'stats': stats,
            'marker_hits': hits,
            'insights': insights
        }
