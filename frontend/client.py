import requests
import sys
import time
import os
import json
import random
import msvcrt
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.rule import Rule
from rich.live import Live
from rich.markdown import Markdown
from rich import box
from rich.layout import Layout
from rich.table import Table
from rich.syntax import Syntax

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

    # Premium Minimalist Style Prompt
    input_style = PromptStyle.from_dict({
        'prompt': '#cba6f7 bold',       # Lavender
        'username': '#89b4fa',          # Blue
        'at': '#6c7086',                # Overlay0
        'host': '#a6e3a1',              # Green
        'colon': '#9399b2',             # Overlay2
        'input': '#cdd6f4',             # Text
        'bottom-toolbar': '#1e1e2e bg:#cba6f7', # Inverse
    })
    session = PromptSession(history=InMemoryHistory(), style=input_style)
    USE_PROMPT_TOOLKIT = True

except Exception:
    USE_PROMPT_TOOLKIT = False
    session = None

# --- KONFIGURASI ---
API_URL = "http://127.0.0.1:5000/chat"
MODELS_URL = "http://127.0.0.1:5000/models"
SET_MODEL_URL = "http://127.0.0.1:5000/model/set"

console = Console()

# THEME COLORS (PREMIUM MINIMALIST PALETTE)
C_PRIMARY = "bright_magenta"    # Lavender/Purple (#cba6f7)
C_SECONDARY = "dodger_blue2"    # Blue (#89b4fa)
C_ACCENT = "spring_green1"      # Green (#a6e3a1)
C_WARNING = "gold1"             # Yellow (#f9e2af)
C_ERROR = "red1"                # Red (#f38ba8)
C_DIM = "grey35"                # Overlay (#6c7086)
C_TEXT = "white"                # Text (#cdd6f4)

# GLOBAL STATE
CURRENT_MODEL = "Unknown"

def show_intro():
    # Aggressive Clear to wipe history
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Minimalist Fade-in Logo
    logo_text = "L U M I N O"
    version_text = "v4.5"
    
    console.print()
    console.print()
    
    # Simple elegant header
    console.print(Align.center(Text(logo_text, style=f"bold {C_PRIMARY}")))
    console.print(Align.center(Text(f"Intelligence Interface {version_text}", style=f"dim {C_TEXT}")))
    
    console.print()
    console.print(Align.center(Rule(style=f"dim {C_DIM}", characters="─")))
    console.print()

def handle_model_switch():
    """Interactive Model Switcher (Client-Side UI)"""
    global CURRENT_MODEL
    try:
        # 1. Fetch Models
        response = requests.get(MODELS_URL)
        response.raise_for_status()
        available_models = response.json().get("models", [])
        
        if not available_models:
            console.print(f"[{C_ERROR}]No models found on server.[/]")
            return

        selected_index = 0
        total_options = len(available_models)

        # 2. Interactive Menu Loop
        while True:
            # Aggressive Clear
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print()
            console.print()
            
            # Header
            console.print(Align.center(Text("SELECT MODEL", style=f"bold {C_TEXT}")))
            console.print(Align.center(Text("Choose your intelligence engine", style=f"dim {C_DIM}")))
            console.print()

            # --- RENDER PILIHAN (GRID) ---
            grid = Table.grid(expand=True, padding=(0, 2))
            for _ in range(total_options):
                grid.add_column(justify="center", ratio=1)

            row_panels = []
            for idx, filename in enumerate(available_models):
                is_selected = (idx == selected_index)
                
                if is_selected:
                    border_col = C_PRIMARY
                    box_type = box.ROUNDED
                    name_style = f"bold {C_PRIMARY}"
                else:
                    border_col = C_DIM
                    box_type = box.ROUNDED
                    name_style = f"dim {C_TEXT}"

                # Minimalist Card
                card = Panel(
                    Align.center(
                        Text(filename, style=name_style)
                    ),
                    border_style=border_col,
                    box=box_type,
                    width=30,
                    padding=(1,1)
                )
                row_panels.append(card)

            # Handle grid rows if too many models (wrap)
            grid.add_row(*row_panels)

            console.print(Align.center(grid))
            console.print()
            console.print(Align.center(f"[dim {C_DIM}]Use ← → to navigate, ENTER to select[/]"))

            # --- INPUT HANDLING ---
            key = msvcrt.getch()
            if key == b'\xe0': 
                key = msvcrt.getch()
                if key == b'K': # Kiri
                    selected_index = (selected_index - 1) % total_options
                elif key == b'M': # Kanan
                    selected_index = (selected_index + 1) % total_options
            elif key == b'\r': # Enter
                break
            elif key == b'\x03': # Ctrl+C
                return

        # 3. Send Selection to Server
        selected_model = available_models[selected_index]
        
        console.print()
        with console.status(f"[dim]Switching to {selected_model}...[/]", spinner="dots", spinner_style=C_PRIMARY):
            resp = requests.post(SET_MODEL_URL, json={"model": selected_model})
            resp.raise_for_status()
            
        # Update Global State
        CURRENT_MODEL = selected_model.replace(".gguf", "").title()
        
        # Clear screen back to intro (Clean Look)
        show_intro()
        # No persistent print!

    except Exception as e:
        console.print(f"[{C_ERROR}]Model switch failed: {e}[/]")
        time.sleep(2)

