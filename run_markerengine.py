#!/usr/bin/env python3
"""
MarkerEngine - Hauptstartpunkt der Anwendung
Startet die GUI mit der echten Marker-Pipeline
"""

import sys
import os
from pathlib import Path

# Füge das Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importiere die GUI
from markerengine.gui.app import main

if __name__ == "__main__":
    print("🚀 Starte MarkerEngine...")
    print("📁 Verwende Marker aus:", project_root / "Marker")
    
    # Prüfe ob Marker vorhanden sind
    marker_path = project_root / "Marker"
    if not marker_path.exists():
        print("⚠️  WARNUNG: Marker-Ordner nicht gefunden!")
        print("   Erwarteter Pfad:", marker_path)
        
    # Starte die GUI
    main()
