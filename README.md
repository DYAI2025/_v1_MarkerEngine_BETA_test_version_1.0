# 🔍 MarkerEngine v1.0 - WhatsApp Chat Analyse mit KI

**Professionelle Kommunikationsanalyse mit vierstufiger Marker-Pipeline**

## ✨ Features

- **Vierstufige Analyse-Pipeline:**
  - 🔤 **Atomic Markers**: Erkennung einzelner Schlüsselwörter und Phrasen
  - 🧩 **Semantic Patterns**: Kombinationen von Atomics zu Bedeutungsmustern
  - 🌐 **Cluster Dynamics**: Erkennung von Kommunikationsdynamiken
  - ⚡ **Meta Patterns**: Hochrangige Risiko- und Verhaltensmuster

- **Echte Marker aus 3 Wochen Entwicklung:**
  - Über 100+ vordefinierte Marker
  - Wissenschaftlich fundiert (Gottman, Satir, Schulz von Thun)
  - Erkennung von Manipulation, Gaslighting, emotionalen Mustern

- **Optionale KI-Integration:**
  - Kimi K2 API für erweiterte Insights
  - Sentiment-Analyse
  - Risikobewertung

## 🚀 Installation & Start

### Voraussetzungen
- Python 3.8+
- 500 MB freier Speicherplatz

### Quick Start

1. **Repository klonen:**
   ```bash
   git clone https://github.com/DYAI2025/_v1_MarkerEngine_BETA_test_version_1.0.git
   cd _v1_MarkerEngine_BETA_test_version_1.0
   ```

2. **Dependencies installieren:**
   ```bash
   pip install -r requirements.txt
   ```

3. **App starten:**
   ```bash
   python run_markerengine.py
   ```

### Pipeline testen
```bash
python test_pipeline.py
```

## 📱 WhatsApp Chat exportieren

### iPhone
1. WhatsApp → Chat öffnen
2. Kontakt antippen → "Chat exportieren"
3. "Ohne Medien" wählen
4. Als .txt speichern

### Android
1. WhatsApp → Chat öffnen
2. Drei Punkte → "Mehr" → "Chat exportieren"
3. "Ohne Medien" wählen

## 🤖 KI-Features aktivieren

1. Erstelle eine `.env` Datei:
   ```bash
   cp .env.example .env
   ```

2. Füge deinen Kimi API Key ein:
   ```
   KIMI_API_KEY=sk-your-api-key-here
   ```

## 🏗️ Projektstruktur

```
_v1_MarkerEngine_BETA_test_version_1.0/
├── Marker/                  # ECHTE Marker-Definitionen
│   ├── atomic/             # 100+ Atomic Markers
│   ├── semantic/           # Semantic Patterns
│   ├── cluster/            # Cluster Dynamics
│   └── meta_marker/        # Meta Patterns
├── markerengine/           # Core Engine
│   ├── core/              # Analyse-Engine
│   ├── gui/               # PySide6 GUI
│   └── kimi/              # KI-Integration
└── run_markerengine.py    # Hauptstartpunkt
```

## 📊 Analyse-Ergebnisse

Die Engine liefert:
- **Statistiken**: Anzahl gefundener Marker pro Ebene
- **Atomic Hits**: Konkrete Textstellen mit Markern
- **Semantic Patterns**: Erkannte Bedeutungsmuster
- **Cluster Dynamics**: Kommunikationsdynamiken
- **Meta Patterns**: Kritische Verhaltensmuster
- **Insights**: KI-generierte Empfehlungen

## 🔧 Entwicklung

### Tests ausführen
```bash
python test_pipeline.py
```

### Neue Marker hinzufügen
Marker sind YAML-Dateien im `/Marker/` Verzeichnis:
- Atomic: `/Marker/atomic/MARKER_NAME.yaml`
- Semantic: `/Marker/semantic/S_PATTERN.yaml`
- Cluster: `/Marker/cluster/C_DYNAMIC.yaml`
- Meta: `/Marker/meta_marker/MM_META.yaml`

## 📝 Lizenz

MIT License - siehe LICENSE

## 🙏 Credits

- Entwickelt mit Unterstützung von Claude (Anthropic)
- Basierend auf Kommunikationstheorien von Gottman, Satir, Schulz von Thun
- Frontend inspiriert von fraud-detection-with-gnn

---

**Wichtig**: Diese Software analysiert Kommunikationsmuster zu Schutzzwecken. Die Ergebnisse sind Hinweise, keine Diagnosen.
