"""
Kimi K2 API Client - Robuste KI-Integration
"""
import os
import httpx
import asyncio
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from functools import lru_cache

# Simple logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KimiK2Client:
    """
    Robuster Client für Kimi K2 API
    Features:
    - Async/await Support
    - Automatische Retries
    - Caching
    - Strukturierte Fehlerbehandlung
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("KIMI_API_KEY")
        self.base_url = "https://api.moonshot.ai/v1"
        self.model = "moonshot-v1-8k"
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self.max_retries = 3
        
        # Stats
        self.stats = {
            "requests": 0,
            "successes": 0,
            "failures": 0
        }
        
    @property
    def is_available(self) -> bool:
        """Prüft ob die API verfügbar ist"""
        return bool(self.api_key)
        
    async def analyze_text(
        self,
        text: str,
        context: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Analysiere Text mit Kimi K2
        """
        if not self.is_available:
            return {"error": "Kimi API key not configured", "ai_available": False}
            
        self.stats["requests"] += 1
        
        # Build prompt
        messages = [
            {
                "role": "system",
                "content": "Du bist ein Experte für Kommunikationsanalyse und Betrugserkennung. Analysiere den folgenden WhatsApp-Chat und identifiziere wichtige Muster."
            },
            {
                "role": "user", 
                "content": self._build_prompt(text, context)
            }
        ]
        
        # Make request with retries
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.model,
                            "messages": messages,
                            "temperature": temperature,
                            "max_tokens": max_tokens
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                        
                        # Try to parse JSON response
                        try:
                            result = json.loads(content)
                            self.stats["successes"] += 1
                            return {
                                "ai_available": True,
                                "ai_analysis": result,
                                "model": self.model
                            }
                        except json.JSONDecodeError:
                            # Return as text if not JSON
                            self.stats["successes"] += 1
                            return {
                                "ai_available": True,
                                "ai_analysis": {
                                    "summary": content,
                                    "raw_text": True
                                },
                                "model": self.model
                            }
                    
                    elif response.status_code == 429:
                        # Rate limit
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                            continue
                    
                    else:
                        logger.error(f"API error: {response.status_code}")
                        
            except Exception as e:
                logger.error(f"Request failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                    
        self.stats["failures"] += 1
        return {
            "error": "Failed to get AI analysis",
            "ai_available": False
        }
        
    def _build_prompt(self, text: str, context: Optional[str]) -> str:
        """Erstelle strukturierten Analyse-Prompt"""
        prompt_parts = [
            f"Analysiere diesen WhatsApp-Chat-Auszug (max 2000 Zeichen):",
            f"```\n{text[:2000]}\n```"
        ]
        
        if context:
            prompt_parts.append(f"\nKontext: {context}")
            
        prompt_parts.extend([
            "\nErstelle eine strukturierte Analyse als JSON mit:",
            "{\n",
            '  "sentiment": {"overall": "positive|neutral|negative", "score": 0.0-1.0},\n',
            '  "key_topics": ["topic1", "topic2", ...],\n',
            '  "risk_indicators": [{"type": "...", "severity": "low|medium|high", "description": "..."}],\n',
            '  "communication_patterns": ["pattern1", "pattern2"],\n',
            '  "summary": "2-3 Sätze Zusammenfassung"\n',
            "}"
        ])
        
        return "\n".join(prompt_parts)

# Synchronous wrapper for GUI integration
def analyze_with_kimi_sync(text: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Synchrone Wrapper-Funktion für GUI"""
    client = KimiK2Client(api_key=api_key)
    
    if not client.is_available:
        return {"ai_available": False, "reason": "No API key"}
    
    # Run async function in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(client.analyze_text(text))
        return result
    finally:
        loop.close()