def show_help():
    console.print()
    grid = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    grid.add_column("Command", style=f"bold {C_PRIMARY}", justify="right")
    grid.add_column("Description", style=f"dim {C_TEXT}")
    
    grid.add_row("/model", "Switch AI Model")
    grid.add_row("/paste", "Paste Mode")
    grid.add_row("/help", "Show Help")
    grid.add_row("exit", "Quit")
    
    panel = Panel(
        Align.center(grid),
        title="[bold]COMMANDS[/]",
        border_style=C_DIM,
        box=box.ROUNDED,
        width=60
    )
    console.print(Align.center(panel))
    console.print()

def get_multiline_input():
    """Mode Input Khusus Paste"""
    console.print()
    console.print(Align.center(f"[{C_WARNING}]Paste Mode[/] [dim](Type 'END' to send)[/]"))
    
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
    return full_text

def get_bottom_toolbar():
    # Minimalist hints with Active Model
    return HTML(f" <style fg='#6c7086'> {CURRENT_MODEL} </style> <style fg='#45475a'>|</style> <style fg='#6c7086'> /help </style> ")

def get_user_input():
    """Wrapper cerdas untuk menangani input"""
    console.print() 
    
    if USE_PROMPT_TOOLKIT and session:
        try:
            # Minimalist Prompt: ● 
            return session.prompt(
                HTML(f"<style fg='{C_PRIMARY}'>●</style> "),
                bottom_toolbar=get_bottom_toolbar
            )
        except Exception:
            return Prompt.ask(f"[{C_PRIMARY}]●[/]")
    else:
        return Prompt.ask(f"[{C_PRIMARY}]●[/]")

def create_hud_panel(content, title=None, border_style=C_DIM, subtitle=None):
    return Panel(
        content,
        border_style=border_style,
        box=box.ROUNDED, 
        padding=(1, 2),
        subtitle=subtitle,
        subtitle_align="right"
    )

