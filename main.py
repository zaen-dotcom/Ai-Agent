import threading
import time
import sys
import logging
import os
import json
import io

# FORCE UTF-8 ENCODING (Fix for Windows 'charmap' error)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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
            # Stream the response
            for event in engine.generate_response(processed_msg, stream=True):
                if isinstance(event, dict):
                    if event["type"] == "content":
                        yield json.dumps({"type": "token", "content": event["data"]}) + "\n"
                    elif event["type"] == "usage":
                        yield json.dumps({"type": "usage", "stats": event["data"]}) + "\n"
                else:
                    # Fallback for legacy string yields (safety)
                    yield json.dumps({"type": "token", "content": event}) + "\n"
        
        return Response(stream_with_context(generate()), mimetype='application/json')
    else:
        result = engine.generate_response(processed_msg, stream=False)
        
        # Handle legacy string response
        if isinstance(result, str):
             return jsonify({"response": result, "files_read": []})
             
        # Handle new dict response
        return jsonify({
            "response": result["content"],
            "usage": result.get("usage"),
            "files_read": []
        })

@app.route('/model/set', methods=['POST'])
def set_model():
    data = request.json
    model_name = data.get('model')
    if not model_name:
        return jsonify({"error": "Model name required"}), 400
        
    try:
        success = engine.switch_model(model_name)
        if success:
            return jsonify({"status": "success", "message": f"Switched to {model_name}"})
        else:
            return jsonify({"error": "Failed to load model"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset_model():
    """Legacy endpoint - redirects to default behavior or error"""
    return jsonify({"error": "Use /model/set to switch models"}), 400

@app.route('/models', methods=['GET'])
def list_models():
    return jsonify({"models": config.get_available_models()})

def run_server():
    # use_reloader=False itu WAJIB agar patch di atas bekerja
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # 1. Intro Visual (Removed legacy intro import)
    
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