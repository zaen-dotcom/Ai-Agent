import os
from pathlib import Path

# ==================================================
# 1. PATH CONFIGURATION
# ==================================================
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
MODELS_DIR = ROOT_DIR / "models"
PROJECT_DIR = ROOT_DIR

# ==================================================
# 2. DEFAULT PARAMETERS
# ==================================================
DEFAULT_INIT_PARAMS = {
    "n_ctx": 8192,
    "n_gpu_layers": 99,  # Offload all to GPU
    "n_threads": 8,
    "n_batch": 512,
    "verbose": False,
    "use_mlock": True,
    "use_mmap": True,
    "rope_freq_base": 1000000
}

DEFAULT_GEN_PARAMS = {
    "max_tokens": 4096,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.1,
}

# ==================================================
# 3. PROMPT TEMPLATES & SYSTEM PROMPTS
# ==================================================
SYSTEM_PROMPT_GENERAL = """
Kamu adalah Lumino, asisten AI yang cerdas, ramah, dan berwawasan luas yang di kembangkan oleh Fadil Z.
Fokusmu adalah memberikan penjelasan yang jelas, akurat, dan edukatif.

ATURAN FORMATTING (CLI):
- JANGAN gunakan LaTeX block ($$, \\frac). Gunakan Unicode (√, ², ÷).
- Gunakan bullet points untuk list.
- Bahasa Indonesia yang baku dan jelas.
"""

SYSTEM_PROMPT_CODING = """
Kamu adalah Lumino, Assistant Local Intelligence Unit spesialis coding dan arsitektur software.

ATURAN:
1. MATEMATIKA: Gunakan Unicode (√, ², ÷). JANGAN LaTeX.
2. CODING: Gunakan markdown block ```language ... ```.
3. ANALISIS: To-the-point, jelaskan root cause dan solusi.
"""

def format_chatml(system, messages):
    """Format for Qwen/ChatML models"""
    prompt = f"<|im_start|>system\n{system}<|im_end|>\n"
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
    prompt += "<|im_start|>assistant\n"
    return prompt

def format_llama3(system, messages):
    """Format for Llama 3 models"""
    prompt = f"<|start_header_id|>system<|end_header_id|>\n\n{system}<|eot_id|>"
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        prompt += f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}<|eot_id|>"
    prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
    return prompt

# ==================================================
# 4. MODEL CONFIGURATIONS
# ==================================================
class ModelConfig:
    def __init__(self, filename):
        self.filename = filename
        self.path = str(MODELS_DIR / filename)
        
        # Default values
        self.description = "General Purpose AI"
        self.icon = "🧠"
        self.name = filename.replace(".gguf", "").replace("-", " ").title()
        
        # Detect type based on filename
        lower_name = filename.lower()
        
        if "coder" in lower_name:
            self.type = "qwen_coder"
            self.name = "Qwen 2.5 Coder"
            self.description = "Coding & Arsitektur"
            self.icon = "💻"
            self.system_prompt = SYSTEM_PROMPT_CODING
            self.stop_tokens = ["<|im_end|>", "<|endoftext|>"]
            self.format_func = format_chatml
            self.init_params = DEFAULT_INIT_PARAMS.copy()
            self.init_params["n_ctx"] = 16384 
            self.gen_params = DEFAULT_GEN_PARAMS.copy()
            self.gen_params["temperature"] = 0.1 # Precise for coding
            self.gen_params["stop"] = self.stop_tokens
            
        elif "qwen" in lower_name and "instruct" in lower_name:
            self.type = "qwen_instruct"
            self.name = "Qwen 2.5 Instruct"
            self.description = "Asisten Serbaguna & Cepat"
            self.icon = "🚀"
            self.system_prompt = SYSTEM_PROMPT_GENERAL
            self.stop_tokens = ["<|im_end|>", "<|endoftext|>"]
            self.format_func = format_chatml
            self.init_params = DEFAULT_INIT_PARAMS.copy()
            self.init_params["n_ctx"] = 8192
            self.gen_params = DEFAULT_GEN_PARAMS.copy()
            self.gen_params["temperature"] = 0.7
            self.gen_params["stop"] = self.stop_tokens

        elif "llama-3" in lower_name:
            self.type = "llama3"
            self.name = "Llama 3.1 Instruct" 
            self.description = "Pengetahuan Umum & Logika"
            self.icon = "📚"
            self.system_prompt = SYSTEM_PROMPT_GENERAL
            self.stop_tokens = ["<|eot_id|>", "<|end_of_text|>", "assistant\n\n"]
            self.format_func = format_llama3
            self.init_params = DEFAULT_INIT_PARAMS.copy()
            self.init_params["rope_freq_base"] = 500000 
            self.gen_params = DEFAULT_GEN_PARAMS.copy()
            self.gen_params["stop"] = self.stop_tokens
            
        else:
            # Fallback / Generic
            self.type = "generic"
            self.description = "Model Generik"
            self.icon = "🤖"
            self.system_prompt = SYSTEM_PROMPT_GENERAL
            self.stop_tokens = ["User:", "Assistant:"]
            self.format_func = None 
            self.init_params = DEFAULT_INIT_PARAMS.copy()
            self.gen_params = DEFAULT_GEN_PARAMS.copy()

        # CRITICAL FIX: Add model_path to init_params
        self.init_params["model_path"] = self.path

    def make_prompt(self, messages):
        if self.format_func:
            return self.format_func(self.system_prompt, messages)
        else:
            # Fallback simple format
            prompt = f"System: {self.system_prompt}\n\n"
            for msg in messages:
                prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
            prompt += "Assistant: "
            return prompt

def get_available_models():
    """Scan models directory for .gguf files"""
    if not MODELS_DIR.exists():
        return []
    return [f.name for f in MODELS_DIR.glob("*.gguf")]