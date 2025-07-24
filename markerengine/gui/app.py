"""
MarkerEngine GUI - Simplified Working Version
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit, QProgressBar
from PySide6.QtCore import Qt, QThread, Signal
import json
from pathlib import Path

class AnalysisThread(QThread):
    progress = Signal(int)
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        
    def run(self):
        try:
            self.progress.emit(20)
            
            # Read file
            with open(self.filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                
            self.progress.emit(50)
            
            # Analyze
            from ..core.analyzer import MarkerAnalyzer
            analyzer = MarkerAnalyzer()
            result = analyzer.analyze(text)
            
            self.progress.emit(100)
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))

class MarkerEngineWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MarkerEngine v1.0')
        self.setMinimumSize(800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel('🔍 MarkerEngine')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 32px; font-weight: bold; margin: 20px;')
        layout.addWidget(title)
        
        # File button
        self.file_btn = QPushButton('WhatsApp-Chat auswählen (.txt)')
        self.file_btn.clicked.connect(self.select_file)
        self.file_btn.setStyleSheet('padding: 10px; font-size: 16px;')
        layout.addWidget(self.file_btn)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)
        
        # Results
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        layout.addWidget(self.results)
        
        # Dark theme
        self.setStyleSheet('''
            QMainWindow { background-color: #2b2b2b; }
            QWidget { background-color: #2b2b2b; color: #ffffff; }
            QPushButton { background-color: #3c3c3c; border: 1px solid #555; }
            QPushButton:hover { background-color: #4c4c4c; }
            QTextEdit { background-color: #3c3c3c; border: 1px solid #555; }
            QProgressBar { border: 1px solid #555; }
            QProgressBar::chunk { background-color: #4CAF50; }
        ''')
        
    def select_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, 'WhatsApp-Export wählen', '', 'Text Files (*.txt)')
        if filepath:
            self.analyze_file(filepath)
            
    def analyze_file(self, filepath):
        self.progress.show()
        self.results.clear()
        
        self.thread = AnalysisThread(filepath)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.finished.connect(self.show_results)
        self.thread.error.connect(self.show_error)
        self.thread.start()
        
    def show_results(self, results):
        self.progress.hide()
        
        # Format results
        output = '=== ANALYSE ERGEBNISSE ===\n\n'
        
        stats = results.get('stats', {})
        text_stats = stats.get('text', {})
        marker_stats = stats.get('markers', {})
        
        output += f"Wörter: {text_stats.get('total_words', 0)}\n"
        output += f"Zeichen: {text_stats.get('total_chars', 0)}\n"
        output += f"Marker gefunden: {marker_stats.get('total_hits', 0)}\n\n"
        
        if marker_stats.get('by_category'):
            output += 'KATEGORIEN:\n'
            for cat, count in marker_stats['by_category'].items():
                output += f'  {cat}: {count} Treffer\n'
            output += '\n'
            
        hits = results.get('marker_hits', [])
        if hits:
            output += f'TOP MARKER (erste 10):\n'
            for hit in hits[:10]:
                output += f"  • {hit['text']} ({hit['category']})\n"
                
        insights = results.get('insights', [])
        if insights:
            output += '\nINSIGHTS:\n'
            for insight in insights:
                output += f"  • {insight['title']}: {insight['description']}\n"
                
        self.results.setText(output)
        
    def show_error(self, error):
        self.progress.hide()
        self.results.setText(f'❌ Fehler: {error}')

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('MarkerEngine')
    
    window = MarkerEngineWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
