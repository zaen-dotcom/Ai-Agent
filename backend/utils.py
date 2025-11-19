import os
import re
from backend.config import PROJECT_DIR

def read_file_content(filename):
    """
    Membaca file lokal dari folder project secara aman.
    """
    # Gabungkan path project dengan nama file yang diminta
    target_path = os.path.join(PROJECT_DIR, filename.strip())
    
    # Keamanan: Pastikan file benar-benar ada di dalam PROJECT_DIR
    # (Mencegah request seperti /read ../../../windows/system32)
    if not os.path.commonpath([PROJECT_DIR, os.path.abspath(target_path)]) == str(PROJECT_DIR):
        return f"[SISTEM: Akses ditolak. File {filename} berada di luar folder projek.]"

    if not os.path.exists(target_path):
        return f"[SISTEM: File {filename} tidak ditemukan.]"

    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Format agar AI paham ini adalah isi file
            return (
                f"\n\n--- START OF FILE: {filename} ---\n"
                f"```{filename.split('.')[-1]}\n"  # Hint extension untuk syntax highlighting
                f"{content}\n"
                f"```\n"
                f"--- END OF FILE ---\n\n"
            )
    except Exception as e:
        return f"[SISTEM: Gagal membaca file. Error: {str(e)}]"

def process_input_commands(user_input):
    """
    Mendeteksi command /read namafile.ext dan menggantinya dengan isi file asli.
    """
    # Regex untuk mencari pattern /read namafile
    # Contoh match: /read main.py, /read style.css
    pattern = r"/read\s+([a-zA-Z0-9_\-\./]+)"
    
    matches = re.findall(pattern, user_input)
    
    processed_input = user_input
    files_read = []

    for filename in matches:
        file_content = read_file_content(filename)
        # Ganti command /read main.py dengan ISI file tersebut di dalam prompt
        processed_input = processed_input.replace(f"/read {filename}", file_content)
        files_read.append(filename)
    
    return processed_input, files_read