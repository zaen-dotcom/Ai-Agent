import os
from pathlib import Path

# ==================================================
# 1. PATH CONFIGURATION
# ==================================================
# Dapatkan lokasi folder 'backend'
BACKEND_DIR = Path(__file__).resolve().parent   

# Naik satu level ke atas untuk dapatkan ROOT folder (AIAgent)
ROOT_DIR = BACKEND_DIR.parent

# Arahkan ke folder models dari ROOT
MODELS_DIR = ROOT_DIR / "models"

# Project Dir set ke ROOT
PROJECT_DIR = ROOT_DIR 

# --- KONFIGURASI MODEL ---
MODEL_FILENAME = "qwen2.5-coder-7b-instruct-q5_k_m.gguf"
MODEL_PATH = str(MODELS_DIR / MODEL_FILENAME)

# Validasi path
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model tidak ditemukan di: {MODEL_PATH}")

# ==================================================
# 2. MODEL INIT PARAMS (HARDWARE)
# ==================================================
MODEL_INIT_PARAMS = {
    "model_path": MODEL_PATH,
    "n_ctx": 16384,           # Wajib besar untuk konteks file kodingan
    "n_gpu_layers": 99,       # Offload semua ke GPU jika VRAM cukup
    "n_threads": 8,           
    "n_batch": 512,           
    "verbose": False,         
    "use_mlock": True,        
    "use_mmap": True,         
    "rope_freq_base": 1000000 
}

# ==================================================
# 3. GENERATION PARAMS (RESPONSE)
# ==================================================
GENERATION_PARAMS = {
    "max_tokens": 4096,      
    "temperature": 0.6,       
    "top_p": 0.9,             
    "repeat_penalty": 1.1,    
    "echo": False,            
    "stop": ["<|im_end|>", "<|endoftext|>", "\n\n\n"]
}

# ==================================================
# 4. SYSTEM PROMPT (CORE INTELLIGENCE)
# ==================================================
# Update: Menambahkan aturan "CLI Math Formatting"

SYSTEM_PROMPT = """
Kamu adalah Lumino, Local Intelligence Unit spesialis coding dan arsitektur software.

ATURAN FORMATTING TAMPILAN (PENTING UNTUK CLI):
1. MATEMATIKA & LOGIKA (WAJIB UNICODE):
   - Environment ini adalah TERMINAL/CLI, sehingga TIDAK BISA merender LaTeX (seperti $$, \\frac, \\sqrt).
   - JANGAN gunakan sintaks LaTeX. Ganti dengan Simbol Unicode standar:
     * Akar Kuadrat : Gunakan '√' (contoh: √25 = 5)
     * Pangkat      : Gunakan '²' atau '³' atau '^' (contoh: x² + y²)
     * Pecahan      : Gunakan '/' atau '÷' (contoh: 1/2 atau 10 ÷ 2)
     * Perkalian    : Gunakan '×' (contoh: 5 × 5)
     * Pi           : Gunakan 'π' (contoh: 3.14)
     * Sigma/Sum    : Gunakan '∑'
     * Integral     : Gunakan '∫'
     * Logika       : Gunakan '≠', '≈', '≤', '≥'
   - Untuk rumus yang sangat kompleks, tuliskan dalam format satu baris (linear) dengan tanda kurung yang jelas. 
     Contoh: x = (-b ± √(b² - 4ac)) / 2a

2. CODING BERKUALITAS:
   - Tulis kode yang rapi, modular, dan Clean Code.
   - Berikan komentar pada bagian krusial.
   - Selalu gunakan blok markdown untuk kode:
     ```python
     # Kode disini
     ```

3. DEBUGGING & ANALISIS:
   - Jelaskan sumber masalah (Root Cause) secara langsung.
   - Berikan solusi konkret (Code Fix).
   - Identifikasi potensi bug atau anti-pattern.

4. GAYA KOMUNIKASI:
   - Bahasa Indonesia teknis yang padat dan jelas.
   - To-the-point, hindari basa-basi berlebihan.
"""