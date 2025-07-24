#!/usr/bin/env python3
"""
MarkerEngine Kimi Client - Robuste KI-Integration
"""

import os
import httpx
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class KimiK2Client:
    """Client für die Kimi K2 API mit Caching und Retry-Logik"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("KIMI_API_KEY")
        self.base_url = "https://api.moonshot.ai/v1"
        self.timeout = httpx.Timeout(10.0, connect=5.0)
        self._cache = {}
        
    @property
    def is_available(self) -> bool:
        """Prüft ob die API verfügbar ist"""
        return bool(self.api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def enrich_with_kimi(
        self, 
        text: str, 
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reichert Text mit KI-Insights an
        """
        if not self.is_available:
            return {}
            
        # Cache-Check
        cache_key = f"{text[:50]}_{context[:20] if context else ''}"
        if cache_key in self._cache:
            logger.debug("Returning cached result")
            return self._cache[cache_key]
        
        # Prepare prompt
        prompt = self._build_prompt(text, context)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "moonshot-v1-8k",
                        "messages": [
                            {
                                "role": "system",
                                "content": "Du bist ein Experte für Kommunikationsanalyse und Beziehungsdynamiken."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    }
                )
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                try:
                    # Versuche JSON zu parsen
                    result = json.loads(content)
                except json.JSONDecodeError:
                    # Fallback: Strukturiere die Antwort selbst
                    result = {
                        "raw_analysis": content,
                        "timestamp": datetime.now().isoformat(),
                        "status": "parsed_as_text"
                    }
                    
                self._cache[cache_key] = result
                return result
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("Rate limit reached")
                raise
            logger.error(f"HTTP error: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {}
    
    def _build_prompt(self, text: str, context: Optional[str]) -> str:
        """Erstellt einen strukturierten Prompt für die Analyse"""
        prompt_parts = [
            "Analysiere den folgenden WhatsApp-Chat-Auszug auf Kommunikationsmuster und Beziehungsdynamiken:",
            f"Text: {text[:2000]}",  # Begrenzen für Token-Limits
        ]
        
        if context:
            prompt_parts.append(f"Kontext: {context}")
            
        prompt_parts.extend([
            "",
            "Gib eine strukturierte Analyse zurück mit:",
            "1. Emotionale Stimmung (positiv/neutral/negativ mit Prozentangaben)",
            "2. Hauptthemen (Liste der 3-5 wichtigsten Themen)",
            "3. Kommunikationsdynamik (dominant/ausgeglichen/zurückhaltend)",
            "4. Auffällige Muster (z.B. Manipulation, Gaslighting, Love-Bombing)",
            "5. Risikoeinschätzung (niedrig/mittel/hoch mit Begründung)",
            "",
            "Antwort als JSON-Objekt ohne Markdown-Formatierung."
        ])
        
        return "\n".join(prompt_parts)


# Synchrone Wrapper-Funktion für einfache Nutzung
def analyze_with_kimi(text: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Synchroner Wrapper für die KI-Analyse"""
    client = KimiK2Client(api_key)
    
    if not client.is_available:
        return {"error": "No API key provided"}
        
    # Event Loop erstellen falls nicht vorhanden
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(client.enrich_with_kimi(text))
