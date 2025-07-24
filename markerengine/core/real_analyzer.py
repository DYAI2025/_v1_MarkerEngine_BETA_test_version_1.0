"""
MarkerEngine Real Analyzer - Mit Pattern Engine
Verwendet die tatsächlichen Marker aus dem markers/ Verzeichnis
"""
import os
import yaml
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Import Pattern Engine
try:
    from .pattern_engine import MarkerPatternEngine, PatternMatch
    PATTERN_ENGINE_AVAILABLE = True
except ImportError:
    PATTERN_ENGINE_AVAILABLE = False
    print("⚠️ Pattern Engine nicht verfügbar")

logger = logging.getLogger(__name__)

@dataclass
class MarkerResult:
    """Ergebnis eines Marker-Treffers"""
    marker_id: str
    marker_name: str
    level: str  # atomic, semantic, cluster, meta
    matches: List[str]
    confidence: float
    position: int
    context: str

class RealMarkerAnalyzer:
    """Echter Analyzer mit Pattern Engine"""
    
    def __init__(self, markers_path: str = None):
        """
        Initialisiert den Analyzer mit echten Markern
        
        Args:
            markers_path: Pfad zum markers/ Verzeichnis
        """
        if markers_path is None:
            base_path = Path(__file__).parent.parent.parent
            markers_path = base_path / "markers"
        
        self.markers_path = Path(markers_path)
        
        # Initialisiere Pattern Engine
        if PATTERN_ENGINE_AVAILABLE:
            self.pattern_engine = MarkerPatternEngine(markers_path)
            print("✅ Pattern Engine aktiviert!")
        else:
            print("⚠️ Fallback auf einfache Suche")
            self.markers = {'atomic': {}, 'semantic': {}, 'cluster': {}, 'meta': {}}
            self._load_all_markers()
    
    def _load_all_markers(self):
        """Lädt alle Marker aus den YAML-Dateien (Fallback)"""
        # Nur für Fallback wenn Pattern Engine nicht verfügbar
        atomic_path = self.markers_path / "atomic"
        if atomic_path.exists():
            for yaml_file in atomic_path.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and 'marker_name' in data:
                            marker_id = data['marker_name']
                            self.markers['atomic'][marker_id] = data
                except Exception as e:
                    logger.error(f"Error loading {yaml_file}: {e}")
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analysiert einen Text mit allen Markern
        
        Args:
            text: Der zu analysierende Text
            
        Returns:
            Analyse-Ergebnisse
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'text_length': len(text),
            'atomic_hits': [],
            'semantic_hits': [],
            'cluster_hits': [],
            'meta_hits': [],
            'statistics': {},
            'risk_score': 0.0
        }
        
        # Verwende Pattern Engine wenn verfügbar
        if PATTERN_ENGINE_AVAILABLE and hasattr(self, 'pattern_engine'):
            # Pattern-basierte Erkennung
            pattern_matches = self.pattern_engine.detect_patterns(text, 'atomic')
            
            # Konvertiere zu MarkerResults
            for match in pattern_matches:
                marker_result = MarkerResult(
                    marker_id=match.marker_id,
                    marker_name=match.marker_name,
                    level='atomic',
                    matches=[match.match_text],
                    confidence=match.confidence,
                    position=match.start_pos,
                    context=match.context
                )
                results['atomic_hits'].append(marker_result)
        else:
            # Fallback: Einfache Suche
            for marker_id, marker_data in self.markers['atomic'].items():
                hits = self._detect_atomic_marker_simple(text, marker_data)
                if hits:
                    results['atomic_hits'].extend(hits)
        
        # TODO: Semantic, Cluster und Meta Marker basierend auf Atomic Hits
        
        # Statistiken berechnen
        results['statistics'] = {
            'total_atomic_hits': len(results['atomic_hits']),
            'unique_atomic_markers': len(set(h.marker_id for h in results['atomic_hits'])),
            'high_risk_markers': self._count_high_risk_markers(results['atomic_hits'])
        }
        
        # Risk Score berechnen
        results['risk_score'] = self._calculate_risk_score(results)
        
        return results
    
    def _detect_atomic_marker_simple(self, text: str, marker_data: Dict) -> List[MarkerResult]:
        """Einfache Marker-Erkennung (Fallback)"""
        hits = []
        
        beispiele = marker_data.get('beispiele', []) or marker_data.get('examples', [])
        
        for beispiel in beispiele:
            if isinstance(beispiel, str):
                clean = beispiel.strip().strip('"').strip('-').strip()
                
                if clean.lower() in text.lower():
                    match_pos = text.lower().find(clean.lower())
                    context = text[max(0, match_pos-50):min(len(text), match_pos+50)]
                    
                    hit = MarkerResult(
                        marker_id=marker_data.get('marker_name', 'UNKNOWN'),
                        marker_name=marker_data.get('beschreibung', '')[:50],
                        level='atomic',
                        matches=[clean],
                        confidence=0.8,
                        position=match_pos,
                        context=context
                    )
                    hits.append(hit)
        
        return hits
    
    def _count_high_risk_markers(self, hits: List[MarkerResult]) -> int:
        """Zählt High-Risk Marker"""
        high_risk_keywords = [
            'SCAM', 'FRAUD', 'MANIPULATION', 'GASLIGHTING', 
            'CRISIS', 'MONEY', 'BLAME', 'GUILT', 'SHIFT',
            'PLATFORM_SWITCH', 'URGENCY', 'WEBCAM_EXCUSE'
        ]
        
        count = 0
        for hit in hits:
            if any(keyword in hit.marker_id.upper() for keyword in high_risk_keywords):
                count += 1
        return count
    
    def _calculate_risk_score(self, results: Dict) -> float:
        """Berechnet einen Risiko-Score basierend auf den Treffern"""
        score = 0.0
        
        # Basis-Score aus Anzahl der Treffer
        atomic_hits = len(results['atomic_hits'])
        if atomic_hits > 0:
            score += min(atomic_hits * 0.15, 4.0)
        
        # High-Risk Marker erhöhen den Score stark
        high_risk = results['statistics'].get('high_risk_markers', 0)
        score += high_risk * 0.8
        
        # Verschiedene Marker-Typen erhöhen Score
        unique_markers = results['statistics'].get('unique_atomic_markers', 0)
        if unique_markers > 5:
            score += 1.5
        elif unique_markers > 3:
            score += 0.8
        
        # Normalize auf 0-10
        return min(score, 10.0)

