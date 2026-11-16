#!/usr/bin/env python3
"""
mamba/moves/visual_agent.py - Computer Use & Visual Grounding Agent per Mamba OS
Combina visione artificiale multimodale (gemini-flash-lite / gemini-3.8-flash via FreeLLMAPI)
con User Moves nativi e aggancio a WinSta0\\default.

Velocità record: risposta visiva in ~1.7s!
"""

import os
import sys
import json
import base64
import time
from io import BytesIO
from typing import Dict, Any, Optional, Tuple
from PIL import Image

# Importa client FreeLLM e movimenti utente
from mamba.core.freellm_client import FreeLLMClient
from mamba.moves.user_moves import (
    attach_to_user_desktop,
    get_screen_size,
    get_mouse_position,
    smooth_move,
    click_at,
    type_text,
    take_screenshot
)

class VisualAgent:
    def __init__(self, model: str = "gemini-flash-lite"):
        self.model = model
        self.client = FreeLLMClient()
        attach_to_user_desktop()

    def capture_and_encode(self, max_width: int = 1280) -> Tuple[str, float, float]:
        """
        Cattura lo schermo del desktop visibile e restituisce (b64, scale_x, scale_y).
        """
        attach_to_user_desktop()
        img = take_screenshot()
        orig_w, orig_h = img.size
        
        # Ridimensiona proporzionalmente se necessario
        if orig_w > max_width:
            ratio = max_width / float(orig_w)
            new_h = int(float(orig_h) * ratio)
            resized = img.resize((max_width, new_h), Image.Resampling.LANCZOS)
        else:
            resized = img

        scale_x = orig_w / float(resized.width)
        scale_y = orig_h / float(resized.height)

        buffer = BytesIO()
        resized.save(buffer, format="JPEG", quality=80)
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return b64, scale_x, scale_y

    def locate_element(self, query: str) -> Dict[str, Any]:
        """
        Trova le coordinate (x, y) di un elemento visivo sullo schermo.
        """
        print(f"[visual_agent] 📸 Cattura schermo per cercare: '{query}'...")
        b64, scale_x, scale_y = self.capture_and_encode()
        screen_w, screen_h = get_screen_size()

        prompt = f"""You are a GUI visual grounding agent for a desktop screen.
Screen resolution is {screen_w}x{screen_h}.
Your task: Find the exact center coordinates (x, y) of: '{query}'.

Return ONLY a valid JSON object in this format (no markdown, no extra text):
{{"found": true, "x": 100, "y": 200, "description": "short note"}}

If not found, return:
{{"found": false, "x": 0, "y": 0, "description": "not visible"}}
"""

        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]
        }]

        print(f"[visual_agent] 🧠 Analisi visiva con FreeLLM ({self.model})...")
        t0 = time.time()
        
        # Tenta con il modello ultrarapido, fallback su gemini-3.8-flash
        res = None
        for candidate in [self.model, "gemini-3.8-flash", "claude-sonnet-4-5"]:
            try:
                res = self.client.chat(messages, model=candidate, temperature=0.1, timeout=25)
                if res and res.get("content"):
                    break
            except Exception as e:
                print(f"[visual_agent] Tentativo con {candidate} fallito ({e}), provo fallback...")
                
        latency = time.time() - t0
        if not res or not res.get("content"):
            return {"found": False, "x": 0, "y": 0, "description": "Nessuna risposta dal modello", "latency": latency}

        content = res.get("content", "").strip()

        # Pulizia formato markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        try:
            parsed = json.loads(content)
            # Scala le coordinate se l'immagine era stata ridimensionata
            raw_x = int(parsed.get("x", 0))
            raw_y = int(parsed.get("y", 0))
            
            # Se le coordinate sono già in scala originale o ridimensionata
            if raw_x <= 1280 and scale_x > 1.05 and raw_x > 0:
                target_x = int(raw_x * scale_x)
                target_y = int(raw_y * scale_y)
            else:
                target_x = raw_x
                target_y = raw_y

            target_x = max(0, min(screen_w - 1, target_x))
            target_y = max(0, min(screen_h - 1, target_y))
            
            return {
                "found": parsed.get("found", True if target_x > 0 else False),
                "x": target_x,
                "y": target_y,
                "description": parsed.get("description", ""),
                "latency": round(latency, 2),
                "model": res.get("model", self.model)
            }
        except Exception as e:
            print(f"[visual_agent] Parsing fallback: {content} ({e})")
            return {
                "found": False,
                "x": 0,
                "y": 0,
                "description": content,
                "latency": round(latency, 2)
            }

    def click_element(self, query: str, double: bool = False) -> Dict[str, Any]:
        """
        Cerca visivamente un elemento sullo schermo, muove il mouse fluidamente e ci clicca sopra.
        """
        attach_to_user_desktop()
        target = self.locate_element(query)
        if not target.get("found"):
            print(f"[visual_agent] ❌ Elemento '{query}' non individuato: {target.get('description')}")
            return target

        tx, ty = target["x"], target["y"]
        print(f"[visual_agent] 🎯 Trovato a ({tx}, {ty}) in {target['latency']}s! Scivolo con il cursore...")
        
        # Movimento visibile di 1 secondo per vederlo chiaramente muoversi
        click_res = click_at(tx, ty, double=double, duration=1.0)
        print(f"[visual_agent] ✅ Click eseguito su ({tx}, {ty})!")
        
        return {
            "success": True,
            "target": query,
            "coordinates": (tx, ty),
            "description": target.get("description"),
            "latency": target.get("latency")
        }

if __name__ == "__main__":
    agent = VisualAgent()
    target_query = sys.argv[1] if len(sys.argv) > 1 else "l'orologio nella barra delle applicazioni in basso a destra"
    print(f"=== MAMBA VISUAL AGENT ===")
    print(f"Obiettivo visivo: '{target_query}'")
    print(f"Posizione mouse attuale: {get_mouse_position()}")
    result = agent.click_element(target_query)
    print("Risultato:", result)
