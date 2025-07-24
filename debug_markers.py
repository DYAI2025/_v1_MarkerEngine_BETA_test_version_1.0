#!/usr/bin/env python3
"""
Debug-Script für die MarkerEngine
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from markerengine.core.engine import MarkerEngine
import logging

# Aktiviere Debug-Logging
logging.basicConfig(level=logging.DEBUG)

# Test-Text mit exakten Phrasen aus den Markern
TEST_PHRASES = [
    "Du legst alles auf die Goldwaage, deswegen knallt's",
    "Nicht meine Schuld, du hast mich nicht informiert",
    "Selber schuld, wenn du so empfindlich bist",
    "Wenn du nicht immer so drängen würdest",
    "Ich liebe dich",
    "wenig Zeit",
    "bin mir nicht sicher"
]

def debug_markers():
    print("=== MARKERENGINE DEBUG ===\n")
    
    # Engine initialisieren
    engine = MarkerEngine()
    
    print(f"1. Geladene Marker:")
    print(f"   - Atomic: {len(engine.atomic_markers)}")
    print(f"   - Patterns kompiliert: {len(engine.compiled_patterns)}")
    
    # Zeige erste 5 Atomic Marker
    print(f"\n2. Erste 5 Atomic Marker:")
    for i, (marker_id, data) in enumerate(list(engine.atomic_markers.items())[:5]):
        print(f"   {i+1}. {marker_id}")
        if 'beispiele' in data and data['beispiele']:
            print(f"      Beispiel: {data['beispiele'][0]}")
    
    # Teste einzelne Phrasen
    print(f"\n3. Teste einzelne Phrasen:")
    for phrase in TEST_PHRASES:
        print(f"\n   Testing: '{phrase}'")
        result = engine.analyze(phrase)
        if result.atomic_hits:
            for hit in result.atomic_hits:
                print(f"      ✓ GEFUNDEN: {hit.marker_name} - '{hit.text}'")
        else:
            print(f"      ✗ Keine Treffer")
    
    # Teste den vollen Chat
    print(f"\n4. Teste vollen Chat:")
    full_chat = """
    Tom: Du legst alles auf die Goldwaage, deswegen knallt's
    Sarah: Das ist unfair
    Tom: Nicht meine Schuld, du hast mich nicht informiert
    """
    
    result = engine.analyze(full_chat)
    print(f"   - Atomic Hits: {len(result.atomic_hits)}")
    for hit in result.atomic_hits:
        print(f"      • {hit.marker_name}: '{hit.text}'")


if __name__ == "__main__":
    debug_markers()
