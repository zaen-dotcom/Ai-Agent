import requests
import sys
import time
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.markdown import Markdown
from rich.rule import Rule  # <-- Ini yang tadi kurang
from rich import box

# --- KONFIGURASI UI ---
# API URL harus sama dengan port di main.py
API_URL = "http://127.0.0.1:5000/chat"

console = Console()

# Palet Warna Cyberpunk/Modern
C_USER = "green"
C_AI = "cyan"
C_ACCENT = "bright_cyan"
C_DIM = "grey50"
C_ERROR = "red"

def show_intro():
    """Menampilkan Intro Loading saat client pertama kali dipanggil oleh main.py"""
    console.clear()
    
    # Logo ASCII
    logo = """
    ██╗     ██╗   ██╗███╗   ███╗██╗███╗   ██╗ ██████╗ 
    ██║     ██║   ██║████╗ ████║██║████╗  ██║██╔═══██╗
    ██║     ██║   ██║██╔████╔██║██║██╔██╗ ██║██║   ██║
    ██║     ██║   ██║██║╚██╔╝██║██║██║╚██╗██║██║   ██║
    ███████╗╚██████╔╝██║ ╚═╝ ██║██║██║ ╚████║╚██████╔╝
    ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
    """
    
    console.print(Align.center(Text(logo, style=f"bold {C_AI}")))
    console.print(Align.center(Text("SYSTEM INITIALIZED via MAIN CORE", style=f"bold {C_DIM} tracking=3")))
    console.print("\n")

    # Animasi Loading (Hiasan visual)
    with Progress(
        SpinnerColumn(style=C_ACCENT),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=30, style=C_AI, complete_style=C_ACCENT),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Establishing Uplink...", total=100)
        for _ in range(25):
            time.sleep(0.02)
            progress.advance(task, 4)

    console.print(Align.center(Text("● CONNECTED TO MY BRAIN", style="bold green")))
    console.print(Rule(style=C_DIM))
    console.print("\n")

def print_ai_message(markdown_text, context_files=None):
    """Render pesan AI dengan panel modern"""
    md_content = Markdown(markdown_text)
    
    subtitle = None
    if context_files:
        files_str = ", ".join(context_files)
        subtitle = f"[dim]Context: {files_str}[/]"

    ai_panel = Panel(
        md_content,
        box=box.ROUNDED,
        border_style=C_AI,
        title=f"[bold {C_ACCENT}]⚡ Lumino[/]",
        subtitle=subtitle,
        subtitle_align="right",
        title_align="left",
        padding=(1, 2),
        expand=True
    )
    console.print(ai_panel)
    console.print() # Spasi bawah

def run():
    """Fungsi utama yang dipanggil oleh main.py"""
    # Tampilkan intro
    show_intro()

    while True:
        try:
            # 1. Input User Modern
            user_input = Prompt.ask(f"[bold {C_ACCENT}]❯[/] Input")
            
            # Cek command exit
            if user_input.lower() in ['exit', 'quit']:
                console.print(f"\n[bold {C_DIM}]Terminating Session...[/]")
                break
            
            if not user_input.strip():
                continue

            # 2. Loading State & Request ke Server
            # Menggunakan spinner aesthetic kotak-kotak
            with console.status(f"[bold {C_DIM}]Processing...[/]", spinner="aesthetic"):
                try:
                    payload = {"message": user_input}
                    # Request ke server Flask yang dijalankan main.py
                    response = requests.post(API_URL, json=payload)
                    response.raise_for_status()
                    
                    data = response.json()
                    bot_reply = data.get("response", "")
                    files_read = data.get("files_read", [])

                    # 3. Tampilkan Balasan
                    print_ai_message(bot_reply, files_read)

                except requests.exceptions.ConnectionError:
                    # Error khusus jika server Flask di main.py belum siap/mati
                    console.print(f"[bold red]Error:[/][dim] Cannot connect to server at {API_URL}.[/]")
                    console.print("[dim]Ensure Flask server in main.py is running.[/]")
                
                except Exception as e:
                    console.print(f"[bold red]Error:[/][dim] {e}[/]")

        except KeyboardInterrupt:
            console.print(f"\n[{C_DIM}]Interrupted by User.[/]")
            break

# Blok ini hanya jalan jika client.py dijalankan sendiri (testing)
if __name__ == "__main__":
    run()