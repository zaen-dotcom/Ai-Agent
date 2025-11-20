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
MODEL_FILENAME = "Qwen2.5-7B-Instruct.Q5_1.gguf" # Pastikan nama file sesuai
MODEL_PATH = str(MODELS_DIR / MODEL_FILENAME)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model tidak ditemukan di: {MODEL_PATH}")

# ==================================================
# 2. MODEL INIT PARAMS
# ==================================================
MODEL_INIT_PARAMS = {
    "model_path": MODEL_PATH,
    "n_ctx": 16384,           
    "n_gpu_layers": 99,       
    "n_threads": 8,           
    "n_batch": 512,           
    "verbose": False,         
    "use_mlock": True,        
    "use_mmap": True,
    "rope_freq_base": 1000000 
}

# ==================================================
# 3. GENERATION PARAMS
# ==================================================
GENERATION_PARAMS = {
    "max_tokens": 2048,       
    "temperature": 0.5,       
    "top_p": 0.9,            
    "repeat_penalty": 1.15,    
    "echo": False,            
    "stop": ["<|im_end|>", "<|endoftext|>"] 
}

# ==================================================
# 4. SYSTEM PROMPT (CLI OPTIMIZED)
# ==================================================
SYSTEM_PROMPT = """
Kamu adalah Lumino (Qwen Core), ahli Fisika Kuantum dan Matematika.

ATURAN FORMATTING (KRUSIAL UNTUK CLI):
1. DILARANG KERAS menggunakan format LaTeX Block seperti:
   - \\begin{pmatrix}, \\begin{bmatrix}, \\frac{}{}
   - Terminal TIDAK BISA membaca kode tersebut!

2. GUNAKAN FORMAT LINEAR / PYTHON STYLE:
   - Matriks: Gunakan representasi array [[a, b], [c, d]]
   - Pecahan: Gunakan garis miring (1/2, a/b)
   - Akar: Gunakan simbol √ atau pangkat (1/2)

3. FISIKA KUANTUM:
   - Gunakan Notasi Dirac dengan representasi vektor baris:
     Contoh: |0⟩ = [1, 0]  dan  |1⟩ = [0, 1]
   - Operator Pauli (contoh format yang benar):
     σ_x = [[0, 1], [1, 0]]
     σ_z = [[1, 0], [0, -1]]

4. BAHASA:
   - Gunakan Bahasa Indonesia untuk penjelasan.
   - Jelaskan langkah perhitungan secara verbal jika rumus terlalu rumit.
"""

# ==================================================
# 5. PROMPT TEMPLATE
# ==================================================
def MAKE_PROMPT(system, user):
    return (
        f"<|im_start|>system\n{system}<|im_end|>\n"
        f"<|im_start|>user\n{user}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )