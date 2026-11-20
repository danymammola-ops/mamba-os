import sqlite3
import urllib.request
import json

db_path = r"c:\Users\danym\Desktop\Dany\mio\ai\freellmapi\server\data\freeapi.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT value FROM settings WHERE key = 'unified_api_key'")
key = cur.fetchone()[0]
print("Key found:", key)

req = urllib.request.Request("http://127.0.0.1:3001/v1/models", headers={"Authorization": f"Bearer {key}"})
with urllib.request.urlopen(req) as r:
    data = json.loads(r.read())
    print("Port 3001 models authorized:", len(data.get("data", [])))
