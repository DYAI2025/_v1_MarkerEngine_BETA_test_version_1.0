"""
MarkerEngine Real Analyzer - Mit echten Markern
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
    """Echter Analyzer mit den richtigen Markern"""
    
    def __init__(self, markers_path: str = None):
        """
        Initialisiert den Analyzer mit echten Markern
        
        Args:
            markers_path: Pfad zum markers/ Verzeichnis
        """
        if markers_path is None:
            # Finde den markers Ordner relativ zur aktuellen Datei
            base_path = Path(__file__).parent.parent.parent
            markers_path = base_path / "markers"
        
        self.markers_path = Path(markers_path)
        self.markers = {
            'atomic': {},
            'semantic': {},
            'cluster': {},
            'meta': {}
        }
        
        # Lade alle Marker
        self._load_all_markers()
        
    def _load_all_markers(self):
        """Lädt alle Marker aus den YAML-Dateien"""
        
        # Lade Atomic Marker
        atomic_path = self.markers_path / "atomic"
        if atomic_path.exists():
            for yaml_file in atomic_path.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and 'marker_name' in data:
                            marker_id = f"A_{data['marker_name'].upper()}"
                            self.markers['atomic'][marker_id] = data
                            logger.info(f"Loaded atomic marker: {marker_id}")
                except Exception as e:
                    logger.error(f"Error loading {yaml_file}: {e}")
        
        # Lade Semantic Marker
        semantic_path = self.markers_path / "semantic"
        if semantic_path.exists():
            for yaml_file in semantic_path.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and 'marker_name' in data:
                            marker_id = f"S_{data['marker_name'].upper()}"
                            self.markers['semantic'][marker_id] = data
                            logger.info(f"Loaded semantic marker: {marker_id}")
                except Exception as e:
                    logger.error(f"Error loading {yaml_file}: {e}")
        
        # Lade Cluster Marker (falls vorhanden)
        cluster_path = self.markers_path / "cluster"
        if cluster_path.exists():
            for yaml_file in cluster_path.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and 'marker_name' in data:
                            marker_id = f"C_{data['marker_name'].upper()}"
                            self.markers['cluster'][marker_id] = data
                except Exception as e:
                    logger.error(f"Error loading {yaml_file}: {e}")
        
        # Lade Meta Marker
        meta_path = self.markers_path / "meta_marker"
        if meta_path.exists():
            for yaml_file in meta_path.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and 'marker_name' in data:
                            marker_id = f"MM_{data['marker_name'].upper()}"
                            self.markers['meta'][marker_id] = data
                except Exception as e:
                    logger.error(f"Error loading {yaml_file}: {e}")
        
        print(f"✅ Geladen: {len(self.markers['atomic'])} Atomic, "
              f"{len(self.markers['semantic'])} Semantic, "
              f"{len(self.markers['cluster'])} Cluster, "
              f"{len(self.markers['meta'])} Meta Marker")
    
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
        
        # 1. Atomic Marker Detection
        for marker_id, marker_data in self.markers['atomic'].items():
            hits = self._detect_atomic_marker(text, marker_data)
            if hits:
                results['atomic_hits'].extend(hits)
        
        # 2. Semantic Marker Detection (basierend auf Atomic Hits)
        # TODO: Implementiere composed_of Logik
        
        # 3. Statistiken berechnen
        results['statistics'] = {
            'total_atomic_hits': len(results['atomic_hits']),
            'unique_atomic_markers': len(set(h.marker_id for h in results['atomic_hits'])),
            'high_risk_markers': self._count_high_risk_markers(results['atomic_hits'])
        }
        
        # 4. Risk Score berechnen
        results['risk_score'] = self._calculate_risk_score(results)
        
        return results
    
    def _detect_atomic_marker(self, text: str, marker_data: Dict) -> List[MarkerResult]:
        """Erkennt Atomic Marker im Text"""
        hits = []
        
        # Hole die Beispiele aus dem Marker
        examples = marker_data.get('beispiele', [])
        if not examples:
            examples = marker_data.get('examples', [])
        
        # Suche nach jedem Beispiel im Text
        for example in examples:
            if isinstance(example, str):
                # Bereinige das Beispiel
                pattern = example.strip().strip('"').strip('-').strip()
                
                # Suche im Text (case-insensitive)
                if pattern.lower() in text.lower():
                    # Finde die genaue Position
                    match_pos = text.lower().find(pattern.lower())
                    context = text[max(0, match_pos-50):min(len(text), match_pos+50)]
                    
                    hit = MarkerResult(
                        marker_id=marker_data.get('marker_name', 'UNKNOWN'),
                        marker_name=marker_data.get('beschreibung', '')[:50],
                        level='atomic',
                        matches=[pattern],
                        confidence=0.9,
                        position=match_pos,
                        context=context
                    )
                    hits.append(hit)
        
        return hits
    
    def _count_high_risk_markers(self, hits: List[MarkerResult]) -> int:
        """Zählt High-Risk Marker"""
        high_risk_keywords = [
            'SCAM', 'FRAUD', 'MANIPULATION', 'GASLIGHTING', 
            'CRISIS', 'MONEY', 'BLAME', 'GUILT'
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
            score += min(atomic_hits * 0.1, 3.0)
        
        # High-Risk Marker erhöhen den Score
        high_risk = results['statistics'].get('high_risk_markers', 0)
        score += high_risk * 0.5
        
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
    # Test mit einer Beispiel-Datei
    test_text = """
    Du legst alles auf die Goldwaage, deswegen knallt's.
    Lass uns auf WhatsApp wechseln, diese App ist unpersönlich.
    Ich brauche dringend Geld für eine Operation.
    Du bildest dir das nur ein, ich habe das nie gesagt.
    """
    
    analyzer = RealMarkerAnalyzer()
    results = analyzer.analyze_text(test_text)
    
    print("\n🔍 Analyse-Ergebnisse:")
    print(f"Atomic Hits: {len(results['atomic_hits'])}")
    print(f"Risk Score: {results['risk_score']:.1f}/10")
    
    if results['atomic_hits']:
        print("\n📍 Gefundene Marker:")
        for hit in results['atomic_hits'][:5]:  # Erste 5
            print(f"  - {hit.marker_id}: '{hit.matches[0][:50]}...'")
