"""
MarkerAnalyzer - Mit Kimi K2 Integration
"""
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import os

class MarkerAnalyzer:
    def __init__(self):
        self.markers = {
            'emotional.positive': ['liebe', 'freude', 'glücklich', 'danke', 'super', 'toll', 'wunderbar', 'schön'],
            'emotional.negative': ['traurig', 'wütend', 'enttäuscht', 'schlecht', 'problem', 'schwierig', 'leider'],
            'urgency': ['schnell', 'sofort', 'dringend', 'eilig', 'jetzt', 'gleich'],
            'money': ['geld', 'euro', 'zahlen', 'überweisen', 'kosten', 'preis', 'bezahlen', 'konto'],
            'trust': ['vertrauen', 'glaub mir', 'ehrlich', 'versprechen', 'geheim'],
            'manipulation': ['nur du', 'niemand sonst', 'letzte chance', 'einmalig', 'exklusiv']
        }
        
    def analyze(self, text: str, profile: str = 'atomic', use_ai: bool = True) -> Dict[str, Any]:
        text_lower = text.lower()
        words = text.split()
        
        # 1. Rule-based analysis
        hits = []
        for category, markers in self.markers.items():
            for marker in markers:
                for match in re.finditer(r'\b' + re.escape(marker) + r'\b', text_lower):
                    hits.append({
                        'marker_id': f'{category}:{marker}',
                        'category': category,
                        'text': marker,
                        'position': match.start(),
                        'context': text[max(0, match.start()-50):min(len(text), match.end()+50)]
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
        
        # Generate rule-based insights
        insights = []
        
        # High marker density
        if len(hits) > 10:
            insights.append({
                'type': 'pattern',
                'title': 'Hohe Marker-Dichte',
                'description': f'{len(hits)} Marker in {len(words)} Wörtern gefunden.',
                'severity': 'medium',
                'source': 'rules'
            })
            
        # Manipulation patterns
        manip_count = stats['markers']['by_category'].get('manipulation', 0)
        trust_count = stats['markers']['by_category'].get('trust', 0)
        if manip_count + trust_count > 3:
            insights.append({
                'type': 'warning',
                'title': 'Manipulationsmuster erkannt',
                'description': f'{manip_count + trust_count} Vertrauens- und Manipulationsmarker gefunden.',
                'severity': 'high',
                'source': 'rules'
            })
            
        # Money + urgency combo
        money_count = stats['markers']['by_category'].get('money', 0)
        urgency_count = stats['markers']['by_category'].get('urgency', 0)
        if money_count > 0 and urgency_count > 0:
            insights.append({
                'type': 'warning',
                'title': 'Geld + Dringlichkeit',
                'description': 'Kombination aus Geld-Themen und Zeitdruck kann auf Betrug hinweisen.',
                'severity': 'high',
                'source': 'rules'
            })
        
        result = {
            'profile': profile,
            'stats': stats,
            'marker_hits': hits,
            'insights': insights,
            'ai_analysis': None
        }
        
        # 2. AI analysis with Kimi K2 (if available)
        if use_ai and os.getenv('KIMI_API_KEY'):
            try:
                from ..kimi.client import analyze_with_kimi_sync
                
                # Prepare context from rule analysis
                context = f"Gefundene Marker: {len(hits)}, Hauptkategorien: {list(stats['markers']['by_category'].keys())}"
                
                # Get AI analysis
                ai_result = analyze_with_kimi_sync(text[:2000], os.getenv('KIMI_API_KEY'))
                
                if ai_result.get('ai_available'):
                    result['ai_analysis'] = ai_result.get('ai_analysis')
                    
                    # Add AI insights
                    if 'risk_indicators' in ai_result.get('ai_analysis', {}):
                        for risk in ai_result['ai_analysis']['risk_indicators']:
                            insights.append({
                                'type': 'ai_warning',
                                'title': f"KI: {risk.get('type', 'Risiko')}",
                                'description': risk.get('description', ''),
                                'severity': risk.get('severity', 'medium'),
                                'source': 'ai'
                            })
                            
            except Exception as e:
                print(f"AI analysis failed: {e}")
        
        return result
