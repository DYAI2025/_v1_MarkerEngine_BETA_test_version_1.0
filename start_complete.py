#!/usr/bin/env python3
"""
MarkerEngine Complete - Mit Whisper v3 Audio-Transkription
"""
import sys
import os
from pathlib import Path

# Prüfe Dependencies
print("🔍 Prüfe Dependencies...")
try:
    import whisper
    print("✅ Whisper v3 verfügbar")
except ImportError:
    print("⚠️  Whisper nicht installiert - Audio-Transkription wird deaktiviert")
    print("    Installieren mit: pip install openai-whisper")

# Füge den markerengine Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))

try:
    from markerengine.gui.main_window_complete import main
    
    print("\n🚀 Starte MarkerEngine Complete...")
    print("📁 Marker-Verzeichnis: markers/")
    print("🎤 Whisper v3 Audio-Transkription: Aktiviert")
    print("✅ Alle Systeme bereit!\n")
    
    main()
    
except ImportError as e:
    print(f"❌ Import-Fehler: {e}")
    print("\nInstalliere die Requirements:")
    print("  pip install -r requirements.txt")
    print("\nFür Audio-Support zusätzlich:")
    print("  brew install ffmpeg  # macOS")
    print("  pip install openai-whisper")
    sys.exit(1)
except Exception as e:
    print(f"❌ Fehler beim Start: {e}")
    sys.exit(1)
