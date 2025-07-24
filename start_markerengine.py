#!/usr/bin/env python3
"""
MarkerEngine Launcher - Startet die App mit echten Markern
"""
import sys
import os
from pathlib import Path

# Füge den markerengine Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))

try:
    from markerengine.gui.main_window import main
    
    print("🚀 Starte MarkerEngine mit echten Markern...")
    print("📁 Marker-Verzeichnis: markers/")
    print("✅ Alle Systeme bereit!")
    
    main()
    
except ImportError as e:
    print(f"❌ Import-Fehler: {e}")
    print("Installiere erst die Requirements:")
    print("  pip install PySide6 PyYAML")
    sys.exit(1)
except Exception as e:
    print(f"❌ Fehler beim Start: {e}")
    sys.exit(1)
