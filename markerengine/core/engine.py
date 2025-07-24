#!/usr/bin/env python3
"""
MarkerEngine Core - Die echte Engine mit der vierstufigen Marker-Pipeline
Verwendet die ECHTEN Marker aus dem /Marker/ Ordner
"""

import os
import re
import yaml
import json
from typing import Dict, List, Set, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from collections import defaultdict
import logging
from datetime import datetime

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MarkerHit:
    """Repräsentiert einen Marker-Treffer"""
    marker_id: str
    marker_name: str
    text: str
    position_start: int
    position_end: int
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    

@dataclass
class AnalysisResult:
    """Komplettes Analyse-Ergebnis mit allen vier Ebenen"""
    atomic_hits: List[MarkerHit] = field(default_factory=list)
    semantic_hits: List[MarkerHit] = field(default_factory=list)
    cluster_hits: List[MarkerHit] = field(default_factory=list)
    meta_hits: List[MarkerHit] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    insights: List[Dict[str, Any]] = field(default_factory=list)
    

class MarkerEngine:
    """
    Die echte MarkerEngine mit vierstufiger Hierarchie:
    1. Atomic (A_)
    2. Semantic (S_) 
    3. Cluster (C_)
    4. Meta (MM_)
    """
    
    def __init__(self, marker_base_path: str = None):
        """Initialisiert die Engine mit dem Marker-Verzeichnis"""
        if marker_base_path is None:
            # Standard-Pfad zum echten Marker-Ordner
            marker_base_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "Marker"
            )
            
        self.marker_base_path = Path(marker_base_path)
        
        # Marker-Sammlungen für jede Ebene
        self.atomic_markers = {}
        self.semantic_markers = {}
        self.cluster_markers = {}
        self.meta_markers = {}
        
        # Kompilierte Regex-Patterns für Performance
        self.compiled_patterns = {}
        
        # Lade alle Marker
        self._load_all_markers()
        
    def _load_all_markers(self):
        """Lädt alle Marker aus den YAML-Dateien"""
        logger.info(f"Lade Marker aus: {self.marker_base_path}")
        
        # Atomic Markers
        atomic_path = self.marker_base_path / "atomic"
        if atomic_path.exists():
            for yaml_file in atomic_path.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and 'marker_name' in data:
                            marker_id = data['marker_name']
                            self.atomic_markers[marker_id] = data
                            
                            # Kompiliere Regex-Patterns aus den Beispielen
                            if 'beispiele' in data:
                                patterns = self._create_patterns_from_examples(data['beispiele'])
                                self.compiled_patterns[marker_id] = patterns
                                
                except Exception as e:
                    logger.error(f"Fehler beim Laden von {yaml_file}: {e}")
                    
        logger.info(f"Geladen: {len(self.atomic_markers)} Atomic Markers")
        
        # Semantic Markers
        semantic_path = self.marker_base_path / "semantic"
        if semantic_path.exists():
            for yaml_file in semantic_path.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data:
                            marker_id = data.get('id', yaml_file.stem)
                            self.semantic_markers[marker_id] = data
                except Exception as e:
                    logger.error(f"Fehler beim Laden von {yaml_file}: {e}")
                    
        logger.info(f"Geladen: {len(self.semantic_markers)} Semantic Markers")
        
        # Cluster Markers
        cluster_path = self.marker_base_path / "cluster"
        if cluster_path.exists():
            for yaml_file in cluster_path.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data:
                            marker_id = data.get('id', yaml_file.stem)
                            self.cluster_markers[marker_id] = data
                except Exception as e:
                    logger.error(f"Fehler beim Laden von {yaml_file}: {e}")
                    
        logger.info(f"Geladen: {len(self.cluster_markers)} Cluster Markers")
        
        # Meta Markers
        meta_path = self.marker_base_path / "meta_marker"
        if meta_path.exists():
            for yaml_file in meta_path.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data:
                            marker_id = data.get('id', yaml_file.stem)
                            self.meta_markers[marker_id] = data
                except Exception as e:
                    logger.error(f"Fehler beim Laden von {yaml_file}: {e}")
                    
        logger.info(f"Geladen: {len(self.meta_markers)} Meta Markers")
        
    def _create_patterns_from_examples(self, examples: List[str]) -> List[re.Pattern]:
        """Erstellt Regex-Patterns aus Beispielen"""
        patterns = []
        
        for example in examples:
            # Bereinige das Beispiel
            clean_example = example.strip().strip('"').strip('-').strip()
            
            # Escape special regex characters
            escaped = re.escape(clean_example)
            
            # Erlaube Variationen (Groß-/Kleinschreibung, Wortgrenzen)
            pattern = rf'\b{escaped}\b'
            
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                patterns.append(compiled)
            except Exception as e:
                logger.warning(f"Konnte Pattern nicht kompilieren: {pattern} - {e}")
                
        return patterns
        
    def analyze(self, text: str) -> AnalysisResult:
        """
        Führt die komplette vierstufige Analyse durch
        """
        logger.info("Starte Analyse...")
        result = AnalysisResult()
        
        # Phase 1: Atomic Marker Detection
        logger.info("Phase 1: Atomic Marker Detection")
        atomic_hits = self._detect_atomic_markers(text)
        result.atomic_hits = atomic_hits
        logger.info(f"Gefunden: {len(atomic_hits)} Atomic Hits")
        
        # Phase 2: Semantic Marker Evaluation
        logger.info("Phase 2: Semantic Marker Evaluation")
        semantic_hits = self._evaluate_semantic_markers(text, atomic_hits)
        result.semantic_hits = semantic_hits
        logger.info(f"Gefunden: {len(semantic_hits)} Semantic Hits")
        
        # Phase 3: Cluster Detection
        logger.info("Phase 3: Cluster Detection")
        cluster_hits = self._detect_clusters(text, semantic_hits)
        result.cluster_hits = cluster_hits
        logger.info(f"Gefunden: {len(cluster_hits)} Cluster Hits")
        
        # Phase 4: Meta Marker Triggering
        logger.info("Phase 4: Meta Marker Triggering")
        meta_hits = self._trigger_meta_markers(cluster_hits)
        result.meta_hits = meta_hits
        logger.info(f"Gefunden: {len(meta_hits)} Meta Hits")
        
        # Statistiken berechnen
        result.statistics = self._calculate_statistics(result)
        
        # Insights generieren
        result.insights = self._generate_insights(result)
        
        return result
        
    def _detect_atomic_markers(self, text: str) -> List[MarkerHit]:
        """Phase 1: Erkennt Atomic Markers im Text"""
        hits = []
        
        for marker_id, patterns in self.compiled_patterns.items():
            marker_data = self.atomic_markers.get(marker_id, {})
            
            for pattern in patterns:
                for match in pattern.finditer(text):
                    hit = MarkerHit(
                        marker_id=marker_id,
                        marker_name=marker_data.get('marker_name', marker_id),
                        text=match.group(0),
                        position_start=match.start(),
                        position_end=match.end(),
                        metadata={
                            'beschreibung': marker_data.get('beschreibung', ''),
                            'kategorie': marker_data.get('kategorie', 'UNCATEGORIZED')
                        }
                    )
                    hits.append(hit)
                    
        return hits
        
    def _evaluate_semantic_markers(self, text: str, atomic_hits: List[MarkerHit]) -> List[MarkerHit]:
        """Phase 2: Evaluiert Semantic Markers basierend auf Atomic Hits"""
        hits = []
        
        # Gruppiere Atomic Hits nach ID für schnelleren Zugriff
        atomic_by_id = defaultdict(list)
        for hit in atomic_hits:
            atomic_by_id[hit.marker_id].append(hit)
            
        for marker_id, marker_data in self.semantic_markers.items():
            # Prüfe ob die benötigten Atomic Markers vorhanden sind
            if 'composed_of' in marker_data:
                required_atomics = marker_data['composed_of']
                
                # Prüfe Regeln
                if self._check_semantic_rules(marker_data, atomic_by_id, text):
                    hit = MarkerHit(
                        marker_id=marker_id,
                        marker_name=marker_data.get('name', marker_id),
                        text=f"Semantic Pattern: {marker_id}",
                        position_start=0,
                        position_end=len(text),
                        confidence=0.85,
                        metadata={
                            'description': marker_data.get('description', ''),
                            'composed_of': required_atomics
                        }
                    )
                    hits.append(hit)
                    
        return hits
        
    def _check_semantic_rules(self, marker_data: Dict, atomic_by_id: Dict, text: str) -> bool:
        """Prüft ob die Regeln für einen Semantic Marker erfüllt sind"""
        rules = marker_data.get('rules', {})
        
        # Co-occurrence Regel
        if 'co_occurrence' in rules:
            co_rule = rules['co_occurrence']
            required = set(co_rule.get('markers', []))
            window = co_rule.get('window', 3)
            
            # Prüfe ob alle benötigten Marker im Fenster vorhanden sind
            found = set()
            for marker_id in required:
                if marker_id in atomic_by_id and atomic_by_id[marker_id]:
                    found.add(marker_id)
                    
            if found == required:
                return True
                
        # Frequency Regel
        if 'frequency' in rules:
            freq_rule = rules['frequency']
            marker = freq_rule.get('marker')
            min_count = freq_rule.get('min_count', 1)
            
            if marker in atomic_by_id and len(atomic_by_id[marker]) >= min_count:
                return True
                
        return False
        
    def _detect_clusters(self, text: str, semantic_hits: List[MarkerHit]) -> List[MarkerHit]:
        """Phase 3: Erkennt Cluster basierend auf Semantic Patterns"""
        hits = []
        
        # Gruppiere Semantic Hits nach ID
        semantic_by_id = defaultdict(list)
        for hit in semantic_hits:
            semantic_by_id[hit.marker_id].append(hit)
            
        for marker_id, marker_data in self.cluster_markers.items():
            if 'composed_of' in marker_data:
                required_semantics = marker_data['composed_of']
                
                # Prüfe ob genügend der benötigten Semantic Marker vorhanden sind
                found_count = 0
                for sem_id in required_semantics:
                    if sem_id in semantic_by_id:
                        found_count += 1
                        
                # Trigger threshold
                threshold = marker_data.get('trigger_threshold', len(required_semantics))
                
                if found_count >= threshold:
                    hit = MarkerHit(
                        marker_id=marker_id,
                        marker_name=marker_data.get('name', marker_id),
                        text=f"Cluster Pattern: {marker_id}",
                        position_start=0,
                        position_end=len(text),
                        confidence=0.75,
                        metadata={
                            'description': marker_data.get('description', ''),
                            'severity': marker_data.get('severity', 'medium')
                        }
                    )
                    hits.append(hit)
                    
        return hits
        
    def _trigger_meta_markers(self, cluster_hits: List[MarkerHit]) -> List[MarkerHit]:
        """Phase 4: Triggert Meta Markers basierend auf Clusters"""
        hits = []
        
        # Gruppiere Cluster Hits nach ID
        cluster_by_id = defaultdict(list)
        for hit in cluster_hits:
            cluster_by_id[hit.marker_id].append(hit)
            
        for marker_id, marker_data in self.meta_markers.items():
            if 'composed_of' in marker_data:
                required_clusters = marker_data['composed_of']
                
                # Prüfe Trigger Threshold
                found_count = 0
                for cluster_id in required_clusters:
                    if cluster_id in cluster_by_id:
                        found_count += 1
                        
                threshold = marker_data.get('trigger_threshold', 2)
                
                if found_count >= threshold:
                    hit = MarkerHit(
                        marker_id=marker_id,
                        marker_name=marker_data.get('name', marker_id),
                        text=f"Meta Pattern: {marker_id}",
                        position_start=0,
                        position_end=0,
                        confidence=0.9,
                        metadata={
                            'description': marker_data.get('description', ''),
                            'risk_level': marker_data.get('risk_level', 'high')
                        }
                    )
                    hits.append(hit)
                    
        return hits
        
    def _calculate_statistics(self, result: AnalysisResult) -> Dict[str, Any]:
        """Berechnet Statistiken über die Analyse"""
        return {
            'total_markers': (
                len(result.atomic_hits) + 
                len(result.semantic_hits) + 
                len(result.cluster_hits) + 
                len(result.meta_hits)
            ),
            'by_level': {
                'atomic': len(result.atomic_hits),
                'semantic': len(result.semantic_hits),
                'cluster': len(result.cluster_hits),
                'meta': len(result.meta_hits)
            },
            'unique_patterns': {
                'atomic': len(set(h.marker_id for h in result.atomic_hits)),
                'semantic': len(set(h.marker_id for h in result.semantic_hits)),
                'cluster': len(set(h.marker_id for h in result.cluster_hits)),
                'meta': len(set(h.marker_id for h in result.meta_hits))
            }
        }
        
    def _generate_insights(self, result: AnalysisResult) -> List[Dict[str, Any]]:
        """Generiert Insights aus den Analyse-Ergebnissen"""
        insights = []
        
        # Risk Assessment
        if result.meta_hits:
            insights.append({
                'type': 'risk_alert',
                'level': 'high',
                'message': f'Achtung: {len(result.meta_hits)} kritische Meta-Muster erkannt!',
                'patterns': [h.marker_name for h in result.meta_hits]
            })
            
        # Kommunikationsdynamik
        if result.cluster_hits:
            cluster_names = [h.marker_name for h in result.cluster_hits]
            insights.append({
                'type': 'communication_dynamic',
                'level': 'medium',
                'message': 'Folgende Kommunikationsdynamiken wurden identifiziert:',
                'patterns': cluster_names
            })
            
        # Emotionale Stimmung
        emotional_markers = [h for h in result.atomic_hits if 'EMO' in h.marker_id]
        if emotional_markers:
            insights.append({
                'type': 'emotional_tone',
                'level': 'info',
                'message': f'{len(emotional_markers)} emotionale Marker gefunden',
                'distribution': self._analyze_emotional_distribution(emotional_markers)
            })
            
        return insights
        
    def _analyze_emotional_distribution(self, emotional_markers: List[MarkerHit]) -> Dict[str, int]:
        """Analysiert die Verteilung emotionaler Marker"""
        distribution = defaultdict(int)
        
        for marker in emotional_markers:
            if 'HIGH_VALENCE' in marker.marker_id:
                distribution['positive'] += 1
            elif 'LOW_VALENCE' in marker.marker_id:
                distribution['negative'] += 1
            else:
                distribution['neutral'] += 1
                
        return dict(distribution)


