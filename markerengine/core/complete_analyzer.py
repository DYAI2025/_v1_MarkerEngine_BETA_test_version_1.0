"""
MarkerEngine Complete Analyzer - Mit Whisper Integration
Kombiniert Marker-Analyse mit Audio-Transkription
"""
import os
import yaml
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# Import unsere Module
try:
    from .whisper_integration import WhisperTranscriber, WhatsAppAudioProcessor
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️ Whisper nicht verfügbar - Audio-Transkription deaktiviert")

from .real_analyzer import RealMarkerAnalyzer, MarkerResult

logger = logging.getLogger(__name__)

class CompleteWhatsAppAnalyzer:
    """
    Vollständiger Analyzer mit:
    - Whisper v3 Audio-Transkription
    - Echte Marker-Analyse
    - Integration beider Systeme
    """
    
    def __init__(self, 
                 markers_path: str = None,
                 whisper_model: str = "large-v3",
                 enable_audio: bool = True):
        """
        Initialisiert den kompletten Analyzer
        
        Args:
            markers_path: Pfad zu den Marker-YAML-Dateien
            whisper_model: Whisper Model Size
            enable_audio: Audio-Transkription aktivieren
        """
        # Marker Analyzer
        self.marker_analyzer = RealMarkerAnalyzer(markers_path)
        
        # Whisper Transcriber (optional)
        self.whisper_enabled = enable_audio and WHISPER_AVAILABLE
        if self.whisper_enabled:
            try:
                self.transcriber = WhisperTranscriber(model_size=whisper_model)
                self.audio_processor = WhatsAppAudioProcessor(self.transcriber)
                logger.info("✅ Whisper v3 Audio-Transkription aktiviert")
            except Exception as e:
                logger.error(f"❌ Whisper konnte nicht geladen werden: {e}")
                self.whisper_enabled = False
        else:
            logger.info("ℹ️ Audio-Transkription deaktiviert")
    
    def analyze_whatsapp_export(self, 
                               export_path: str,
                               process_audio: bool = True) -> Dict[str, Any]:
        """
        Analysiert einen kompletten WhatsApp-Export
        
        Args:
            export_path: Pfad zum Export (Datei oder Ordner)
            process_audio: Audio-Dateien transkribieren
            
        Returns:
            Vollständige Analyse mit Audio + Markern
        """
        export_path = Path(export_path)
        
        # Finde Chat-Datei
        if export_path.is_file():
            chat_file = export_path
            media_folder = export_path.parent
        else:
            # Suche _chat.txt im Ordner
            chat_files = list(export_path.glob("*chat*.txt"))
            if not chat_files:
                raise FileNotFoundError(f"Keine Chat-Datei gefunden in {export_path}")
            chat_file = chat_files[0]
            media_folder = export_path
        
        # Phase 1: Audio-Transkription (falls aktiviert)
        enhanced_chat = None
        audio_messages = []
        
        if process_audio and self.whisper_enabled:
            logger.info("🎤 Starte Audio-Transkription...")
            try:
                enhanced_chat, audio_messages = self.audio_processor.process_chat_with_audio(
                    str(chat_file),
                    str(media_folder)
                )
                logger.info(f"✅ {len(audio_messages)} Sprachnachrichten transkribiert")
            except Exception as e:
                logger.error(f"Fehler bei Audio-Transkription: {e}")
                enhanced_chat = None
        
        # Falls keine Audio-Transkription, nutze Original-Chat
        if enhanced_chat is None:
            with open(chat_file, 'r', encoding='utf-8') as f:
                enhanced_chat = f.read()
        
        # Phase 2: Marker-Analyse auf dem erweiterten Chat
        logger.info("🔍 Starte Marker-Analyse...")
        marker_results = self.marker_analyzer.analyze_text(enhanced_chat)
        
        # Phase 3: Kombiniere Ergebnisse
        complete_results = {
            'timestamp': datetime.now().isoformat(),
            'file_info': {
                'chat_file': str(chat_file),
                'media_folder': str(media_folder),
                'size': os.path.getsize(chat_file),
                'has_media': len(list(media_folder.glob("*.opus"))) > 0 or 
                            len(list(media_folder.glob("*.mp4"))) > 0
            },
            'audio_analysis': {
                'enabled': self.whisper_enabled and process_audio,
                'transcribed_messages': len(audio_messages),
                'audio_details': [
                    {
                        'timestamp': msg.timestamp,
                        'sender': msg.sender,
                        'transcription': msg.transcription,
                        'confidence': msg.confidence
                    } for msg in audio_messages
                ] if audio_messages else []
            },
            'marker_analysis': marker_results,
            'enhanced_chat': enhanced_chat,  # Der erweiterte Chat mit Transkriptionen
            'summary': self._generate_summary(marker_results, audio_messages)
        }
        
        return complete_results
    
    def _generate_summary(self, 
                         marker_results: Dict[str, Any], 
                         audio_messages: List) -> Dict[str, Any]:
        """Generiert eine Zusammenfassung der Analyse"""
        
        # Risk Assessment
        risk_level = "Niedrig"
        if marker_results['risk_score'] >= 7:
            risk_level = "Hoch"
        elif marker_results['risk_score'] >= 4:
            risk_level = "Mittel"
        
        # Audio Summary
        audio_summary = {}
        if audio_messages:
            total_audio = len(audio_messages)
            avg_confidence = sum(m.confidence for m in audio_messages) / total_audio
            audio_summary = {
                'total_voice_messages': total_audio,
                'average_confidence': round(avg_confidence, 2),
                'transcription_quality': 'Gut' if avg_confidence > 0.8 else 'Mittel' if avg_confidence > 0.6 else 'Niedrig'
            }
        
        # Key Findings
        key_findings = []
        
        # Prüfe auf kritische Marker
        critical_markers = ['SCAM', 'FRAUD', 'MANIPULATION', 'GASLIGHTING', 'MONEY', 'CRISIS']
        for hit in marker_results.get('atomic_hits', []):
            for critical in critical_markers:
                if critical in hit.marker_id.upper():
                    key_findings.append(f"⚠️ {critical}-Indikator gefunden")
                    break
        
        return {
            'risk_assessment': {
                'level': risk_level,
                'score': marker_results['risk_score'],
                'high_risk_markers': marker_results['statistics'].get('high_risk_markers', 0)
            },
            'audio_summary': audio_summary,
            'key_findings': list(set(key_findings)),  # Unique findings
            'recommendations': self._generate_recommendations(risk_level, key_findings)
        }
    
    def _generate_recommendations(self, risk_level: str, findings: List[str]) -> List[str]:
        """Generiert Empfehlungen basierend auf der Analyse"""
        recommendations = []
        
        if risk_level == "Hoch":
            recommendations.append("🚨 Hohe Vorsicht geboten - mehrere Risiko-Indikatoren gefunden")
            recommendations.append("📋 Dokumentieren Sie verdächtige Nachrichten")
            recommendations.append("🛡️ Überprüfen Sie Identität des Gesprächspartners")
        
        if any("MONEY" in f or "CRISIS" in f for f in findings):
            recommendations.append("💰 Seien Sie vorsichtig bei Geldanfragen")
            recommendations.append("✅ Verifizieren Sie Notfälle über andere Kanäle")
        
        if any("MANIPULATION" in f or "GASLIGHTING" in f for f in findings):
            recommendations.append("🧠 Achten Sie auf emotionale Manipulation")
            recommendations.append("👥 Sprechen Sie mit vertrauten Personen")
        
        if not recommendations:
            recommendations.append("✅ Keine kritischen Muster erkannt")
            recommendations.append("📊 Regelmäßige Überprüfung empfohlen")
        
        return recommendations

