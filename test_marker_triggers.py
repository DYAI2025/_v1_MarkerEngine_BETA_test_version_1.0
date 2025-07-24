#!/usr/bin/env python3
"""
Test ob die Marker jetzt richtig triggern
"""
import sys
from pathlib import Path

# Füge den markerengine Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))

from markerengine.core.real_analyzer import RealMarkerAnalyzer
from markerengine.core.pattern_engine import MarkerPatternEngine

print("🧪 MARKER TRIGGER TEST")
print("=" * 60)

# Test-Nachrichten mit verschiedenen Marker-Triggern
test_messages = [
    # BLAME_SHIFT Marker
    ("Du legst alles auf die Goldwaage, deswegen knallt's.", "A_BLAME_SHIFT_MARKER"),
    ("Wenn du nicht widersprechen würdest, gäbe es keinen Streit.", "A_BLAME_SHIFT_MARKER"),
    ("Wegen dir haben wir Verspätung.", "A_BLAME_SHIFT_MARKER"),
    ("Das ist alles deine Schuld!", "A_BLAME_SHIFT_MARKER"),
    
    # GASLIGHTING Marker
    ("Du bildest dir das nur ein.", "GASLIGHTING"),
    ("Das habe ich nie gesagt.", "GASLIGHTING"),
    
    # PLATFORM_SWITCH (Scammer Verhalten)
    ("Lass uns auf WhatsApp wechseln, diese App ist unpersönlich.", "PLATFORM_SWITCH"),
    
    # CRISIS_MONEY_REQUEST
    ("Ich brauche dringend Geld für eine Operation.", "CRISIS_MONEY"),
    
    # Normale Nachrichten (sollten keine Treffer haben)
    ("Hey, wie geht's dir heute?", None),
    ("Schönes Wetter heute!", None),
]

# Erstelle Analyzer
print("\n📊 Initialisiere MarkerEngine...")
analyzer = RealMarkerAnalyzer()

# Teste jeden Text
total_tests = len(test_messages)
correct = 0

print(f"\n🔍 Teste {total_tests} Nachrichten:\n")

for i, (text, expected_marker) in enumerate(test_messages, 1):
    print(f"{i}. Text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
    print(f"   Erwartet: {expected_marker or 'Keine Treffer'}")
    
    # Analysiere
    results = analyzer.analyze_text(text)
    
    # Prüfe Ergebnisse
    if results['atomic_hits']:
        found_markers = [hit.marker_id for hit in results['atomic_hits']]
        print(f"   Gefunden: {', '.join(found_markers)}")
        
        # Prüfe ob erwartet
        if expected_marker:
            marker_found = any(expected_marker in marker for marker in found_markers)
            if marker_found:
                print("   ✅ KORREKT")
                correct += 1
            else:
                print("   ❌ FALSCH - Erwarteter Marker nicht gefunden")
        else:
            print("   ❌ FALSCH - Unerwartete Treffer")
    else:
        print("   Gefunden: Keine Treffer")
        if expected_marker is None:
            print("   ✅ KORREKT")
            correct += 1
        else:
            print("   ❌ FALSCH - Marker nicht erkannt")
    
    print(f"   Risk Score: {results['risk_score']:.1f}/10")
    print()

# Zusammenfassung
print("=" * 60)
print(f"\n📊 ERGEBNIS: {correct}/{total_tests} Tests bestanden ({correct/total_tests*100:.0f}%)")

if correct == total_tests:
    print("🎉 Alle Marker triggern korrekt!")
else:
    print("⚠️  Einige Marker triggern noch nicht richtig.")

# Detaillierter Test eines komplexen Texts
print("\n" + "=" * 60)
print("\n🔬 DETAILLIERTER TEST mit komplexem Text:")

complex_text = """
Hey Schatz, tut mir leid wegen gestern. Du weißt ja, wenn du nicht immer alles 
auf die Goldwaage legen würdest, hätten wir diese Streitereien nicht. 

Übrigens, diese Dating-App ist echt unpersönlich. Lass uns auf WhatsApp wechseln, 
da können wir besser schreiben. Meine Nummer ist...

Ach ja, ich habe ein kleines Problem. Mein Konto wurde gesperrt und ich brauche 
dringend 500€ für die Miete. Kannst du mir helfen? Nur als Leihgabe natürlich.

Du bildest dir das mit meiner Ex nur ein. Das war nie so wie du denkst.
"""

print("📝 Text enthält mehrere Marker-Trigger:")
print(complex_text)
print("\n🔍 Analysiere...")

results = analyzer.analyze_text(complex_text)

print(f"\n📊 Gefundene Marker: {results['statistics']['total_atomic_hits']}")
print(f"📊 Unique Marker: {results['statistics']['unique_atomic_markers']}")
print(f"📊 High-Risk Marker: {results['statistics']['high_risk_markers']}")
print(f"⚠️  Risk Score: {results['risk_score']:.1f}/10")

if results['atomic_hits']:
    print("\n🎯 Details der Treffer:")
    for hit in results['atomic_hits'][:10]:  # Erste 10
        print(f"\n   Marker: {hit.marker_id}")
        print(f"   Text: '{hit.matches[0]}'")
        print(f"   Konfidenz: {hit.confidence:.1%}")
        print(f"   Position: {hit.position}")

print("\n✅ Test abgeschlossen!")
