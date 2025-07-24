"""
MarkerEngine GUI - Mit Whisper v3 Integration
"""
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QProgressBar, QTabWidget, QFileDialog, QMessageBox,
                             QGroupBox, QLineEdit, QCheckBox, QComboBox)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPalette, QColor, QDragEnterEvent, QDropEvent

# Füge den Pfad zum markerengine Modul hinzu
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from markerengine.core.complete_analyzer import CompleteWhatsAppAnalyzer, analyze_whatsapp_complete
    ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import complete_analyzer: {e}")
    ANALYZER_AVAILABLE = False

class AnalysisThread(QThread):
    """Worker Thread für die komplette Analyse"""
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, export_path, enable_audio=True, whisper_model="large-v3"):
        super().__init__()
        self.export_path = export_path
        self.enable_audio = enable_audio
        self.whisper_model = whisper_model
        
    def run(self):
        """Führt die komplette Analyse aus"""
        try:
            self.status.emit("🔍 Starte Analyse...")
            self.progress.emit(10)
            
            # Phase 1: Audio-Transkription
            if self.enable_audio:
                self.status.emit("🎤 Transkribiere Sprachnachrichten...")
                self.progress.emit(30)
            
            # Verwende den kompletten Analyzer
            results = analyze_whatsapp_complete(
                self.export_path,
                enable_audio=self.enable_audio,
                whisper_model=self.whisper_model
            )
            
            self.progress.emit(100)
            self.status.emit("✅ Analyse abgeschlossen!")
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(f"Fehler bei der Analyse: {str(e)}")

class MarkerEngineGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.export_path = None
        self.analysis_results = None
        self.init_ui()
        
    def init_ui(self):
        """Initialisiert die UI"""
        self.setWindowTitle("🔍 MarkerEngine - Mit Whisper v3")
        self.setGeometry(100, 100, 1400, 900)
        
        # Haupt-Widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Header
        header = QLabel("MarkerEngine - WhatsApp Analyse mit Spracherkennung")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: bold;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #3498db);
                color: white;
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(header)
        
        # Settings Group
        settings_group = QGroupBox("⚙️ Einstellungen")
        settings_layout = QVBoxLayout()
        
        # Audio Settings
        audio_layout = QHBoxLayout()
        self.audio_checkbox = QCheckBox("🎤 Sprachnachrichten transkribieren")
        self.audio_checkbox.setChecked(True)
        self.audio_checkbox.stateChanged.connect(self.on_audio_toggle)
        audio_layout.addWidget(self.audio_checkbox)
        
        # Whisper Model Selection
        audio_layout.addWidget(QLabel("Whisper Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large", "large-v3"])
        self.model_combo.setCurrentText("large-v3")
        self.model_combo.setToolTip("large-v3 = Beste Qualität (5GB), tiny = Schnell (39MB)")
        audio_layout.addWidget(self.model_combo)
        
        audio_layout.addStretch()
        settings_layout.addLayout(audio_layout)
        
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        
        # File Selection Area
        file_group = QGroupBox("📁 WhatsApp-Export auswählen")
        file_layout = QVBoxLayout()
        
        # Info Text
        info_label = QLabel("Wählen Sie den WhatsApp-Export Ordner oder die _chat.txt Datei")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        file_layout.addWidget(info_label)
        
        # Drag & Drop Area
        self.drop_area = QLabel("📂 WhatsApp-Export hier ablegen\n(Ordner mit _chat.txt und Audio-Dateien)\noder klicken zum Auswählen")
        self.drop_area.setAlignment(Qt.AlignCenter)
        self.drop_area.setMinimumHeight(150)
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 3px dashed #3498db;
                border-radius: 10px;
                background: #ecf0f1;
                font-size: 16px;
                color: #7f8c8d;
            }
            QLabel:hover {
                background: #d5dbdb;
                border-color: #2980b9;
            }
        """)
        self.drop_area.setAcceptDrops(True)
        self.drop_area.mousePressEvent = self.select_export
        file_layout.addWidget(self.drop_area)
        
        # Selected Path Label
        self.path_label = QLabel("Kein Export ausgewählt")
        self.path_label.setAlignment(Qt.AlignCenter)
        self.path_label.setWordWrap(True)
        file_layout.addWidget(self.path_label)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # Analyze Button
        self.analyze_btn = QPushButton("🚀 Analyse starten")
        self.analyze_btn.setMinimumHeight(60)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #229954);
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #229954, stop:1 #1e8449);
            }
            QPushButton:disabled {
                background: #95a5a6;
            }
        """)
        main_layout.addWidget(self.analyze_btn)
        
        # Progress Area
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; color: #3498db;")
        main_layout.addWidget(self.status_label)
        
        # Results Tabs
        self.results_tabs = QTabWidget()
        self.results_tabs.setVisible(False)
        
        # Tab 1: Übersicht
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        overview_layout.addWidget(self.overview_text)
        self.results_tabs.addTab(overview_tab, "📊 Übersicht")
        
        # Tab 2: Audio-Transkriptionen
        audio_tab = QWidget()
        audio_layout = QVBoxLayout(audio_tab)
        self.audio_text = QTextEdit()
        self.audio_text.setReadOnly(True)
        audio_layout.addWidget(self.audio_text)
        self.results_tabs.addTab(audio_tab, "🎤 Sprachnachrichten")
        
        # Tab 3: Gefundene Marker
        markers_tab = QWidget()
        markers_layout = QVBoxLayout(markers_tab)
        self.markers_text = QTextEdit()
        self.markers_text.setReadOnly(True)
        markers_layout.addWidget(self.markers_text)
        self.results_tabs.addTab(markers_tab, "🎯 Gefundene Marker")
        
        # Tab 4: Risiko-Bewertung
        risk_tab = QWidget()
        risk_layout = QVBoxLayout(risk_tab)
        self.risk_text = QTextEdit()
        self.risk_text.setReadOnly(True)
        risk_layout.addWidget(self.risk_text)
        self.results_tabs.addTab(risk_tab, "⚠️ Risiko-Bewertung")
        
        main_layout.addWidget(self.results_tabs)
        
        # Apply Dark Theme
        self.apply_theme()
        
    def apply_theme(self):
        """Wendet das Dark Theme an"""
        self.setStyleSheet("""
            QMainWindow {
                background: #2c3e50;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: white;
                border: 2px solid #34495e;
                border-radius: 10px;
                padding-top: 15px;
                margin-top: 10px;
                background: #34495e;
            }
            QGroupBox::title {
                padding: 5px 10px;
                background: #2c3e50;
                border-radius: 5px;
            }
            QTextEdit {
                background: #1a252f;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
            }
            QTabWidget::pane {
                border: 2px solid #34495e;
                background: #2c3e50;
            }
            QTabBar::tab {
                background: #34495e;
                color: white;
                padding: 12px 25px;
                margin-right: 5px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: #3498db;
            }
            QCheckBox {
                color: white;
                font-size: 14px;
            }
            QComboBox {
                background: #34495e;
                color: white;
                border: 1px solid #2c3e50;
                padding: 5px;
                border-radius: 5px;
            }
            QLabel {
                color: white;
            }
        """)
        
    def on_audio_toggle(self, state):
        """Toggle Audio-Transkription"""
        self.model_combo.setEnabled(state == Qt.Checked)
        
    def select_export(self, event):
        """Export-Auswahl Dialog"""
        # Frage ob Ordner oder Datei
        msg = QMessageBox()
        msg.setWindowTitle("Export-Typ auswählen")
        msg.setText("Was möchten Sie auswählen?")
        folder_btn = msg.addButton("📁 Export-Ordner", QMessageBox.ActionRole)
        file_btn = msg.addButton("📄 Nur _chat.txt", QMessageBox.ActionRole)
        msg.addButton("Abbrechen", QMessageBox.RejectRole)
        
        msg.exec()
        
        if msg.clickedButton() == folder_btn:
            # Ordner auswählen
            folder = QFileDialog.getExistingDirectory(
                self,
                "WhatsApp-Export Ordner auswählen",
                "",
                QFileDialog.ShowDirsOnly
            )
            if folder:
                self.export_path = folder
                self.path_label.setText(f"📂 {Path(folder).name}")
                self.analyze_btn.setEnabled(True)
                self.drop_area.setText("✅ Export-Ordner ausgewählt")
                
        elif msg.clickedButton() == file_btn:
            # Datei auswählen
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "WhatsApp _chat.txt auswählen",
                "",
                "Text Files (*chat*.txt);;All Files (*)"
            )
            if file_path:
                self.export_path = file_path
                self.path_label.setText(f"📄 {Path(file_path).name}")
                self.analyze_btn.setEnabled(True)
                self.drop_area.setText("✅ Chat-Datei ausgewählt")
                
    def start_analysis(self):
        """Startet die komplette Analyse"""
        if not self.export_path or not ANALYZER_AVAILABLE:
            return
            
        # UI vorbereiten
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_tabs.setVisible(False)
        
        # Worker Thread starten
        self.analysis_thread = AnalysisThread(
            self.export_path,
            enable_audio=self.audio_checkbox.isChecked(),
            whisper_model=self.model_combo.currentText()
        )
        self.analysis_thread.progress.connect(self.update_progress)
        self.analysis_thread.status.connect(self.update_status)
        self.analysis_thread.finished.connect(self.show_results)
        self.analysis_thread.error.connect(self.show_error)
        self.analysis_thread.start()
        
    def update_progress(self, value):
        """Aktualisiert den Fortschritt"""
        self.progress_bar.setValue(value)
        
    def update_status(self, status):
        """Aktualisiert den Status"""
        self.status_label.setText(status)
        
    def show_results(self, results):
        """Zeigt die kompletten Analyse-Ergebnisse"""
        self.analysis_results = results
        self.progress_bar.setVisible(False)
        self.results_tabs.setVisible(True)
        self.analyze_btn.setEnabled(True)
        
        # Tab 1: Übersicht
        summary = results.get('summary', {})
        risk = summary.get('risk_assessment', {})
        
        overview = f"""
🔍 ANALYSE-ÜBERSICHT
==================

📄 Datei: {results['file_info']['chat_file']}
📂 Media: {'Ja' if results['file_info']['has_media'] else 'Nein'}
📏 Größe: {results['file_info']['size']:,} Bytes

📊 STATISTIKEN
=============
• Text-Länge: {results['marker_analysis']['text_length']:,} Zeichen
• Atomic Marker: {results['marker_analysis']['statistics']['total_atomic_hits']}
• Unique Marker: {results['marker_analysis']['statistics']['unique_atomic_markers']}
• High-Risk Marker: {results['marker_analysis']['statistics']['high_risk_markers']}

🎤 AUDIO-ANALYSE
===============
• Aktiviert: {'Ja' if results['audio_analysis']['enabled'] else 'Nein'}
• Sprachnachrichten: {results['audio_analysis']['transcribed_messages']}
{f"• Qualität: {summary['audio_summary'].get('transcription_quality', 'N/A')}" if summary.get('audio_summary') else ''}

⚠️ RISIKO-BEWERTUNG
==================
• Level: {risk.get('level', 'Unbekannt')}
• Score: {risk.get('score', 0):.1f}/10
• High-Risk Marker: {risk.get('high_risk_markers', 0)}

📋 WICHTIGE BEFUNDE
=================="""
        
        for finding in summary.get('key_findings', []):
            overview += f"\n{finding}"
            
        self.overview_text.setText(overview)
        
        # Tab 2: Audio-Transkriptionen
        audio_text = "🎤 SPRACHNACHRICHTEN-TRANSKRIPTIONEN\n" + "="*40 + "\n\n"
        
        if results['audio_analysis']['transcribed_messages'] > 0:
            for i, audio in enumerate(results['audio_analysis']['audio_details'], 1):
                audio_text += f"{i}. {audio['timestamp']} - {audio['sender']}\n"
                audio_text += f"   📝 Transkription: {audio['transcription']}\n"
                audio_text += f"   💯 Konfidenz: {audio['confidence']:.1%}\n\n"
        else:
            audio_text += "Keine Sprachnachrichten transkribiert.\n"
            
        self.audio_text.setText(audio_text)
        
        # Tab 3: Gefundene Marker
        markers_text = "🎯 GEFUNDENE MARKER\n" + "="*40 + "\n\n"
        
        marker_hits = results['marker_analysis'].get('atomic_hits', [])
        if marker_hits:
            for i, hit in enumerate(marker_hits[:30], 1):  # Erste 30
                markers_text += f"{i}. {hit.marker_id}\n"
                markers_text += f"   📍 Treffer: '{hit.matches[0][:80]}...'\n"
                markers_text += f"   📄 Kontext: ...{hit.context}...\n"
                markers_text += f"   💯 Konfidenz: {hit.confidence:.1%}\n\n"
        else:
            markers_text += "Keine Marker gefunden.\n"
            
        self.markers_text.setText(markers_text)
        
        # Tab 4: Risiko-Bewertung & Empfehlungen
        risk_text = "⚠️ RISIKO-BEWERTUNG & EMPFEHLUNGEN\n" + "="*40 + "\n\n"
        
        risk_text += f"GESAMT-RISIKO: {risk.get('level', 'Unbekannt')} ({risk.get('score', 0):.1f}/10)\n\n"
        
        # Detaillierte Befunde
        if summary.get('key_findings'):
            risk_text += "KRITISCHE BEFUNDE:\n"
            for finding in summary['key_findings']:
                risk_text += f"{finding}\n"
            risk_text += "\n"
        
        # Empfehlungen
        risk_text += "EMPFEHLUNGEN:\n"
        for rec in summary.get('recommendations', []):
            risk_text += f"{rec}\n"
            
        self.risk_text.setText(risk_text)
        
    def show_error(self, error_msg):
        """Zeigt Fehler an"""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        QMessageBox.critical(self, "Fehler", error_msg)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Drag Enter Event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        """Drop Event"""
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        if paths:
            path = Path(paths[0])
            if path.is_dir() or (path.is_file() and 'chat' in path.name):
                self.export_path = str(path)
                self.path_label.setText(f"{'📂' if path.is_dir() else '📄'} {path.name}")
                self.analyze_btn.setEnabled(True)
                self.drop_area.setText("✅ Export ausgewählt")

def main():
    """Hauptfunktion"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show window
    window = MarkerEngineGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
