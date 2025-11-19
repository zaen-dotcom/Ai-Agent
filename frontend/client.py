import requests
import sys
import time
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.rule import Rule
from rich import box
import colorsys # Untuk membuat gradasi warna

# --- IMPORT FORMATTER CANGGIH (Yang sudah kita buat) ---
# Ini menjamin Tabel & Matematika tampil sempurna
try:
    from formatter import create_styled_panel
except ImportError:
    # Fallback jika file formatter.py belum ada/salah nama
    def create_styled_panel(text, title):
        from rich.markdown import Markdown
        return Panel(Markdown(text), title=title)

# --- KONFIGURASI ---
API_URL = "http://127.0.0.1:5000/chat"
console = Console()

# Palet Warna (Professional Tech Theme)
C_PRIMARY = "dodger_blue1"   # Biru Profesional
C_ACCENT  = "cyan"           # Aksen Tech
C_TEXT    = "white"          # Teks Utama
C_DIM     = "grey58"         # Teks Info
C_SUCCESS = "green"

# --- FUNGSI UNTUK GENERATE GRADASI WARNA ---
def get_gradient_color(start_rgb, end_rgb, fraction):
    """Menghasilkan warna RGB di antara dua warna berdasarkan fraksi (0.0-1.0)"""
    r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * fraction)
    g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * fraction)
    b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * fraction)
    return f"#{r:02x}{g:02x}{b:02x}"

def show_intro():
    """Menampilkan Intro Loading dengan Logo Gradasi"""
    console.clear()
    
    # Logo ASCII
    logo = """
 ██╗     ██╗   ██╗███╗    ███╗██╗███╗    ██╗ ██████╗ 
 ██║     ██║   ██║████╗  ████║██║████╗   ██║██╔═══██╗
 ██║     ██║   ██║██╔████╔██║██║██╔██╗  ██║██║   ██║
 ██║     ██║   ██║██║╚██╔╝██║██║██║╚██╗██║██║   ██║
 ███████╗╚██████╔╝██║ ╚═╝ ██║██║██║ ╚████║╚██████╔╝
 ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
    """
    
    # Warna awal dan akhir untuk gradasi (RGB tuples)
    # rich.color.Color bisa membantu di sini, tapi kita pakai manual dulu
    start_rgb = (0, 70, 150)  # Dark Blue
    end_rgb = (0, 200, 255)  # Bright Cyan

    logo_lines = logo.strip().split('\n')
    num_lines = len(logo_lines)

    console.print() # Spasi atas
    for i, line in enumerate(logo_lines):
        # Hitung fraksi untuk setiap baris
        fraction = i / (num_lines - 1) if num_lines > 1 else 0
        gradient_color = get_gradient_color(start_rgb, end_rgb, fraction)
        console.print(Align.center(Text(line, style=f"bold {gradient_color}")))
    
    console.print(Align.center(Text("AI INTELLIGENCE CORE", style=f"bold {C_DIM} tracking=1")))
    console.print(Align.center(Text("v1.0.4-stable", style=f"{C_DIM}"))) # Versi di bawah logo
    console.print("\n")

    # System Check Animation (Cepat & Informatif)
    steps = [
        "Resolving local endpoints...",
        "Verifying security handshake...",
        "Syncing context buffer...",
        "Connection established."
    ]

    with Progress(
        SpinnerColumn("dots", style=C_ACCENT),
        TextColumn("[white]{task.description}"),
        BarColumn(bar_width=20, style="grey15", complete_style=C_PRIMARY),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task("Init...", total=100)
        
        chunk = 100 / len(steps)
        for step in steps:
            progress.update(task, description=step)
            time.sleep(0.15)
            progress.advance(task, chunk)

    # Status Akhir
    console.print(Align.center(f"[{C_SUCCESS}]●[/] [{C_DIM}]CONNECTED TO MY BRAIN[/]"))
    console.print(Rule(style=C_DIM))
    console.print()

def run():
    """Main Loop"""
    show_intro()

    while True:
        try:
            console.print()
            user_input = Prompt.ask(f"[bold {C_PRIMARY}]❯[/]")
            
            if not user_input.strip():
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                console.print(f"\n[bold {C_DIM}]Closing connection...[/]")
                break

            with console.status(f"[bold {C_DIM}]Thinking...[/]", spinner="dots", spinner_style=C_PRIMARY):
                try:
                    payload = {"message": user_input}
                    
                    start_time = time.time()
                    response = requests.post(API_URL, json=payload)
                    end_time = time.time()
                    
                    response.raise_for_status()
                    
                    data = response.json()
                    bot_reply = data.get("response", "")
                    files_read = data.get("files_read", [])
                    
                    latency = (end_time - start_time) * 1000

                    panel_title = f"Lumino [dim]({latency:.0f}ms)[/]"
                    
                    final_panel = create_styled_panel(bot_reply, title=panel_title)
                    console.print(final_panel)

                    if files_read:
                        file_list = ", ".join([f"'{f}'" for f in files_read])
                        console.print(f"   [{C_ACCENT}]└─ 📎 References:[/][dim] {file_list}[/]")

                except requests.exceptions.ConnectionError:
                    console.print(Panel(f"[bold red]Connection Lost[/]\nCannot reach {API_URL}", style="red"))
                except Exception as e:
                    console.print(Panel(f"[bold red]System Error[/]\n{str(e)}", style="red"))

        except KeyboardInterrupt:
            console.print(f"\n[{C_DIM}]Session terminated by user.[/]")
            break

if __name__ == "__main__":
    run()