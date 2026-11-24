#!/usr/bin/env python3
"""
mamba/voice/tts_engine.py - Servizio Voce Neurale Italiana per MAMBA OS
Usa Microsoft Edge-TTS (voce naturale gratuita) con cache locale su disco e retry.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CACHE_DIR = DATA_DIR / "tts-cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

AVAILABLE_VOICES: List[Dict[str, str]] = [
    {"id": "it-IT-GiuseppeMultilingualNeural", "label": "Giuseppe (Naturale · Consigliata)", "gender": "M"},
    {"id": "it-IT-DiegoNeural", "label": "Diego (Deciso)", "gender": "M"},
    {"id": "it-IT-IsabellaNeural", "label": "Isabella (Espressiva)", "gender": "F"},
    {"id": "it-IT-ElsaNeural", "label": "Elsa (Chiara)", "gender": "F"},
]
DEFAULT_VOICE = "it-IT-GiuseppeMultilingualNeural"

URL_RE = re.compile(r"https?://\S+")
MD_SYMBOLS_RE = re.compile(r"[*_`#>~|\[\]{}]+")
EMOJI_SURROGATE_RE = re.compile(r"[\U00010000-\U0010ffff]")


def clean_speech_text(text: str) -> str:
    """Rimuove markdown, emoji e simboli tecnici per una lettura vocale naturale."""
    if not text:
        return ""
    s = URL_RE.sub("link", text)
    s = s.replace("[[", "").replace("]]", "")
    s = MD_SYMBOLS_RE.sub(" ", s)
    s = EMOJI_SURROGATE_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    # Limite ragionevole per risposta fluida (max ~900 caratteri per singolo chunk)
    if len(s) > 950:
        s = s[:940].rsplit(" ", 1)[0] + "."
    return s


async def _synth_edge_tts(text: str, voice: str, rate: str, pitch: str) -> bytes:
    import edge_tts

    audio = bytearray()
    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    async for chunk in comm.stream():
        if chunk.get("type") == "audio":
            audio.extend(chunk["data"])
    return bytes(audio)


def synthesize_speech(
    text: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+4%",
    pitch: str = "+0Hz",
    use_cache: bool = True,
) -> bytes:
    """Genera audio MP3 neurale con retry automatico e cache locale."""
    cleaned = clean_speech_text(text)
    if not cleaned:
        raise ValueError("Testo vocale vuoto")

    valid_ids = {v["id"] for v in AVAILABLE_VOICES}
    if voice not in valid_ids:
        voice = DEFAULT_VOICE

    cache_key = hashlib.sha256(f"{voice}|{rate}|{pitch}|{cleaned}".encode("utf-8")).hexdigest()[:24]
    cache_file = CACHE_DIR / f"{cache_key}.mp3"

    if use_cache and cache_file.exists() and cache_file.stat().st_size > 200:
        return cache_file.read_bytes()

    last_err: Optional[Exception] = None
    for attempt in range(4):
        try:
            audio_bytes = asyncio.run(_synth_edge_tts(cleaned, voice, rate, pitch))
            if audio_bytes and len(audio_bytes) > 200:
                if use_cache:
                    try:
                        cache_file.write_bytes(audio_bytes)
                    except Exception:
                        pass
                return audio_bytes
        except Exception as exc:
            last_err = exc
            time.sleep(0.25 * (attempt + 1))

    raise RuntimeError(f"Edge-TTS fallito dopo 4 tentativi: {last_err}")
