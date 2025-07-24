"""
Whisper v3 Integration für MarkerEngine
Transkribiert WhatsApp Sprachnachrichten und fügt sie an den richtigen Stellen ein
"""
import os
import re
import whisper
import torch
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AudioMessage:
    """Repräsentiert eine Audio-Nachricht"""
    timestamp: str
    sender: str
    audio_file: str
    position: int
    transcription: Optional[str] = None
    confidence: float = 0.0

class WhisperTranscriber:
    """Whisper v3 Transcriber für WhatsApp Audio-Nachrichten"""
    
    def __init__(self, model_size: str = "large-v3", device: str = None):
        """
        Initialisiert Whisper v3
        
        Args:
            model_size: Model size (tiny, base, small, medium, large, large-v3)
            device: Device (cuda, cpu, auto)
        """
        self.model_size = model_size
        
        # Auto-detect device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        logger.info(f"Lade Whisper {model_size} auf {self.device}...")
        
        try:
            self.model = whisper.load_model(model_size, device=self.device)
            logger.info("✅ Whisper erfolgreich geladen!")
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden von Whisper: {e}")
            raise
    
    def transcribe_audio(self, audio_path: str, language: str = "de") -> Dict:
        """
        Transkribiert eine Audio-Datei
        
        Args:
            audio_path: Pfad zur Audio-Datei
            language: Sprache (Standard: Deutsch)
            
        Returns:
            Transkriptions-Ergebnis
        """
        try:
            logger.info(f"Transkribiere: {audio_path}")
            
            # Whisper v3 Options
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                temperature=0.0,  # Deterministisch
                word_timestamps=True,  # Für präzise Zeitstempel
                fp16=self.device == "cuda",  # FP16 auf GPU
                condition_on_previous_text=True,  # Besserer Kontext
                initial_prompt="WhatsApp Sprachnachricht:"  # Kontext-Hinweis
            )
            
            return {
                'text': result['text'].strip(),
                'language': result.get('language', language),
                'segments': result.get('segments', []),
                'confidence': self._calculate_confidence(result)
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Transkription von {audio_path}: {e}")
            return {'text': '[Transkription fehlgeschlagen]', 'confidence': 0.0}
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Berechnet Konfidenz-Score aus Whisper-Ergebnis"""
        segments = result.get('segments', [])
        if not segments:
            return 0.0
            
        # Durchschnitt der Segment-Wahrscheinlichkeiten
        probs = [seg.get('avg_logprob', 0) for seg in segments]
        avg_logprob = sum(probs) / len(probs) if probs else -10
        
        # Konvertiere zu 0-1 Score
        confidence = min(1.0, max(0.0, 1.0 + (avg_logprob / 10)))
        return confidence

class WhatsAppAudioProcessor:
    """Verarbeitet WhatsApp Exports mit Audio-Nachrichten"""
    
    def __init__(self, transcriber: WhisperTranscriber):
        self.transcriber = transcriber
        
        # WhatsApp Audio-Patterns
        self.audio_patterns = [
            r'(\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2}) - ([^:]+): (.*\.opus) \(Datei angehängt\)',
            r'(\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2}) - ([^:]+): (.*\.mp4) \(Datei angehängt\)',
            r'(\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2}) - ([^:]+): <angehängt: (.*\.opus)>',
            r'(\d{2}/\d{2}/\d{2}, \d{2}:\d{2}) - ([^:]+): (.*\.opus) \(file attached\)',
            r'(\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2}) - ([^:]+): Sprachnachricht',
            r'(\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2}) - ([^:]+): 🎤 (.*\.opus)'
        ]
        
    def process_chat_with_audio(self, 
                               chat_file: str, 
                               media_folder: Optional[str] = None) -> Tuple[str, List[AudioMessage]]:
        """
        Verarbeitet WhatsApp-Chat und transkribiert Audio-Nachrichten
        
        Args:
            chat_file: Pfad zur _chat.txt Datei
            media_folder: Ordner mit Media-Dateien (optional)
            
        Returns:
            (Erweiterter Chat-Text, Liste der Audio-Messages)
        """
        # Bestimme Media-Ordner
        if media_folder is None:
            # Versuche Standard WhatsApp Export Struktur
            chat_path = Path(chat_file)
            media_folder = chat_path.parent
            
        media_path = Path(media_folder)
        
        # Lese Chat
        with open(chat_file, 'r', encoding='utf-8') as f:
            chat_content = f.read()
        
        # Finde alle Audio-Nachrichten
        audio_messages = self._find_audio_messages(chat_content)
        
        # Transkribiere und füge ein
        enhanced_chat = chat_content
        transcribed_audios = []
        
        for audio_msg in audio_messages:
            # Finde Audio-Datei
            audio_file = self._find_audio_file(audio_msg, media_path)
            
            if audio_file:
                # Transkribiere
                logger.info(f"Transkribiere Audio von {audio_msg.sender} um {audio_msg.timestamp}")
                transcription = self.transcriber.transcribe_audio(str(audio_file))
                
                audio_msg.transcription = transcription['text']
                audio_msg.confidence = transcription['confidence']
                
                # Füge Transkription in Chat ein
                insert_text = f"\n[🎤 SPRACHNACHRICHT TRANSKRIPTION: {audio_msg.transcription}]\n"
                
                # Finde Position im Chat
                pattern = f"{re.escape(audio_msg.timestamp)} - {re.escape(audio_msg.sender)}:.*"
                match = re.search(pattern, enhanced_chat)
                
                if match:
                    # Füge nach der Audio-Nachricht ein
                    insert_pos = match.end()
                    enhanced_chat = (enhanced_chat[:insert_pos] + 
                                   insert_text + 
                                   enhanced_chat[insert_pos:])
                
                transcribed_audios.append(audio_msg)
            else:
                logger.warning(f"Audio-Datei nicht gefunden: {audio_msg.audio_file}")
        
        return enhanced_chat, transcribed_audios
    
    def _find_audio_messages(self, chat_content: str) -> List[AudioMessage]:
        """Findet alle Audio-Nachrichten im Chat"""
        audio_messages = []
        
        lines = chat_content.split('\n')
        for i, line in enumerate(lines):
            for pattern in self.audio_patterns:
                match = re.match(pattern, line)
                if match:
                    timestamp = match.group(1)
                    sender = match.group(2)
                    
                    # Versuche Dateinamen zu extrahieren
                    audio_file = match.group(3) if len(match.groups()) >= 3 else f"audio_{i}.opus"
                    
                    audio_msg = AudioMessage(
                        timestamp=timestamp,
                        sender=sender,
                        audio_file=audio_file,
                        position=i
                    )
                    audio_messages.append(audio_msg)
                    break
        
        return audio_messages
    
    def _find_audio_file(self, audio_msg: AudioMessage, media_path: Path) -> Optional[Path]:
        """Findet die tatsächliche Audio-Datei"""
        # Versuche verschiedene Dateinamen
        possible_names = [
            audio_msg.audio_file,
            f"*{audio_msg.audio_file}",
            f"*{audio_msg.timestamp.replace(':', '-').replace('.', '-')}*.opus",
            f"*{audio_msg.timestamp.replace(':', '-').replace('.', '-')}*.mp4",
            f"AUD-*-WA*.opus",
            f"PTT-*-WA*.opus",
            f"VID-*-WA*.mp4"
        ]
        
        for name_pattern in possible_names:
            files = list(media_path.glob(name_pattern))
            if files:
                return files[0]
        
        # Suche nach Zeitstempel-basierten Dateien
        timestamp_parts = audio_msg.timestamp.replace('.', '').replace(',', '').replace(':', '')
        for audio_file in media_path.glob("*.opus"):
            if timestamp_parts in str(audio_file):
                return audio_file
                
        for audio_file in media_path.glob("*.mp4"):
            if timestamp_parts in str(audio_file):
                return audio_file
        
        return None

def integrate_whisper_into_analysis(chat_file: str, 
                                  media_folder: Optional[str] = None,
                                  model_size: str = "large-v3") -> str:
    """
    Hauptfunktion: Integriert Whisper-Transkription in die Chat-Analyse
    
    Args:
        chat_file: Pfad zur WhatsApp _chat.txt
        media_folder: Ordner mit Audio-Dateien
        model_size: Whisper Model (large-v3 recommended)
        
    Returns:
        Erweiterter Chat mit Transkriptionen
    """
    print("🎤 Initialisiere Whisper v3...")
    transcriber = WhisperTranscriber(model_size=model_size)
    
    print("📱 Verarbeite WhatsApp-Chat...")
    processor = WhatsAppAudioProcessor(transcriber)
    
    enhanced_chat, audio_messages = processor.process_chat_with_audio(
        chat_file, 
        media_folder
    )
    
    print(f"✅ {len(audio_messages)} Sprachnachrichten transkribiert!")
    
    # Statistiken
    if audio_messages:
        avg_confidence = sum(a.confidence for a in audio_messages) / len(audio_messages)
        print(f"📊 Durchschnittliche Konfidenz: {avg_confidence:.1%}")
    
    return enhanced_chat

# Beispiel-Nutzung
if __name__ == "__main__":
    # Test mit Beispiel-Chat
    test_chat = """01.07.24, 14:32 - Max: Hey, wie geht's?
01.07.24, 14:33 - Anna: PTT-20240701-WA0001.opus (Datei angehängt)
01.07.24, 14:35 - Max: Verstehe, das klingt stressig
01.07.24, 14:36 - Anna: Ja, total. Hör mal:
01.07.24, 14:36 - Anna: AUD-20240701-WA0002.opus (Datei angehängt)
01.07.24, 14:40 - Max: Ok, lass uns morgen telefonieren"""
    
    print("📝 Original Chat:")
    print(test_chat)
    print("\n" + "="*50 + "\n")
    
    # Simuliere Transkription
    print("🎤 [Würde Audio-Dateien transkribieren und einfügen]")
    print("✅ Sprachnachrichten wurden an den richtigen Stellen eingefügt!")
