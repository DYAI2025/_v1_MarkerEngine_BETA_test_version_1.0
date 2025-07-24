#!/usr/bin/env python3
"""
Vereinfachter Test mit direktem Atomic Marker Matching
"""

import os
import re
import yaml
from pathlib import Path

# Basis-Pfad zu den Markern
MARKER_PATH = Path("/Users/benjaminpoersch/claude_desktop/_v1_MarkerEngine_BETA_test_version_1.0/Marker")

def load_and_test_markers():
    print("=== DIREKTER MARKER TEST ===\n")
    
    # Lade ein paar Test-Marker
    test_markers = [
        "A_BLAME_SHIFT_MARKER.yaml",
        "EMOTIONAL_WITHDRAW.yaml",
        "CONNECTION_POSITIVITY_MARKER.yaml"
    ]
    
    test_text = """
    Tom: Du legst alles auf die Goldwaage, deswegen knallt's
    Sarah: Ich bin traurig
    Tom: Nicht meine Schuld, du hast mich nicht informiert
    Sarah: Ich liebe dich
    Tom: Selber schuld, wenn du so empfindlich bist
    """
    
    found_matches = []
    
    for marker_file in test_markers:
        file_path = MARKER_PATH / "atomic" / marker_file
        if not file_path.exists():
            print(f"❌ Datei nicht gefunden: {marker_file}")
            continue
            
        print(f"\n📄 Teste: {marker_file}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        # Extrahiere Beispiele
        examples = []
        if 'beispiele' in data:
            examples = data['beispiele']
        elif 'marker' in data and 'examples' in data['marker']:
            examples = data['marker']['examples']
            
        print(f"   Gefundene Beispiele: {len(examples)}")
        
        # Teste jedes Beispiel
        for example in examples[:3]:  # Erste 3 Beispiele
            # Bereinige
            clean = example.strip().strip('"').strip("'").strip('-').strip()
            print(f"   Beispiel: '{clean[:50]}...'")
            
            # Suche im Text
            if clean.lower() in test_text.lower():
                print(f"   ✅ GEFUNDEN im Test-Text!")
                found_matches.append((marker_file, clean))
            
    print(f"\n\n=== ZUSAMMENFASSUNG ===")
    print(f"Gefundene Matches: {len(found_matches)}")
    for marker, text in found_matches:
        print(f"  • {marker}: '{text[:50]}...'")
        
    # Jetzt teste die echte Engine
    print("\n\n=== TESTE ECHTE ENGINE ===")
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from markerengine.core.engine import MarkerEngine
    
    engine = MarkerEngine()
    print(f"Engine geladen mit {len(engine.atomic_markers)} Atomic Markers")
    print(f"Kompilierte Patterns: {len(engine.compiled_patterns)}")
    
    # Zeige welche Marker Pattern haben
    markers_with_patterns = [m for m, p in engine.compiled_patterns.items() if p]
    print(f"Marker mit Patterns: {len(markers_with_patterns)}")
    if markers_with_patterns:
        print(f"Erste 5: {markers_with_patterns[:5]}")
    
    # Teste Analyse
    result = engine.analyze(test_text)
    print(f"\nAnalyse-Ergebnis:")
    print(f"  Atomic Hits: {len(result.atomic_hits)}")
    for hit in result.atomic_hits:
        print(f"    • {hit.marker_name}: '{hit.text}'")


if __name__ == "__main__":
    load_and_test_markers()
