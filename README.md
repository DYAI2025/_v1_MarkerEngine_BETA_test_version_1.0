# 🔍 MarkerEngine v1.0

**Intelligente WhatsApp-Chat Analyse mit KI-Integration**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Kimi K2](https://img.shields.io/badge/AI-Kimi%20K2-purple.svg)](https://platform.moonshot.ai/)

MarkerEngine ist eine Desktop-Anwendung zur Muster- und Betrugsanalyse in WhatsApp-Chats mit optionaler KI-Unterstützung durch Kimi K2.

## ✨ Features

- 📱 **WhatsApp-Chat Analyse**: Drag & Drop von Chat-Exporten (.txt)
- 🎯 **Regel-basierte Analyse**: Vordefinierte Marker für Kommunikationsmuster
- 🤖 **KI-Integration (Kimi K2)**: Erweiterte Insights durch KI-Analyse
- 🔍 **Dual-Analyse**: Trennung zwischen Regel- und KI-Ergebnissen
- 📊 **Detaillierte Statistiken**: Wort-/Zeichenzahl, Marker-Verteilung
- 🌓 **Dark Mode UI**: Modernes, augenschonendes Interface
- 🔒 **Datenschutz**: Lokale Analyse, nur KI-Anfragen gehen an API

## 🚀 Quick Start

### 1. Installation

```bash
# Repository klonen
git clone https://github.com/DYAI2025/_v1_MarkerEngine_BETA_test_version_1.0.git
cd _v1_MarkerEngine_BETA_test_version_1.0

# Dependencies installieren
pip install -r requirements.txt
```

### 2. KI-Features aktivieren (Optional aber empfohlen)

1. Kopiere `.env.example` zu `.env`:
   ```bash
   cp .env.example .env
   ```

2. Füge deinen Kimi K2 API Key ein:
   ```
   KIMI_API_KEY=sk-dein-api-key-hier
   ```

   > 🔑 Bekomme deinen API Key auf: https://platform.moonshot.ai/

### 3. App starten

**Mac:**
```bash
chmod +x run_macos.command
./run_macos.command
```

**Windows:**
```
Doppelklick auf run_windows.bat
```

**Development:**
```bash
python run_app.py
```

## 📱 WhatsApp-Chat exportieren

**iPhone:**
1. WhatsApp → Chat öffnen
2. Kontaktname antippen
3. "Chat exportieren" → "Ohne Medien"
4. Als .txt speichern

**Android:**
1. WhatsApp → Chat öffnen  
2. ⋮ (Drei Punkte) → Mehr → Chat exportieren
3. "Ohne Medien" wählen
4. Als .txt speichern

## 🎯 Was wird analysiert?

### Regel-basierte Marker:
- **Emotionen**: Positive/negative Stimmungen
- **Dringlichkeit**: Zeitdruck-Indikatoren  
- **Geld**: Finanzielle Themen
- **Vertrauen**: Vertrauensappelle
- **Manipulation**: Manipulative Muster

### KI-Analyse (Kimi K2):
- **Sentiment-Analyse**: Gesamtstimmung des Chats
- **Hauptthemen**: Automatische Themenerkennung
- **Risiko-Indikatoren**: Betrugs- und Manipulationsmuster
- **Kommunikationsmuster**: Verhaltensanalyse
- **Zusammenfassung**: KI-generierte Übersicht

## 🔧 Konfiguration

Die App funktioniert ohne Konfiguration. Für KI-Features:

1. **In der App**: API Key direkt in der GUI eingeben
2. **Oder via .env**: Datei erstellen mit `KIMI_API_KEY=...`

## 📊 Ergebnisse verstehen

Die App zeigt drei Tabs:

1. **📋 Regel-Analyse**: Gefundene Marker und Statistiken
2. **🤖 KI-Analyse**: Kimi K2 Insights (wenn API Key vorhanden)
3. **💡 Insights**: Kombinierte Warnungen und Muster

### Schweregrade:
- 🔴 **Hoch**: Sofortige Aufmerksamkeit erforderlich
- 🟡 **Mittel**: Verdächtige Muster
- 🟢 **Niedrig**: Informative Hinweise

## 🛡️ Datenschutz

- Regel-Analyse: 100% lokal auf deinem Computer
- KI-Analyse: Nur Text-Auszüge (max 2000 Zeichen) werden an Kimi K2 API gesendet
- Keine Datenspeicherung auf Servern
- API-Kommunikation nur wenn explizit aktiviert

## 🐛 Troubleshooting

**"Keine KI-Analyse verfügbar"**
- Prüfe deinen API Key in den Einstellungen
- Stelle sicher, dass du Internet hast
- Überprüfe dein API-Guthaben auf platform.moonshot.ai

**"Import Error"**
- Installiere alle Dependencies: `pip install -r requirements.txt`
- Python 3.8+ erforderlich

## 📈 Geplante Features

- [ ] Audio-Transkription (WhatsApp Sprachnachrichten)
- [ ] Export als PDF-Report
- [ ] Batch-Analyse mehrerer Chats
- [ ] Weitere Sprachen (EN, ES, FR)
- [ ] Custom Marker-Profile

## 📄 Lizenz

MIT License - siehe LICENSE

---

Entwickelt mit ❤️ und Claude | Powered by Kimi K2 🤖
