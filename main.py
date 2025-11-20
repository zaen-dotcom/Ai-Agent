import threading
import time
import sys
import logging
import os

# --- 1. SILENCE FLASK & WERKZEUG (KODE INI WAJIB PALING ATAS) ---
# Matikan log startup Flask CLI (* Serving Flask app...)
import flask.cli
flask.cli.show_server_banner = lambda *args: None

# Matikan log startup Werkzeug (* Running on http://...)
from werkzeug.serving import BaseWSGIServer
def silent_startup(self): pass # Fungsi kosong
BaseWSGIServer.log_startup = silent_startup

# Matikan log request HTTP (POST /chat 200 OK)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
log.disabled = True
# ----------------------------------------------------------------

# --- IMPORT LAINNYA ---
from frontend import intro
from frontend import client 
from backend.core import engine
from backend.utils import process_input_commands
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "Pesan kosong"}), 400

    processed_msg, files_read = process_input_commands(user_message)
    ai_response = engine.generate_response(processed_msg)

    return jsonify({
        "response": ai_response,
        "files_read": files_read
    })

@app.route('/reset', methods=['POST'])
def reset_model():
    """Memicu menu pemilihan model di sisi server"""
    try:
        # Panggil fungsi switch di engine
        engine.switch_model() 
        return jsonify({"status": "success", "message": "Neural Module Switched"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_server():
    # use_reloader=False itu WAJIB agar patch di atas bekerja
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # 1. Intro Visual
    try:
        intro() 
    except:
        pass

    # 2. Jalankan Server (Sekarang benar-benar hening)
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # 3. Delay
    time.sleep(2) 

    # 4. Jalankan UI Client
    try:
        client.run() 
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)