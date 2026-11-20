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
                output_text = ""

                # Esegui in base alla rotta
                if rtype == "text":
                    output_text = console.execute(prompt)
                elif rtype == "whatsapp":
                    res = console.execute(prompt)
                    output_text = f"Messaggio inviato su WhatsApp a {res.get('recipient', 'contatto')} in {res.get('elapsed', 0):.2f}s!"
                elif rtype == "close_app":
                    res = console.execute(prompt)
                    output_text = f"Applicazione {res.get('app')} chiusa con successo."
                elif rtype == "snap_window":
                    res = console.execute(prompt)
                    output_text = f"Finestra {res.get('window')} posizionata al 50% con successo."
                else:
                    output_text = console.execute(prompt) or "Comando elaborato."

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
    httpd = HTTPServer(server_address, MambaUIHandler)
    print(f"\n🐍 [MAMBA OS HUD] Server avviato con successo su: http://127.0.0.1:{port}")
    print(f"👉 Apri il browser all'indirizzo sopra per interagire con l'App HUD!")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArresto del server Mamba UI.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
