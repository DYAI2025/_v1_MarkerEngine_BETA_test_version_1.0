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

# Test-Chat (ein realistischer WhatsApp-Export mit mehr Marker-relevanten Phrasen)
TEST_CHAT = """
[07.11.24, 14:32:15] Sarah: Hey, wie geht's dir? Lange nichts gehört 😊
[07.11.24, 14:33:42] Tom: Hi! Ja, war viel los. Dir gut?
[07.11.24, 14:34:18] Sarah: Ja, alles okay. Vermisse unsere Gespräche. Ich liebe es, mit dir zu reden
[07.11.24, 14:35:02] Tom: Stimmt, war echt lange her. Tut mir leid
[07.11.24, 14:35:45] Sarah: Hast du Lust, mal wieder was zu unternehmen? Wäre schön, dich zu sehen
[07.11.24, 14:37:23] Tom: Klar, aber bin grad echt im Stress mit der Arbeit. Wenig Zeit momentan
[07.11.24, 14:38:01] Sarah: Oh, verstehe. Wann hättest du denn Zeit?
[07.11.24, 14:40:15] Tom: Schwer zu sagen... vielleicht nächste Woche? Bin mir nicht sicher
[07.11.24, 14:41:33] Sarah: Okay... du sagst das jetzt schon zum dritten Mal 😕 Fühle mich etwas enttäuscht
[07.11.24, 14:43:47] Tom: Nicht meine Schuld, du hast mich nicht informiert, dass es dir so wichtig ist
[07.11.24, 14:44:29] Sarah: Wie bitte? Du hättest dich auch mal melden können
[07.11.24, 14:46:12] Tom: Wenn du nicht immer so drängen würdest, wäre es entspannter
[07.11.24, 14:47:55] Sarah: Ich dränge nicht, ich vermisse dich einfach nur
[07.11.24, 14:49:03] Tom: Du legst alles auf die Goldwaage, deswegen knallt's
[07.11.24, 14:50:22] Sarah: Das ist jetzt unfair. Ich bin einfach traurig darüber
[07.11.24, 14:51:44] Tom: Selber schuld, wenn du so empfindlich bist
[08.11.24, 09:15:33] Tom: Morgen! Tut mir leid wegen gestern. War blöd von mir
[08.11.24, 09:45:21] Sarah: Hi. Danke für die Entschuldigung. War auch nicht leicht für mich
[08.11.24, 09:47:02] Tom: Ich wollte dich nicht verletzen. Können wir neu anfangen?
[08.11.24, 09:48:15] Sarah: Gerne. Ich freue mich darauf
[08.11.24, 09:50:33] Tom: Wie wäre es mit Donnerstag? Abendessen beim Italiener?
[08.11.24, 09:52:47] Sarah: Das klingt wunderbar! Ich bin glücklich, dass wir das klären konnten
[08.11.24, 09:54:01] Tom: Ich auch. Freue mich auf dich
[08.11.24, 09:55:28] Sarah: Bis Donnerstag dann! ❤️
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
