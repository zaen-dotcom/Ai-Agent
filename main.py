import threading
import time
import sys
import logging
import os
import json

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
from backend import config
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    stream_mode = data.get('stream', False)

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # Process message (simple pass-through for now)
    processed_msg = user_message
    
    if stream_mode:
        def generate():
            # Yield file info first as a special event/chunk if needed
            # But for simplicity, we just stream the text. 
            # Client might need to know about files_read separately or we prepend it.
            # if files_read:
            #    yield json.dumps({"type": "info", "files": files_read}) + "\n"
            
            # Stream the response
            for token in engine.generate_response(processed_msg, stream=True):
                yield json.dumps({"type": "token", "content": token}) + "\n"
        
        return Response(stream_with_context(generate()), mimetype='application/json')
    else:
        ai_response = engine.generate_response(processed_msg, stream=False)
        return jsonify({
            "response": ai_response,
            "files_read": []
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

@app.route('/models', methods=['GET'])
def list_models():
    return jsonify({"models": config.get_available_models()})

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