def analyze_whatsapp_complete(export_path: str, 
                            enable_audio: bool = True,
                            whisper_model: str = "large-v3") -> Dict[str, Any]:
    """
    Haupt-Funktion für komplette WhatsApp-Analyse
    
    Args:
        export_path: Pfad zum WhatsApp-Export
        enable_audio: Audio-Transkription aktivieren
        whisper_model: Whisper Model (tiny, base, small, medium, large, large-v3)
        
    Returns:
        Vollständige Analyse-Ergebnisse
    """
    print("🚀 Starte komplette WhatsApp-Analyse...")
    print(f"📁 Export: {export_path}")
    print(f"🎤 Audio: {'Aktiviert' if enable_audio else 'Deaktiviert'}")
    
    analyzer = CompleteWhatsAppAnalyzer(
        whisper_model=whisper_model,
        enable_audio=enable_audio
    )
    
    results = analyzer.analyze_whatsapp_export(export_path)
    
    print("\n✅ Analyse abgeschlossen!")
    print(f"📊 Risk Score: {results['summary']['risk_assessment']['score']:.1f}/10")
    print(f"🎯 Marker gefunden: {results['marker_analysis']['statistics']['total_atomic_hits']}")
    
    if results['audio_analysis']['enabled']:
        print(f"🎤 Audio transkribiert: {results['audio_analysis']['transcribed_messages']}")
    
    return results

# Beispiel-Nutzung
if __name__ == "__main__":
    # Test-Pfad
    test_export = "/path/to/whatsapp/export"
    
    try:
        results = analyze_whatsapp_complete(
            test_export,
            enable_audio=True,
            whisper_model="large-v3"
        )
        
        # Speichere Ergebnisse
        with open("analysis_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
        print("\n📄 Ergebnisse gespeichert in: analysis_results.json")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
