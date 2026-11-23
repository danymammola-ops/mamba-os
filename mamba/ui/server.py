#!/usr/bin/env python3
"""
mamba/ui/server.py - Server Web & API per Mamba OS Neural HUD
Serve l'interfaccia grafica olografica su http://127.0.0.1:5173
e gestisce le richieste /api/command collegandosi a FreeLLMAPI e ai Micro-Agenti.
"""

import sys
import os
import json
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse

sys.path.insert(0, r"C:\Users\danym\mio\mamba")
from mamba.console import MambaConsole

UI_DIR = os.path.dirname(os.path.abspath(__file__))
console = MambaConsole()

class MambaUIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/api/command":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                prompt = data.get("prompt", "").strip()
                
                route_info = console.route_request(prompt)
                rtype = route_info["type"]
                
                # Esegui il comando
                res = console.execute(prompt)
                if isinstance(res, dict):
                    output_text = res.get("output") or res.get("text") or str(res)
                else:
                    output_text = str(res)

                resp = {
                    "success": True,
                    "output": output_text or "Comando eseguito con successo.",
                    "route": rtype
                }
            except Exception as e:
                resp = {
                    "success": False,
                    "error": str(e),
                    "route": "error"
                }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        elif self.path == "/api/chat/clear":
            console.clear_history()
            resp = {"success": True, "message": "Cronologia chat azzerata."}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        elif self.path == "/api/pet/config":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                new_cfg = json.loads(post_data)
                cfg_file = os.path.join(UI_DIR, "pet_config.json")
                cur_cfg = {}
                if os.path.exists(cfg_file):
                    try:
                        with open(cfg_file, "r", encoding="utf-8") as f:
                            cur_cfg = json.load(f)
                    except Exception:
                        pass
                cur_cfg.update(new_cfg)
                with open(cfg_file, "w", encoding="utf-8") as f:
                    json.dump(cur_cfg, f, indent=2)

                # Gestione processo Desktop Pet fluttuante
                if cur_cfg.get("enabled", True):
                    # Se abilitato, avvia desktop_pet.py se non già attivo
                    import subprocess
                    pet_script = os.path.join(UI_DIR, "desktop_pet.py")
                    subprocess.Popen([sys.executable, pet_script], creationflags=0x00000008) # DETACHED_PROCESS

                resp = {"success": True, "config": cur_cfg}
            except Exception as e:
                resp = {"success": False, "error": str(e)}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        else:
            self.send_error(404, "Endpoint not found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

def run_server(port=5173):
    server_address = ("127.0.0.1", port)
    try:
        httpd = HTTPServer(server_address, MambaUIHandler)
    except OSError as e:
        # Se la porta è già aperta e occupata dal server precedente
        print(f"ℹ️ [MAMBA OS HUD] Il server è già attivo e in ascolto su: http://127.0.0.1:{port}")
        return

    print(f"\n🐍 [MAMBA OS HUD] Server avviato con successo su: http://127.0.0.1:{port}")
    print(f"👉 Apri il browser all'indirizzo sopra per interagire con l'App HUD!")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArresto del server Mamba UI.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
