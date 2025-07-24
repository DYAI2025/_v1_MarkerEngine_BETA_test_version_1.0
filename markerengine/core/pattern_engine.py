"""
MarkerEngine Pattern Detector - Richtige Pattern-Erkennung
"""
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class PatternMatch:
    """Repräsentiert einen Pattern-Match"""
    marker_id: str
    marker_name: str
    pattern: str
    match_text: str
    start_pos: int
    end_pos: int
    confidence: float
    context: str

class MarkerPatternEngine:
    """
    Echte Pattern-Matching Engine für die Marker
    Unterstützt verschiedene Matching-Strategien
    """
    
    def __init__(self, markers_path: str = None):
        """Initialisiert die Pattern Engine"""
        if markers_path is None:
            base_path = Path(__file__).parent.parent.parent
            markers_path = base_path / "markers"
        
        self.markers_path = Path(markers_path)
        self.compiled_patterns = {
            'atomic': {},
            'semantic': {},
            'cluster': {},
            'meta': {}
        }
        
        # Lade und kompiliere alle Patterns
        self._compile_all_patterns()
    
    def _compile_all_patterns(self):
        """Lädt und kompiliert alle Marker-Patterns"""
        
        # Atomic Markers
        atomic_path = self.markers_path / "atomic"
        if atomic_path.exists():
            for yaml_file in atomic_path.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data:
                            patterns = self._extract_patterns_from_marker(data)
                            if patterns:
                                marker_id = data.get('marker_name', yaml_file.stem)
                                self.compiled_patterns['atomic'][marker_id] = {
                                    'data': data,
                                    'patterns': patterns
                                }
                                logger.info(f"Compiled {len(patterns)} patterns for {marker_id}")
                except Exception as e:
                    logger.error(f"Error loading {yaml_file}: {e}")
        
        print(f"✅ Pattern Engine bereit: {len(self.compiled_patterns['atomic'])} Atomic Marker geladen")
    
    def _extract_patterns_from_marker(self, marker_data: Dict) -> List[re.Pattern]:
        """Extrahiert und kompiliert Patterns aus Marker-Daten"""
        patterns = []
        
        # 1. Versuche explizite Patterns
        if 'pattern' in marker_data and marker_data['pattern']:
            for pattern in marker_data['pattern']:
                try:
                    compiled = re.compile(pattern, re.IGNORECASE | re.UNICODE)
                    patterns.append(compiled)
                except:
                    pass
        
        # 2. Versuche atomic_pattern
        if 'atomic_pattern' in marker_data:
            try:
                compiled = re.compile(marker_data['atomic_pattern'], re.IGNORECASE | re.UNICODE)
                patterns.append(compiled)
            except:
                pass
        
        # 3. Generiere Patterns aus Beispielen
        beispiele = marker_data.get('beispiele', []) or marker_data.get('examples', [])
        if beispiele:
            # Erstelle Fuzzy-Patterns aus Beispielen
            for beispiel in beispiele[:10]:  # Erste 10 für Performance
                if isinstance(beispiel, str):
                    # Bereinige das Beispiel
                    clean = beispiel.strip().strip('"').strip("'").strip("-").strip()
                    
                    if len(clean) > 5:  # Mindestlänge
                        # Erstelle verschiedene Pattern-Varianten
                        
                        # 1. Exakter Match (case-insensitive)
                        pattern = re.escape(clean)
                        try:
                            patterns.append(re.compile(pattern, re.IGNORECASE))
                        except:
                            pass
                        
                        # 2. Fuzzy Match (wichtige Wörter)
                        # Extrahiere Schlüsselwörter
                        keywords = self._extract_keywords(clean)
                        if len(keywords) >= 2:
                            # Erstelle Pattern mit Wildcards zwischen Keywords
                            fuzzy_pattern = r'\b' + r'.*?'.join(re.escape(kw) for kw in keywords) + r'\b'
                            try:
                                patterns.append(re.compile(fuzzy_pattern, re.IGNORECASE))
                            except:
                                pass
        
        return patterns
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrahiert Schlüsselwörter aus einem Text"""
        # Entferne Füllwörter
        stopwords = {'der', 'die', 'das', 'und', 'oder', 'aber', 'mit', 'von', 'zu', 
                    'in', 'an', 'auf', 'für', 'ist', 'sind', 'hat', 'haben', 'werden',
                    'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr'}
        
        words = text.lower().split()
        keywords = []
        
        for word in words:
            # Bereinige Wort
            clean_word = re.sub(r'[^\w\säöüß]', '', word)
            if clean_word and len(clean_word) > 2 and clean_word not in stopwords:
                keywords.append(clean_word)
        
        return keywords
    
    def detect_patterns(self, text: str, level: str = 'atomic') -> List[PatternMatch]:
        """
        Erkennt Patterns im Text
        
        Args:
            text: Der zu analysierende Text
            level: Marker-Level (atomic, semantic, etc.)
            
        Returns:
            Liste von PatternMatch-Objekten
        """
        matches = []
        
        for marker_id, marker_info in self.compiled_patterns[level].items():
            patterns = marker_info['patterns']
            data = marker_info['data']
            
            for pattern in patterns:
                try:
                    # Finde alle Matches
                    for match in pattern.finditer(text):
                        # Extrahiere Kontext
                        start = max(0, match.start() - 50)
                        end = min(len(text), match.end() + 50)
                        context = text[start:end]
                        
                        # Berechne Konfidenz
                        confidence = self._calculate_confidence(match, pattern, text)
                        
                        pattern_match = PatternMatch(
                            marker_id=marker_id,
                            marker_name=data.get('beschreibung', '')[:100],
                            pattern=pattern.pattern,
                            match_text=match.group(0),
                            start_pos=match.start(),
                            end_pos=match.end(),
                            confidence=confidence,
                            context=context
                        )
                        
                        matches.append(pattern_match)
                        
                except Exception as e:
                    logger.debug(f"Pattern matching error for {marker_id}: {e}")
        
        # Dedupliziere überlappende Matches
        matches = self._deduplicate_matches(matches)
        
        return matches
    
    def _calculate_confidence(self, match: re.Match, pattern: re.Pattern, text: str) -> float:
        """Berechnet Konfidenz-Score für einen Match"""
        confidence = 0.8  # Basis-Konfidenz
        
        # Exakte Matches haben höhere Konfidenz
        if not any(meta in pattern.pattern for meta in ['.*', '.+', '\\b']):
            confidence = 0.95
        
        # Längere Matches sind vertrauenswürdiger
        match_length = len(match.group(0))
        if match_length > 20:
            confidence += 0.05
        elif match_length < 10:
            confidence -= 0.1
        
        # Wort-Grenzen erhöhen Konfidenz
        if match.start() == 0 or text[match.start()-1].isspace():
            confidence += 0.05
        if match.end() == len(text) or text[match.end()].isspace():
            confidence += 0.05
        
        return min(1.0, max(0.1, confidence))
    
    def _deduplicate_matches(self, matches: List[PatternMatch]) -> List[PatternMatch]:
        """Entfernt überlappende Matches, behält die mit höchster Konfidenz"""
        if not matches:
            return []
        
        # Sortiere nach Position und Konfidenz
        sorted_matches = sorted(matches, key=lambda m: (m.start_pos, -m.confidence))
        
        deduplicated = []
        last_end = -1
        
        for match in sorted_matches:
            # Keine Überlappung
            if match.start_pos >= last_end:
                deduplicated.append(match)
                last_end = match.end_pos
            # Überlappung, aber höhere Konfidenz
            elif deduplicated and match.confidence > deduplicated[-1].confidence:
                # Ersetze den letzten Match
                deduplicated[-1] = match
                last_end = match.end_pos
        
        return deduplicated

# Integration in den Real Analyzer
def enhance_real_analyzer():
    """Erweitert den Real Analyzer mit der Pattern Engine"""
    
    from .real_analyzer import RealMarkerAnalyzer, MarkerResult
    
    # Monkey-patch die detect-Methode
    original_analyze = RealMarkerAnalyzer.analyze_text
    
    def enhanced_analyze_text(self, text: str) -> Dict[str, Any]:
        """Erweiterte Analyse mit Pattern Engine"""
        
        # Verwende Pattern Engine
        if not hasattr(self, 'pattern_engine'):
            self.pattern_engine = MarkerPatternEngine(self.markers_path)
        
        # Erkenne Patterns
        pattern_matches = self.pattern_engine.detect_patterns(text, 'atomic')
        
        # Konvertiere zu MarkerResults
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
        
        # Konvertiere PatternMatches zu MarkerResults
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
        
        # Berechne Statistiken
        results['statistics'] = {
            'total_atomic_hits': len(results['atomic_hits']),
            'unique_atomic_markers': len(set(h.marker_id for h in results['atomic_hits'])),
            'high_risk_markers': self._count_high_risk_markers(results['atomic_hits'])
        }
        
        # Berechne Risk Score
        results['risk_score'] = self._calculate_risk_score(results)
        
        return results
    
    # Ersetze die Methode
    RealMarkerAnalyzer.analyze_text = enhanced_analyze_text
    
    print("✅ Real Analyzer mit Pattern Engine erweitert!")

# Auto-enhance beim Import
enhance_real_analyzer()

# Test-Funktion
if __name__ == "__main__":
    engine = MarkerPatternEngine()
    
    test_texts = [
        "Du legst alles auf die Goldwaage, deswegen knallt's hier ständig!",
        "Wenn du nicht immer widersprechen würdest, hätten wir keinen Streit.",
        "Wegen dir haben wir wieder Verspätung, wie immer.",
        "Das habe ich nie gesagt, du bildest dir das nur ein.",
        "Lass uns auf WhatsApp wechseln, diese App ist unpersönlich.",
        "Ich brauche dringend Geld für eine wichtige Operation."
    ]
    
    print("🧪 Teste Pattern Engine mit echten Beispielen:\n")
    
    for text in test_texts:
        print(f"📝 Text: '{text}'")
        matches = engine.detect_patterns(text)
        
        if matches:
            for match in matches:
                print(f"   ✅ TREFFER: {match.marker_id}")
                print(f"      Match: '{match.match_text}'")
                print(f"      Konfidenz: {match.confidence:.1%}")
        else:
            print(f"   ❌ Keine Treffer")
        print()
