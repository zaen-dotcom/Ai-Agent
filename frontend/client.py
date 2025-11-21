import requests
import sys
import time
import os
import json
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.rule import Rule
from rich.live import Live
from rich.markdown import Markdown
from rich import box

# --- 1. SETUP INPUT (SILENT FALLBACK) ---
USE_PROMPT_TOOLKIT = False
session = None

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.styles import Style as PromptStyle
    from prompt_toolkit.formatted_text import HTML
    
    if sys.platform == 'win32':
        from prompt_toolkit.output.win32 import Win32Output
        try:
            _ = Win32Output(sys.stdout)
        except Exception:
            raise ImportError("Not a real Win32 Console")

    input_style = PromptStyle.from_dict({
        'prompt': 'ansicyan bold',
        'input': '#ffffff',
    })
    session = PromptSession(history=InMemoryHistory(), style=input_style)
    USE_PROMPT_TOOLKIT = True

except Exception:
    USE_PROMPT_TOOLKIT = False
    session = None

# --- FORMATTER ---
try:
    from formatter import create_styled_panel
except ImportError:
    def create_styled_panel(text, title):
        return Panel(Markdown(text), title=title)

# --- KONFIGURASI ---
API_URL = "http://127.0.0.1:5000/chat"
RESET_URL = "http://127.0.0.1:5000/reset"

console = Console()
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
    console.print(Align.center(Text("v4.0-stream", style=f"{C_DIM}")))
    console.print("\n")

    if not USE_PROMPT_TOOLKIT:
         console.print(Align.center("[dim yellow]⚠ Compatibility Mode: Basic Input Active[/]"))

    with Progress(
        SpinnerColumn("dots", style=C_ACCENT),
        TextColumn("[white]{task.description}"),
        BarColumn(bar_width=20, style="grey15", complete_style=C_PRIMARY),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Initializing...", total=100)
        for _ in range(4):
            time.sleep(0.1)
            progress.advance(task, 25)

    console.print(Align.center(f"[{C_SUCCESS}]●[/] [{C_DIM}]CONNECTED TO MY BRAIN[/]"))
    console.print(Rule(style=C_DIM))
    console.print()

def handle_reset():
    console.print()
    console.print(Panel(
        Align.center("[bold yellow]⚠ INITIATING HOT-SWAP PROTOCOL...[/]\n[dim]Check Server Window[/]"),
        border_style="yellow",
        width=60
    ))
    try:
        requests.post(RESET_URL, timeout=None) 
        show_intro()
        console.print(f"[{C_SUCCESS}]✔ Module Switched Successfully![/]")
    except Exception as e:
        console.print(f"[bold red]Failed to switch: {e}[/]")

def get_multiline_input():
    """Mode Input Khusus Paste"""
    console.print()
    console.print(Rule("[bold yellow]PASTE MODE ACTIVATED[/]", style="yellow"))
    console.print("[dim]1. Paste teks panjang Anda di bawah ini.[/]")
    console.print("[dim]2. Tekan [bold white]ENTER[/] untuk baris baru.[/]")
    console.print("[dim]3. Ketik [bold yellow]END[/] di baris baru lalu ENTER untuk mengirim.[/]")
    console.print()
    
    lines = []
    while True:
        try:
            line = input() 
            if line.strip().upper() == 'END':
                break
            lines.append(line)
        except EOFError:
            break
            
    full_text = "\n".join(lines)
    console.print(Rule("[bold yellow]PROCESSING DATA[/]", style="yellow"))
    return full_text

def get_user_input():
    """Wrapper cerdas untuk menangani input"""
    console.print() 
    
    if USE_PROMPT_TOOLKIT and session:
        try:
            return session.prompt(HTML("<b>❯ </b>"))
        except Exception:
            return Prompt.ask(f"[bold {C_PRIMARY}]❯[/]")
    else:
        return Prompt.ask(f"[bold {C_PRIMARY}]❯[/]")

def run():
    global USE_PROMPT_TOOLKIT, session 
    
    show_intro()

    while True:
        try:
            # Ambil input
            user_input = get_user_input()
            
            if not user_input.strip():
                continue
            
            # Command Handling
            if user_input.strip().lower() == '/paste':
                user_input = get_multiline_input()
                if not user_input.strip():
                    console.print("[dim]Paste cancelled.[/]")
                    continue
                    
            elif user_input.strip().lower() == '/model':
                handle_reset()
                continue 
                
            elif user_input.lower() in ['exit', 'quit']:
                console.print(f"\n[bold {C_DIM}]Closing connection...[/]")
                break

            # Kirim ke Server dengan STREAMING
            try:
                start_time = time.time()
                
                payload = {"message": user_input, "stream": True}
                
                full_response = ""
                files_read = []
                
                with requests.post(API_URL, json=payload, stream=True) as response:
                    response.raise_for_status()
                    
                    # Siapkan Panel Live
                    live_panel = Panel(
                        "", 
                        title="Lumino [dim](Thinking...)[/]", 
                        border_style=C_ACCENT,
                        box=box.ROUNDED,
                        padding=(1, 2)
                    )
                    
                    with Live(live_panel, console=console, refresh_per_second=10, transient=True) as live:
                        try:
                            for line in response.iter_lines():
                                if line:
                                    try:
                                        chunk = json.loads(line.decode('utf-8'))
                                        
                                        if chunk['type'] == 'token':
                                            token = chunk['content']
                                            full_response += token
                                            
                                            live.update(Panel(
                                                Markdown(full_response),
                                                title="Lumino [dim](Streaming...)[/]",
                                                border_style=C_ACCENT,
                                                box=box.ROUNDED,
                                                padding=(1, 2)
                                            ))
                                            
                                        elif chunk['type'] == 'info':
                                            files_read = chunk.get('files', [])
                                            
                                    except json.JSONDecodeError:
                                        pass
                        except KeyboardInterrupt:
                            full_response += "\n\n[bold red]⛔ Interrupted by User[/]"
                            live.update(Panel(
                                Markdown(full_response),
                                title="Lumino [dim](Stopped)[/]",
                                border_style="red",
                                box=box.ROUNDED,
                                padding=(1, 2)
                            ))
                            pass

                    # Final Render
                    end_time = time.time()
                    latency = (end_time - start_time) * 1000
                    
                    final_panel = create_styled_panel(full_response, title=f"Lumino [dim]({latency:.0f}ms)[/]")
                    console.print(final_panel)

                    if files_read:
                        file_list = ", ".join([f"'{f}'" for f in files_read])
                        console.print(f"   [{C_ACCENT}]└─ 📎 References:[/][dim] {file_list}[/]")

            except requests.exceptions.ConnectionError:
                console.print(Panel(f"[bold red]Connection Lost[/]\nServer unreachable.", style="red"))
            except Exception as e:
                console.print(Panel(f"[bold red]Error[/]\n{str(e)}", style="red"))

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            if USE_PROMPT_TOOLKIT:
                console.print(f"\n[dim yellow]⚠ Input Error ({e}). Switching to Basic Mode...[/]")
                USE_PROMPT_TOOLKIT = False
                session = None
                continue
            else:
                console.print(f"\n[bold red]Critical Error:[/][white] {e}[/]")
                break

if __name__ == "__main__":
    run()