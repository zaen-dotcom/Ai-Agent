import os
from pathlib import Path

# ==================================================
# 1. PATH CONFIGURATION
# ==================================================
BACKEND_DIR = Path(__file__).resolve().parent   
ROOT_DIR = BACKEND_DIR.parent
MODELS_DIR = ROOT_DIR / "models"
PROJECT_DIR = ROOT_DIR 

# --- KONFIGURASI MODEL ---
# Pastikan nama file sesuai dengan yang Anda download
MODEL_FILENAME = "Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf"
MODEL_PATH = str(MODELS_DIR / MODEL_FILENAME)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model tidak ditemukan di: {MODEL_PATH}")

# ==================================================
# 2. MODEL INIT PARAMS
# ==================================================
MODEL_INIT_PARAMS = {
    "model_path": MODEL_PATH,
    "n_ctx": 8192,            # Context window standar Llama 3.1
    "n_gpu_layers": 99,       # Offload ke GPU
    "n_threads": 8,           
    "n_batch": 512,           
    "verbose": False,         
    "use_mlock": True,        
    "use_mmap": True,         
    "rope_freq_base": 500000  # Settingan wajib untuk Llama 3.1
}

# ==================================================
# 3. GENERATION PARAMS
# ==================================================
GENERATION_PARAMS = {
    "max_tokens": 2048,       
    "temperature": 0.7,       # Sedikit kreatif untuk penjelasan umum
    "top_p": 0.95,            
    "repeat_penalty": 1.15,   # Mencegah pengulangan kata
    "echo": False,            
    
    # STOP TOKENS (Sangat Penting untuk Llama 3 agar tidak looping)
    "stop": [
        "<|eot_id|>", 
        "<|end_of_text|>", 
        "<|start_header_id|>",
        "assistant\n\n"
    ]
}

# ==================================================
# 4. SYSTEM PROMPT (General Knowledge & Math)
# ==================================================
SYSTEM_PROMPT = """
Kamu adalah Lumino, asisten AI yang cerdas, ramah, dan berwawasan luas. 
Fokusmu adalah memberikan penjelasan Pengetahuan Umum, Sains, Sejarah, dan Analisis Logis.

ATURAN FORMATTING (WAJIB DIPATUHI):
1. MATEMATIKA (UNICODE ONLY):
   - Environment ini adalah TERMINAL CLI.
   - DILARANG KERAS menggunakan format LaTeX (seperti $$, \\frac, \\sqrt).
   - GUNAKAN simbol Unicode standar agar terbaca:
     * Akar: Gunakan '√' (contoh: √25 = 5)
     * Pangkat: Gunakan '²' atau '^' (contoh: cm², x^2)
     * Perkalian: Gunakan '×' (contoh: 5 × 5)
     * Pembagian: Gunakan '/' atau '÷'
     * Simbol lain: π, ∑, ∫, ≠, ≈
   - Tulis rumus dalam satu baris (linear).

2. GAYA PENULISAN:
   - Gunakan Bahasa Indonesia yang baku, jelas, dan mudah dimengerti.
   - HINDARI penggunaan em-dashes (—) untuk membuat list.
   - Gunakan Bullet Points standar (• atau -) atau Penomoran (1., 2.) agar rapi.
   - Struktur jawaban harus terorganisir: Pendahuluan -> Poin Utama -> Kesimpulan/Solusi.

3. METODE PEMECAHAN MASALAH:
   - Jika ditanya soal hitungan atau logika:
     * Uraikan "Diketahui".
     * Uraikan "Ditanya".
     * Tunjukkan "Langkah Penyelesaian" secara bertahap.
     * Berikan "Kesimpulan" di akhir.

4. SIFAT:
   - Edukatif: Jelaskan *mengapa* jawabannya begitu, bukan hanya memberi hasil.
   - Objektif: Berikan fakta yang berimbang.
"""

# ==================================================
# 5. PROMPT TEMPLATE (LLAMA 3 FORMAT)
# ==================================================
def MAKE_PROMPT(system, user):
    """
    Format Prompt Resmi Llama 3.1.
    Mencegah model bingung atau looping.
    """
    return (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n{user}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
    )