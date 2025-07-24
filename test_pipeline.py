#!/usr/bin/env python3
"""
Test-Script für die MarkerEngine Pipeline
Testet ob alle 4 Ebenen (Atomic → Semantic → Cluster → Meta) funktionieren
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from markerengine.core.engine import MarkerEngine
import json
from datetime import datetime

# Test-Chat (ein realistischer WhatsApp-Export)
TEST_CHAT = """
[07.11.24, 14:32:15] Sarah: Hey, wie geht's dir? Lange nichts gehört 😊
[07.11.24, 14:33:42] Tom: Hi! Ja, war viel los. Dir gut?
[07.11.24, 14:34:18] Sarah: Ja, alles okay. Vermisse unsere Gespräche
[07.11.24, 14:35:02] Tom: Stimmt, war echt lange her
[07.11.24, 14:35:45] Sarah: Hast du Lust, mal wieder was zu unternehmen?
[07.11.24, 14:37:23] Tom: Klar, aber bin grad echt im Stress mit der Arbeit
[07.11.24, 14:38:01] Sarah: Oh, verstehe. Wann hättest du denn Zeit?
[07.11.24, 14:40:15] Tom: Schwer zu sagen... vielleicht nächste Woche?
[07.11.24, 14:41:33] Sarah: Okay... du sagst das jetzt schon zum dritten Mal 😕
[07.11.24, 14:43:47] Tom: Sorry, ich weiß. Ist echt nicht persönlich gemeint
[07.11.24, 14:44:29] Sarah: Schon klar. Wenn du keine Zeit hast, ist das okay
[07.11.24, 14:46:12] Tom: Nein, ich will schon! Nur grad ist echt viel
[07.11.24, 14:47:55] Sarah: Ich verstehe. Meld dich einfach, wenn du Zeit hast
[07.11.24, 14:49:03] Tom: Mach ich! Versprochen
[07.11.24, 14:50:22] Sarah: Alles klar. Pass auf dich auf
[07.11.24, 14:51:44] Tom: Du auch! Bis bald
[08.11.24, 09:15:33] Tom: Morgen! Wie war dein Tag gestern?
[08.11.24, 09:45:21] Sarah: Hi. War okay. Bei dir?
[08.11.24, 09:47:02] Tom: Ganz gut. Hör mal, wegen nächster Woche...
[08.11.24, 09:48:15] Sarah: Lass mich raten - wird doch nichts?
[08.11.24, 09:50:33] Tom: Nein! Ich wollte fragen ob Donnerstag passt
[08.11.24, 09:52:47] Sarah: Oh! Ja, Donnerstag geht
[08.11.24, 09:54:01] Tom: Super! Kino oder essen gehen?
[08.11.24, 09:55:28] Sarah: Essen wäre schön. Können wir dann mal richtig reden
[08.11.24, 09:57:42] Tom: Klar, gerne. Italiener?
[08.11.24, 09:59:13] Sarah: Perfekt! Freu mich 😊
"""

def test_pipeline():
    """Testet die komplette Marker-Pipeline"""
    print("=" * 60)
    print("MARKERENGINE PIPELINE TEST")
    print("=" * 60)
    
    # Engine initialisieren
    print("\n1. Initialisiere MarkerEngine...")
    engine = MarkerEngine()
    
    # Prüfe ob Marker geladen wurden
    print(f"\n2. Geladene Marker:")
    print(f"   - Atomic: {len(engine.atomic_markers)}")
    print(f"   - Semantic: {len(engine.semantic_markers)}")
    print(f"   - Cluster: {len(engine.cluster_markers)}")
    print(f"   - Meta: {len(engine.meta_markers)}")
    
    if not engine.atomic_markers:
        print("\n❌ FEHLER: Keine Atomic Marker geladen!")
        print("   Stelle sicher, dass der /Marker/atomic/ Ordner existiert")
        return False
    
    # Analyse durchführen
    print("\n3. Führe Analyse durch...")
    result = engine.analyze(TEST_CHAT)
    
    # Ergebnisse prüfen
    print(f"\n4. Analyse-Ergebnisse:")
    print(f"   ✓ Atomic Hits: {len(result.atomic_hits)}")
    print(f"   ✓ Semantic Hits: {len(result.semantic_hits)}")
    print(f"   ✓ Cluster Hits: {len(result.cluster_hits)}")
    print(f"   ✓ Meta Hits: {len(result.meta_hits)}")
    
    # Details ausgeben
    if result.atomic_hits:
        print(f"\n5. Beispiel Atomic Hits:")
        for hit in result.atomic_hits[:5]:
            print(f"   - {hit.marker_name}: '{hit.text}'")
    
    if result.insights:
        print(f"\n6. Generierte Insights:")
        for insight in result.insights:
            print(f"   - [{insight['level']}] {insight['message']}")
    
    # Speichern der Ergebnisse
    output_file = "test_analysis_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_timestamp': datetime.now().isoformat(),
            'statistics': result.statistics,
            'atomic_count': len(result.atomic_hits),
            'semantic_count': len(result.semantic_hits),
            'cluster_count': len(result.cluster_hits),
            'meta_count': len(result.meta_hits),
            'insights': result.insights
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n7. Ergebnisse gespeichert in: {output_file}")
    
    # Erfolgsprüfung
    success = len(result.atomic_hits) > 0
    
    if success:
        print("\n✅ PIPELINE TEST ERFOLGREICH!")
    else:
        print("\n❌ PIPELINE TEST FEHLGESCHLAGEN!")
        print("   Keine Atomic Hits gefunden. Prüfe die Marker-Definitionen.")
    
    return success


if __name__ == "__main__":
    test_pipeline()
