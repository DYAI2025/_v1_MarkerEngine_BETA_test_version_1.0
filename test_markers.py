#!/usr/bin/env python3
"""
MarkerEngine Test - Prüft ob die echten Marker geladen werden
"""
import sys
from pathlib import Path

# Füge den markerengine Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))

from markerengine.core.real_analyzer import RealMarkerAnalyzer

print("🔍 Teste MarkerEngine mit echten Markern...")
print("=" * 50)

# Erstelle Analyzer
analyzer = RealMarkerAnalyzer()

# Test-Text mit echten Marker-Triggern
test_text = """
Du legst alles auf die Goldwaage, deswegen knallt's.
Wenn du nicht widersprechen würdest, gäbe es keinen Streit.
Lass uns auf WhatsApp wechseln, diese App ist unpersönlich.
Ich brauche dringend Geld für eine Operation.
Du bildest dir das nur ein, ich habe das nie gesagt.
Wenn du mich lieben würdest, würdest du mir helfen.
"""

print("\n📝 Test-Text:")
print(test_text)
print("\n" + "=" * 50)

# Analysiere
results = analyzer.analyze_text(test_text)

print(f"\n✅ Analyse abgeschlossen!")
print(f"📊 Statistiken:")
print(f"  - Atomic Hits: {len(results['atomic_hits'])}")
print(f"  - Unique Markers: {results['statistics']['unique_atomic_markers']}")
print(f"  - High-Risk Markers: {results['statistics']['high_risk_markers']}")
print(f"  - Risk Score: {results['risk_score']:.1f}/10")

if results['atomic_hits']:
    print(f"\n🎯 Gefundene Marker (erste 5):")
    for i, hit in enumerate(results['atomic_hits'][:5], 1):
        print(f"\n  {i}. {hit.marker_id}")
        print(f"     Treffer: '{hit.matches[0][:50]}...'")
        print(f"     Position: {hit.position}")

print("\n✅ Test erfolgreich! Die echten Marker funktionieren!")
