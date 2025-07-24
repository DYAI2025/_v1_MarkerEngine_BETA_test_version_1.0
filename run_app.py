#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("MarkerEngine v1.0 starting...")
    try:
        from markerengine.gui.app import main as run_app
        run_app()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Installing dependencies...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        from markerengine.gui.app import main as run_app
        run_app()

if __name__ == "__main__":
    main()
