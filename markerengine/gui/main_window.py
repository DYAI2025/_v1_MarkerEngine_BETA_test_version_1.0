"""
MarkerEngine GUI - Mit echten Markern
"""
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QProgressBar, QTabWidget, QFileDialog, QMessageBox,
                             QGroupBox, QLineEdit, QCheckBox)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPalette, QColor, QDragEnterEvent, QDropEvent

# Füge den Pfad zum markerengine Modul hinzu
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from markerengine.core.real_analyzer import RealMarkerAnalyzer, analyze_whatsapp_chat
except ImportError:
    print("Warning: Could not import real_analyzer, using mock")
    RealMarkerAnalyzer = None

class AnalysisThread(QThread):
    """Worker Thread für die Analyse"""
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        """Führt die Analyse aus"""
        try:
            self.status.emit("🔍 Starte Analyse...")
            self.progress.emit(10)
            
            # Verwende den echten Analyzer
            results = analyze_whatsapp_chat(self.file_path)
            
            self.progress.emit(100)
            self.status.emit("✅ Analyse abgeschlossen!")
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(f"Fehler bei der Analyse: {str(e)}")

class MarkerEngineGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.analysis_results = None
        self.init_ui()
        
    def init_ui(self):
        """Initialisiert die UI"""
        self.setWindowTitle("🔍 MarkerEngine - Mit echten Markern")
        self.setGeometry(100, 100, 1200, 800)
        
        # Haupt-Widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Header
        header = QLabel("MarkerEngine - WhatsApp Chat Analyse")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
                background: #2c3e50;
                color: white;
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(header)
        
        # File Selection Area
        file_group = QGroupBox("Datei auswählen")
        file_layout = QVBoxLayout()
        
        # Drag & Drop Area
        self.drop_area = QLabel("📁 WhatsApp-Chat hier ablegen\noder klicken zum Auswählen")
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
        self.drop_area.mousePressEvent = self.select_file
        file_layout.addWidget(self.drop_area)
        
        # Selected File Label
        self.file_label = QLabel("Keine Datei ausgewählt")
        self.file_label.setAlignment(Qt.AlignCenter)
        file_layout.addWidget(self.file_label)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # Analyze Button
        self.analyze_btn = QPushButton("🚀 Analyse starten")
        self.analyze_btn.setMinimumHeight(50)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background: #27ae60;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: #229954;
            }
            QPushButton:disabled {
                background: #95a5a6;
            }
        """)
        main_layout.addWidget(self.analyze_btn)
        
        # Progress Area
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
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
        
        # Tab 2: Gefundene Marker
        markers_tab = QWidget()
        markers_layout = QVBoxLayout(markers_tab)
        self.markers_text = QTextEdit()
        self.markers_text.setReadOnly(True)
        markers_layout.addWidget(self.markers_text)
        self.results_tabs.addTab(markers_tab, "🎯 Gefundene Marker")
        
        # Tab 3: Risiko-Bewertung
        risk_tab = QWidget()
        risk_layout = QVBoxLayout(risk_tab)
        self.risk_text = QTextEdit()
        self.risk_text.setReadOnly(True)
        risk_layout.addWidget(self.risk_text)
        self.results_tabs.addTab(risk_tab, "⚠️ Risiko-Bewertung")
        
        main_layout.addWidget(self.results_tabs)
        
        # Apply Dark Theme
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
                padding-top: 10px;
                margin-top: 10px;
                background: #34495e;
            }
            QGroupBox::title {
                padding: 5px;
                background: #2c3e50;
                border-radius: 5px;
            }
            QTextEdit {
                background: #34495e;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            QTabWidget::pane {
                border: 2px solid #34495e;
                background: #2c3e50;
            }
            QTabBar::tab {
                background: #34495e;
                color: white;
                padding: 10px 20px;
                margin-right: 5px;
            }
            QTabBar::tab:selected {
                background: #3498db;
            }
        """)
        
    def select_file(self, event):
        """Datei-Auswahl Dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "WhatsApp-Chat auswählen",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"📄 {Path(file_path).name}")
            self.analyze_btn.setEnabled(True)
            self.drop_area.setText("✅ Datei ausgewählt")
            
    def start_analysis(self):
        """Startet die Analyse"""
        if not self.file_path:
            return
            
        # UI vorbereiten
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_tabs.setVisible(False)
        
        # Worker Thread starten
        self.analysis_thread = AnalysisThread(self.file_path)
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
        """Zeigt die Analyse-Ergebnisse"""
        self.analysis_results = results
        self.progress_bar.setVisible(False)
        self.results_tabs.setVisible(True)
        self.analyze_btn.setEnabled(True)
        
        # Tab 1: Übersicht
        overview = f"""