# CLI Interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m markerengine.core.engine <textfile>")
        sys.exit(1)
        
    # Lade Text
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        text = f.read()
        
    # Initialisiere Engine
    engine = MarkerEngine()
    
    # Analysiere
    result = engine.analyze(text)
    
    # Ausgabe
    print(f"\n=== MARKER ENGINE ANALYSE ===")
    print(f"Atomic Hits: {len(result.atomic_hits)}")
    print(f"Semantic Hits: {len(result.semantic_hits)}")
    print(f"Cluster Hits: {len(result.cluster_hits)}")
    print(f"Meta Hits: {len(result.meta_hits)}")
    
    # Details
    if result.meta_hits:
        print("\n⚠️  KRITISCHE META-MARKER:")
        for hit in result.meta_hits:
            print(f"  - {hit.marker_name}: {hit.metadata.get('description', '')}")
            
    if result.insights:
        print("\n💡 INSIGHTS:")
        for insight in result.insights:
            print(f"  - [{insight['level'].upper()}] {insight['message']}")
            
    # JSON Export
    output_file = "analysis_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'statistics': result.statistics,
            'atomic_hits': [{'id': h.marker_id, 'text': h.text} for h in result.atomic_hits],
            'semantic_hits': [{'id': h.marker_id, 'name': h.marker_name} for h in result.semantic_hits],
            'cluster_hits': [{'id': h.marker_id, 'name': h.marker_name} for h in result.cluster_hits],
            'meta_hits': [{'id': h.marker_id, 'name': h.marker_name} for h in result.meta_hits],
            'insights': result.insights
        }, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ Analyse gespeichert in: {output_file}")
