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
import colorsys

# --- FORMATTER ---
try:
    from formatter import create_styled_panel
except ImportError:
    def create_styled_panel(text, title):
        from rich.markdown import Markdown
        return Panel(Markdown(text), title=title)

# --- KONFIGURASI ---
API_URL = "http://127.0.0.1:5000/chat"
RESET_URL = "http://127.0.0.1:5000/reset" # Endpoint Baru

console = Console()

# Warna
C_PRIMARY = "dodger_blue1"
C_ACCENT  = "cyan"
C_DIM     = "grey58"
C_SUCCESS = "green"

def get_gradient_color(start_rgb, end_rgb, fraction):
    r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * fraction)
    g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * fraction)
    b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * fraction)
    return f"#{r:02x}{g:02x}{b:02x}"

def show_intro():
    console.clear()
    logo = """
 ██╗     ██╗   ██╗███╗    ███╗██╗███╗    ██╗ ██████╗ 
 ██║     ██║   ██║████╗  ████║██║████╗   ██║██╔═══██╗
 ██║     ██║   ██║██╔████╔██║██║██╔██╗  ██║██║   ██║
 ██║     ██║   ██║██║╚██╔╝██║██║██║╚██╗██║██║   ██║
 ███████╗╚██████╔╝██║ ╚═╝ ██║██║██║ ╚████║╚██████╔╝
 ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
    """
    start_rgb = (0, 70, 150)
    end_rgb = (0, 200, 255)
    logo_lines = logo.strip().split('\n')
    
    console.print()
    for i, line in enumerate(logo_lines):
        fraction = i / (len(logo_lines) - 1) if len(logo_lines) > 1 else 0
        gradient_color = get_gradient_color(start_rgb, end_rgb, fraction)
        console.print(Align.center(Text(line, style=f"bold {gradient_color}")))
    
    console.print(Align.center(Text("AI INTELLIGENCE CORE", style=f"bold {C_DIM} tracking=1")))
    console.print(Align.center(Text("v2.5-pro", style=f"{C_DIM}")))
    console.print("\n")

    with Progress(
        SpinnerColumn("dots", style=C_ACCENT),
        TextColumn("[white]{task.description}"),
        BarColumn(bar_width=20, style="grey15", complete_style=C_PRIMARY),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Init...", total=100)
        for _ in range(4):
            time.sleep(0.1)
            progress.advance(task, 25)

    console.print(Align.center(f"[{C_SUCCESS}]●[/] [{C_DIM}]CONNECTED TO MY BRAIN[/]"))
    console.print(Rule(style=C_DIM))
    console.print()

def handle_reset():
    """Menangani logika ganti model"""
    console.print()
    console.print(Panel(
        Align.center("[bold yellow]⚠ INITIATING HOT-SWAP PROTOCOL...[/]\n[dim]Please interact with the Server Menu[/]"),
        border_style="yellow",
        width=60
    ))
    
    try:
        # Kirim request ke server untuk reset
        # Timeout=None karena user mungkin lama milih di menu
        response = requests.post(RESET_URL, timeout=None) 
        response.raise_for_status()
        
        # Jika sukses, bersihkan layar dan tampilkan intro lagi
        show_intro()
        console.print(f"[{C_SUCCESS}]Module Switched Successfully![/]")
        
    except Exception as e:
        console.print(f"[bold red]Failed to switch model: {e}[/]")

def run():
    show_intro()

    while True:
        try:
            console.print()
            user_input = Prompt.ask(f"[bold {C_PRIMARY}]❯[/]")
            
            if not user_input.strip():
                continue
            
            # --- CEK COMMAND KHUSUS ---
            if user_input.strip().lower() == '/model':
                handle_reset()
                continue # Skip proses chat, kembali ke loop awal

            if user_input.lower() in ['exit', 'quit']:
                console.print(f"\n[bold {C_DIM}]Closing connection...[/]")
                break

            # Proses Chat Normal
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
                    console.print(Panel(f"[bold red]Connection Lost[/]\nServer might be restarting...", style="red"))
                except Exception as e:
                    console.print(Panel(f"[bold red]System Error[/]\n{str(e)}", style="red"))

        except KeyboardInterrupt:
            console.print(f"\n[{C_DIM}]Session terminated.[/]")
            break

if __name__ == "__main__":
    run()