def get_smart_tail(full_text, max_lines=30):
    """
    Mengambil N baris terakhir dari teks, tapi tetap menjaga konteks Markdown (Code Block).
    """
    lines = full_text.splitlines()
    if len(lines) <= max_lines:
        return full_text
    
    # Ambil tail
    tail_lines = lines[-max_lines:]
    prefix_lines = lines[:-max_lines]
    prefix_text = "\n".join(prefix_lines)
    
    # Cek status Code Block di prefix
    # Hitung jumlah ```
    code_block_markers = prefix_text.count("```")
    in_code_block = (code_block_markers % 2 != 0)
    
    if in_code_block:
        # Kita ada di dalam code block yang terpotong.
        # Cari bahasa dari block terakhir di prefix
        last_marker_idx = prefix_text.rfind("```")
        # Ambil baris setelah marker
        marker_line_end = prefix_text.find("\n", last_marker_idx)
        if marker_line_end == -1: marker_line_end = len(prefix_text)
        
        lang_tag = prefix_text[last_marker_idx+3 : marker_line_end].strip()
        
        # Tambahkan header block buatan di awal tail
        return f"``` {lang_tag} (continued)...\n" + "\n".join(tail_lines)
    else:
        return "\n".join(tail_lines)

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
                    continue
                    
            elif user_input.strip().lower() == '/model':
                handle_model_switch()
                continue 
            
            elif user_input.strip().lower() == '/help':
                show_help()
                continue

            elif user_input.lower() in ['exit', 'quit']:
                console.print(f"\n[{C_DIM}]Shutting down...[/]")
                break

            # Kirim ke Server dengan STREAMING
            try:
                start_time = time.time()
                
                payload = {"message": user_input, "stream": True}
                
                full_response = ""
                files_read = []
                token_stats = None
                
                with requests.post(API_URL, json=payload, stream=True) as response:
                    response.raise_for_status()
                    
                    # OPTIMIZED: Token batching for better CPU efficiency
                    with Live(create_hud_panel(Align.center(Text("Processing...", style=f"dim {C_PRIMARY}"))), 
                              console=console, 
                              refresh_per_second=6,  # Balanced refresh rate
                              vertical_overflow="visible",
                              screen=True) as live:
                        try:
                            token_count = 0
                            for line in response.iter_lines():
                                if line:
                                    try:
                                        chunk = json.loads(line.decode('utf-8'))
                                        
                                        if chunk['type'] == 'token':
                                            token = chunk['content']
                                            full_response += token
                                            token_count += 1
                                            
                                            # Update every 3 tokens for better performance
                                            if token_count % 3 == 0:
                                                safe_height = console.height - 10 
                                                if safe_height < 10: safe_height = 10
                                                
                                                # Ambil Smart Tail
                                                render_text = get_smart_tail(full_response, max_lines=safe_height)
                                                
                                                # Update Live Panel
                                                live.update(create_hud_panel(
                                                    Markdown(render_text, code_theme="monokai"),
                                                    border_style=C_DIM,
                                                    subtitle="[dim]▼ Auto-scrolling[/]" if len(full_response.splitlines()) > safe_height else None
                                                ))
                                            
                                        elif chunk['type'] == 'usage':
                                            token_stats = chunk.get('stats')
                                            
                                        elif chunk['type'] == 'info':
                                            files_read = chunk.get('files', [])
                                            
                                    except json.JSONDecodeError:
                                        pass
                        except KeyboardInterrupt:
                            full_response += f"\n\n[{C_ERROR}]Interrupted[/]"
                            pass

                    # Final Render (Dilakukan SETELAH screen selesai agar bersih di history utama)
                    end_time = time.time()
                    
                    # Construct Minimalist Footer
                    footer_parts = []
                    
                    if token_stats:
                        t_out = token_stats.get('completion_tokens', 0)
                        if t_out > 0 and (end_time - start_time) > 0:
                            speed = t_out / (end_time - start_time)
                            footer_parts.append(f"{speed:.1f} t/s")
                        footer_parts.append(f"{token_stats.get('total_tokens', 0)} toks")
                    
                    footer = f"[dim]{' · '.join(footer_parts)}[/]" if footer_parts else None
                    
                    final_panel = create_hud_panel(
                        Markdown(full_response, code_theme="monokai"), 
                        border_style=C_DIM, # Keep it subtle
                        subtitle=footer
                    )
                    console.print(final_panel)

                    if files_read:
                        file_list = ", ".join([f"'{f}'" for f in files_read])
                        console.print(f"   [{C_ACCENT}]📎[/][dim] {file_list}[/]")

            except requests.exceptions.ConnectionError:
                console.print(f"[{C_ERROR}]Server Unreachable[/]")
            except Exception as e:
                console.print(f"[{C_ERROR}]Error: {str(e)}[/]")

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            if USE_PROMPT_TOOLKIT:
                USE_PROMPT_TOOLKIT = False
                session = None
                continue
            else:
                console.print(f"\n[{C_ERROR}]Critical Error: {e}[/]")
                break

if __name__ == "__main__":
    run()