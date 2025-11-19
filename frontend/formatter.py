import re
from rich.markdown import Markdown
from rich.panel import Panel
from rich import box
from rich.console import Console
from rich.theme import Theme

# --- KONFIGURASI TEMA ---
custom_styles = {
    "markdown.h1": "bold cyan underline",
    "markdown.h2": "bold bright_cyan",
    "markdown.h3": "bold blue",
    "markdown.link": "bold blue underline",
    "markdown.code": "bold #FF00FF",  # Magenta terang untuk kode inline
    "markdown.strong": "bold yellow",
    "markdown.italic": "italic cyan",
    "markdown.block_quote": "dim white",
    # Styling Tabel (Rich handle ini otomatis, tapi kita bisa atur warnanya lewat tema dasar)
}

console = Console(theme=Theme(custom_styles), force_terminal=True, color_system="truecolor")

THEME_CODE_BLOCK = "monokai" 

def replace_latex_with_unicode(text):
    """
    Mengubah sisa-sisa LaTeX menjadi Unicode agar cantik di Terminal.
    """
    replacements = {
        r'\\times': '×',
        r'\\div': '÷',
        r'\\pm': '±',
        r'\\le': '≤',
        r'\\ge': '≥',
        r'\\neq': '≠',
        r'\\approx': '≈',
        r'\\infty': '∞',
        r'\\pi': 'π',
        r'\\theta': 'θ',
        r'\\alpha': 'α',
        r'\\beta': 'β',
        r'\\sum': '∑',
        r'\\prod': '∏',
        r'\\sqrt': '√',
        r'\\int': '∫',
        r'\\rightarrow': '→',
        r'\*\*2': '²', 
        r'\*\*3': '³',
    }
    
    for latex, unicode_char in replacements.items():
        text = re.sub(latex, unicode_char, text)
        
    return text

def clean_markdown_text(text):
    """
    Membersihkan format teks AI dengan logika PINTAR.
    """
    
    # 0. Konversi LaTeX ke Unicode
    text = replace_latex_with_unicode(text)

    # 1. HAPUS ARTIFAK SEBELUM HEADER
    text = re.sub(r'(```\w*)\s*\n(#{1,6}\s)', r'\1\n```\n\n\2', text)

    # 2. PASTIKAN HEADER PUNYA JARAK
    text = re.sub(r'(?<!\n)\n(#{1,6}\s)', r'\n\n\1', text)

    # 3. AUTO-INJECT PYTHON (Hanya jika belum ada lang)
    text = re.sub(r'(\n\n|^)```\s*\n', r'\1```python\n', text)

    # 4. BERSIHKAN PENUTUP CODE BLOCK
    text = re.sub(r'(```)\n(?!```)', r'\1\n\n', text)
    
    # 5. RAPIKAN LIST (Bullet & Numbering)
    text = re.sub(r'(\n)([*-] )', r'\1\n\2', text)
    text = re.sub(r'(\n)(\d+\. )', r'\1\n\2', text)
    
    # 6. RAPIKAN TABEL (FITUR BARU)
    # Masalah: AI sering nulis "Berikut tabelnya:| Header |" tanpa spasi enter.
    # Solusi: Cari baris yang dimulai '|' tapi baris sebelumnya BUKAN '|' (bukan bagian tabel), lalu kasih jarak.
    # Regex: Cari newline, diikuti pipa, di mana sebelumnya TIDAK ada pipa.
    text = re.sub(r'(?<!\|)\n(\|.*\|)', r'\n\n\1', text)

    return text

def create_styled_panel(text, title="Lumino"):
    """
    Membuat Panel Rich yang sudah didesain Modern & Lebar.
    """
    cleaned_text = clean_markdown_text(text)

    md = Markdown(
        cleaned_text,
        code_theme=THEME_CODE_BLOCK, 
        inline_code_lexer="python", 
        hyperlinks=True,
        justify="left" 
    )

    panel = Panel(
        md,
        title=f"[bold cyan]{title}[/]",
        title_align="left",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
        expand=True 
    )

    return panel