🔍 ANALYSE-ÜBERSICHT
==================

📄 Datei: {results['file_info']['name']}
📏 Größe: {results['file_info']['size']:,} Bytes
📅 Analysiert: {results['file_info']['analyzed_at']}

📊 STATISTIKEN
=============
• Text-Länge: {results['text_length']:,} Zeichen
• Atomic Marker gefunden: {results['statistics']['total_atomic_hits']}
• Unique Marker: {results['statistics']['unique_atomic_markers']}
• High-Risk Marker: {results['statistics']['high_risk_markers']}

⚠️ RISIKO-SCORE: {results['risk_score']:.1f}/10

{'🟢 Niedrig' if results['risk_score'] < 3 else '🟡 Mittel' if results['risk_score'] < 7 else '🔴 Hoch'}
        """
        self.overview_text.setText(overview)
        
        # Tab 2: Gefundene Marker
        markers_text = "🎯 GEFUNDENE MARKER\n==================\n\n"
        
        if results['atomic_hits']:
            for i, hit in enumerate(results['atomic_hits'][:20], 1):  # Erste 20
                markers_text += f"{i}. {hit.marker_id}\n"
                markers_text += f"   📍 Gefunden: '{hit.matches[0][:60]}...'\n"
                markers_text += f"   📄 Kontext: ...{hit.context}...\n"
                markers_text += f"   💯 Konfidenz: {hit.confidence:.1%}\n\n"
        else:
            markers_text += "Keine Marker gefunden.\n"
            
        self.markers_text.setText(markers_text)
        
        # Tab 3: Risiko-Bewertung
        risk_text = "⚠️ RISIKO-BEWERTUNG\n==================\n\n"
        
        # Prüfe auf spezifische Risiko-Marker
        risk_markers = {
            'SCAM': "🚨 Betrugs-Indikatoren",
            'MANIPULATION': "🎭 Manipulations-Muster",
            'GASLIGHTING': "🌀 Gaslighting-Verhalten",
            'MONEY': "💰 Geld-bezogene Anfragen",
            'CRISIS': "🆘 Krisen-Muster",
            'BLAME': "👉 Schuldzuweisungen"
        }
        
        found_risks = []
        for hit in results['atomic_hits']:
            for risk_key, risk_name in risk_markers.items():
                if risk_key in hit.marker_id.upper():
                    if risk_name not in found_risks:
                        found_risks.append(risk_name)
                        risk_text += f"\n{risk_name}:\n"
                        risk_text += f"  - Marker: {hit.marker_id}\n"
                        risk_text += f"  - Beispiel: '{hit.matches[0][:50]}...'\n"
        
        if not found_risks:
            risk_text += "✅ Keine spezifischen Risiko-Marker gefunden.\n"
        else:
            risk_text += f"\n\n⚠️ WARNUNG: {len(found_risks)} Risiko-Kategorien identifiziert!"
            
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
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and files[0].endswith('.txt'):
            self.file_path = files[0]
            self.file_label.setText(f"📄 {Path(files[0]).name}")
            self.analyze_btn.setEnabled(True)
            self.drop_area.setText("✅ Datei ausgewählt")

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