def analyze_whatsapp_chat(file_path: str) -> Dict[str, Any]:
    """
    Haupt-Funktion zur Analyse eines WhatsApp-Chats
    
    Args:
        file_path: Pfad zur WhatsApp .txt Datei
        
    Returns:
        Vollständige Analyse
    """
    analyzer = RealMarkerAnalyzer()
    
    # Lese die Datei
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Analysiere
    results = analyzer.analyze_text(content)
    
    # Füge Datei-Info hinzu
    results['file_info'] = {
        'name': os.path.basename(file_path),
        'size': os.path.getsize(file_path),
        'analyzed_at': datetime.now().isoformat()
    }
    
    return results

if __name__ == "__main__":
    # Test mit Beispielen
    test_texts = [
        "Du legst alles auf die Goldwaage, deswegen knallt's.",
        "Lass uns auf WhatsApp wechseln, diese App ist unpersönlich.",
        "Ich brauche dringend Geld für eine Operation.",
        "Du bildest dir das nur ein, ich habe das nie gesagt.",
        "Wenn du nicht immer so spät wärst, hätten wir das Problem nicht.",
        "Wegen dir haben wir Verspätung.",
        "Das ist alles deine Schuld!",
        "Hey, wie geht's dir heute?"  # Sollte keine Treffer haben
    ]
    
    analyzer = RealMarkerAnalyzer()
    
    print("\n🔍 Teste Real Analyzer mit Pattern Engine:")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Text: '{text}'")
        results = analyzer.analyze_text(text)
        
        if results['atomic_hits']:
            print(f"   ✅ {len(results['atomic_hits'])} Treffer:")
            for hit in results['atomic_hits']:
                print(f"      - {hit.marker_id}: '{hit.matches[0]}'")
                print(f"        Konfidenz: {hit.confidence:.1%}")
        else:
            print("   ❌ Keine Marker gefunden")
        
        print(f"   📊 Risk Score: {results['risk_score']:.1f}/10")
