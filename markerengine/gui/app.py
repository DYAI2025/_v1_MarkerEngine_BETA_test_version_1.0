"""
MarkerEngine GUI - Mit Kimi K2 Integration
"""
import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTextEdit, QProgressBar,
    QTabWidget, QCheckBox, QLineEdit, QGroupBox
)
from PySide6.QtCore import Qt, QThread, Signal
import json
from pathlib import Path

class AnalysisThread(QThread):
    progress = Signal(int)
    finished = Signal(dict)
    error = Signal(str)
    status = Signal(str)
    
    def __init__(self, filepath, use_ai=True):
        super().__init__()
        self.filepath = filepath
        self.use_ai = use_ai
        
    def run(self):
        try:
            self.status.emit('Datei wird gelesen...')
            self.progress.emit(20)
            
            # Read file
            with open(self.filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                
            self.status.emit('Analysiere mit Regeln...')
            self.progress.emit(50)
            
            # Analyze
            from ..core.analyzer import MarkerAnalyzer
            analyzer = MarkerAnalyzer()
            result = analyzer.analyze(text, use_ai=self.use_ai)
            
            if self.use_ai and os.getenv('KIMI_API_KEY'):
                self.status.emit('KI-Analyse läuft...')
                self.progress.emit(80)
            
            self.progress.emit(100)
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))

class MarkerEngineWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MarkerEngine v1.0 - WhatsApp Analyse mit KI')
        self.setMinimumSize(1000, 700)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel('🔍 MarkerEngine')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 32px; font-weight: bold; margin: 20px;')
        layout.addWidget(title)
        
        # API Key Group
        api_group = QGroupBox('Kimi K2 API Konfiguration')
        api_layout = QHBoxLayout()
        
        api_layout.addWidget(QLabel('API Key:'))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText('sk-... (optional für KI-Analyse)')
        self.api_key_input.setText(os.getenv('KIMI_API_KEY', ''))
        api_layout.addWidget(self.api_key_input)
        
        self.save_key_btn = QPushButton('Speichern')
        self.save_key_btn.clicked.connect(self.save_api_key)
        api_layout.addWidget(self.save_key_btn)
        
        self.ai_checkbox = QCheckBox('KI-Analyse aktivieren')
        self.ai_checkbox.setChecked(bool(os.getenv('KIMI_API_KEY')))
        api_layout.addWidget(self.ai_checkbox)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # File button
        self.file_btn = QPushButton('📁 WhatsApp-Chat auswählen (.txt)')
        self.file_btn.clicked.connect(self.select_file)
        self.file_btn.setStyleSheet('padding: 15px; font-size: 18px; font-weight: bold;')
        layout.addWidget(self.file_btn)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)
        
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.hide()
        layout.addWidget(self.status_label)
        
        # Results Tabs
        self.tabs = QTabWidget()
        
        # Rule-based results
        self.rule_results = QTextEdit()
        self.rule_results.setReadOnly(True)
        self.tabs.addTab(self.rule_results, '📋 Regel-Analyse')
        
        # AI results
        self.ai_results = QTextEdit()
        self.ai_results.setReadOnly(True)
        self.tabs.addTab(self.ai_results, '🤖 KI-Analyse')
        
        # Combined insights
        self.insights = QTextEdit()
        self.insights.setReadOnly(True)
        self.tabs.addTab(self.insights, '💡 Insights')
        
        layout.addWidget(self.tabs)
        
        # Dark theme
        self.setStyleSheet('''
            QMainWindow { background-color: #2b2b2b; }
            QWidget { background-color: #2b2b2b; color: #ffffff; }
            QPushButton { 
                background-color: #3c3c3c; 
                border: 1px solid #555; 
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #4c4c4c; }
            QTextEdit { 
                background-color: #3c3c3c; 
                border: 1px solid #555;
                border-radius: 5px;
            }
            QProgressBar { 
                border: 1px solid #555; 
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk { 
                background-color: #4CAF50;
                border-radius: 5px;
            }
            QTabWidget::pane { 
                background-color: #3c3c3c;
                border: 1px solid #555;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4c4c4c;
            }
            QGroupBox {
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 3px;
            }
        ''')
        
    def save_api_key(self):
        key = self.api_key_input.text().strip()
        if key:
            os.environ['KIMI_API_KEY'] = key
            self.ai_checkbox.setChecked(True)
            self.status_label.setText('✅ API Key gespeichert')
            self.status_label.show()
        else:
            if 'KIMI_API_KEY' in os.environ:
                del os.environ['KIMI_API_KEY']
            self.ai_checkbox.setChecked(False)
            self.status_label.setText('❌ API Key entfernt')
            self.status_label.show()
            
    def select_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, 
            'WhatsApp-Export wählen', 
            '', 
            'Text Files (*.txt);;All Files (*)'
        )
        if filepath:
            self.analyze_file(filepath)
            
    def analyze_file(self, filepath):
        self.progress.show()
        self.status_label.show()
        self.tabs.setCurrentIndex(0)
        
        # Clear previous results
        self.rule_results.clear()
        self.ai_results.clear()
        self.insights.clear()
        
        use_ai = self.ai_checkbox.isChecked() and bool(os.getenv('KIMI_API_KEY'))
        
        self.thread = AnalysisThread(filepath, use_ai)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.status.connect(self.status_label.setText)
        self.thread.finished.connect(self.show_results)
        self.thread.error.connect(self.show_error)
        self.thread.start()
        
    def show_results(self, results):
        self.progress.hide()
        self.status_label.hide()
        
        # Format rule-based results
        output = '=== REGEL-BASIERTE ANALYSE ===\n\n'
        
        stats = results.get('stats', {})
        text_stats = stats.get('text', {})
        marker_stats = stats.get('markers', {})
        
        output += f"📊 STATISTIKEN:\n"
        output += f"  Wörter: {text_stats.get('total_words', 0):,}\n"
        output += f"  Zeichen: {text_stats.get('total_chars', 0):,}\n"
        output += f"  Marker gefunden: {marker_stats.get('total_hits', 0)}\n\n"
        
        if marker_stats.get('by_category'):
            output += '📍 KATEGORIEN:\n'
            for cat, count in sorted(marker_stats['by_category'].items(), key=lambda x: x[1], reverse=True):
                output += f'  • {cat}: {count} Treffer\n'
            output += '\n'
            
        hits = results.get('marker_hits', [])
        if hits:
            output += f'🎯 TOP MARKER (erste 15):\n'
            for hit in hits[:15]:
                output += f"  • \"{hit['text']}\" ({hit['category']})\n"
                output += f"    Kontext: ...{hit.get('context', '')[20:-20]}...\n\n"
                
        self.rule_results.setText(output)
        
        # AI results
        ai_output = '=== KI-ANALYSE (Kimi K2) ===\n\n'
        
        if results.get('ai_analysis'):
            ai_data = results['ai_analysis']
            
            if isinstance(ai_data, dict):
                if 'summary' in ai_data:
                    ai_output += f"📝 ZUSAMMENFASSUNG:\n{ai_data['summary']}\n\n"
                    
                if 'sentiment' in ai_data:
                    sent = ai_data['sentiment']
                    ai_output += f"😊 STIMMUNG: {sent.get('overall', 'unbekannt')} (Score: {sent.get('score', 0):.2f})\n\n"
                    
                if 'key_topics' in ai_data:
                    ai_output += '🏷️ HAUPTTHEMEN:\n'
                    for topic in ai_data['key_topics']:
                        ai_output += f'  • {topic}\n'
                    ai_output += '\n'
                    
                if 'risk_indicators' in ai_data:
                    ai_output += '⚠️ RISIKO-INDIKATOREN:\n'
                    for risk in ai_data['risk_indicators']:
                        severity_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(risk.get('severity'), '⚪')
                        ai_output += f"  {severity_emoji} {risk.get('type', 'Risiko')}: {risk.get('description', '')}\n"
                    ai_output += '\n'
                    
                if 'communication_patterns' in ai_data:
                    ai_output += '🔄 KOMMUNIKATIONSMUSTER:\n'
                    for pattern in ai_data['communication_patterns']:
                        ai_output += f'  • {pattern}\n'
            else:
                ai_output += str(ai_data)
        else:
            ai_output += '❌ Keine KI-Analyse verfügbar.\n\n'
            ai_output += 'Mögliche Gründe:\n'
            ai_output += '  • Kein API Key konfiguriert\n'
            ai_output += '  • API nicht erreichbar\n'
            ai_output += '  • Rate Limit erreicht\n'
            
        self.ai_results.setText(ai_output)
        
        # Combined insights
        insights_output = '=== KOMBINIERTE INSIGHTS ===\n\n'
        
        insights = results.get('insights', [])
        if insights:
            # Group by source
            rule_insights = [i for i in insights if i.get('source') == 'rules']
            ai_insights = [i for i in insights if i.get('source') == 'ai']
            
            if rule_insights:
                insights_output += '📋 REGEL-BASIERTE INSIGHTS:\n'
                for insight in rule_insights:
                    severity_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(insight.get('severity'), '⚪')
                    insights_output += f"\n{severity_emoji} {insight['title']}\n"
                    insights_output += f"   {insight['description']}\n"
                    
            if ai_insights:
                insights_output += '\n🤖 KI-INSIGHTS:\n'
                for insight in ai_insights:
                    severity_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(insight.get('severity'), '⚪')
                    insights_output += f"\n{severity_emoji} {insight['title']}\n"
                    insights_output += f"   {insight['description']}\n"
        else:
            insights_output += 'Keine besonderen Muster gefunden.'
            
        self.insights.setText(insights_output)
        
        # Switch to appropriate tab
        if results.get('ai_analysis'):
            self.tabs.setCurrentIndex(2)  # Show insights
        else:
            self.tabs.setCurrentIndex(0)  # Show rules
        
    def show_error(self, error):
        self.progress.hide()
        self.status_label.setText(f'❌ Fehler: {error}')
        self.rule_results.setText(f'❌ Fehler bei der Analyse:\n\n{error}')

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('MarkerEngine')
    
    window = MarkerEngineWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
