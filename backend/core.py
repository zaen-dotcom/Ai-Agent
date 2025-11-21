import time
import sys
import os
import gc
import random
import msvcrt

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.layout import Layout
from rich import box

from llama_cpp import Llama

# --- IMPORT KONFIGURASI BARU ---
from backend import config
from backend.config import ModelConfig

# --- PEREDAM SUARA ---
class SuppressFactory:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._devnull = open(os.devnull, 'w', encoding='utf-8')
        sys.stdout = self._devnull
        sys.stderr = self._devnull
        try:
            self._orig_fd1 = os.dup(1)
            self._orig_fd2 = os.dup(2)
            os.dup2(self._devnull.fileno(), 1)
            os.dup2(self._devnull.fileno(), 2)
        except:
            self._orig_fd1 = None
            self._orig_fd2 = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._orig_fd1 is not None:
            os.dup2(self._orig_fd1, 1)
            os.close(self._orig_fd1)
        if self._orig_fd2 is not None:
            os.dup2(self._orig_fd2, 2)
            os.close(self._orig_fd2)
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        self._devnull.close()

console = Console()

# --- FUNGSI PEMBERSIH LAYAR PAKSA ---
def force_clear():
    """Membersihkan layar menggunakan perintah OS (Pasti bersih)"""
    console.clear()
    os.system('cls' if os.name == 'nt' else 'clear')

class AIEngine:
    def __init__(self):
        self.model = None
        self.active_config = None
        self.history = [] # Context Memory
        
        # 1. Pilih Mode
        self._select_module_interactive()
        
        # 2. Load Model
        self.load_model()

    def switch_model(self):
        """Fungsi untuk Hot-Swap via command /model"""
        self._select_module_interactive()
        self.load_model()
        self.history = [] # Reset history on model switch

    def _select_module_interactive(self):
        """Menu Interaktif Dinamis"""
        
        available_models = config.get_available_models()
        if not available_models:
            console.print("[bold red]No models found in 'models/' directory![/]")
            sys.exit(1)

        selected_index = 0
        total_options = len(available_models)

        while True:
            force_clear()
            console.print()
            
            # Header
            console.print(Align.center("[bold white]LUMINO[/][dim] INTELLIGENCE SYSTEM[/]"))
            console.print(Rule(style="dim grey15"))
            console.print()

            # --- RENDER PILIHAN (GRID) ---
            grid = Table.grid(expand=True, padding=(0, 2))
            for _ in range(total_options):
                grid.add_column(justify="center", ratio=1)

            row_panels = []
            for idx, filename in enumerate(available_models):
                is_selected = (idx == selected_index)
                
                # Instantiate config temporarily to get metadata
                temp_config = ModelConfig(filename)
                
                if is_selected:
                    border_col = "cyan"
                    title_style = "bold black on cyan"
                    box_type = box.ROUNDED
                else:
                    border_col = "grey23"
                    title_style = "dim white on grey15"
                    box_type = box.ROUNDED

                content = Text.assemble(
                    (f"\n {temp_config.icon} {temp_config.name} \n", title_style),
                    (f"\n{temp_config.description}", "dim white")
                )
                row_panels.append(Panel(content, border_style=border_col, box=box_type, width=35, padding=(0,0)))

            # Handle grid rows if too many models (wrap)
            # For simplicity assuming < 4 models for now, or horizontal scroll
            grid.add_row(*row_panels)

            main_panel = Panel(
                grid,
                title="[bold white]SELECT NEURAL MODULE[/]",
                subtitle="[dim]← Switch →   |   ENTER Confirm[/]",
                border_style="grey11",
                box=box.HORIZONTALS,
                padding=(2, 2),
                width=100
            )
            console.print(Align.center(main_panel))

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
        
        # SET CONFIG
        selected_filename = available_models[selected_index]
        self.active_config = ModelConfig(selected_filename)
        
        # Feedback visual
        console.print(f"\n[dim]Booting module:[/][bold cyan] {self.active_config.name}[/]")
        time.sleep(0.4)
        force_clear()

    def _print_specs(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="right")
        
        grid.add_row("[dim]Active Module[/]", f"[bold cyan]{self.active_config.name}[/]") 
        grid.add_row("[dim]Architecture[/]", f"[bold cyan]{self.active_config.type.upper()}[/]") 
        grid.add_row("[dim]Context Size[/]", f"[white]{self.active_config.init_params['n_ctx']}[/]")
        grid.add_row("[dim]Threads[/]", f"[white]{self.active_config.init_params['n_threads']}[/]")

        panel = Panel(
            grid,
            title="[bold cyan]SYSTEM DIAGNOSTICS[/]",
            title_align="left",
            border_style="dim cyan", 
            box=box.ROUNDED,        
            padding=(0, 2),
            width=70                
        )
        console.print(Align.center(panel))

    def load_model(self):
        force_clear()
        console.print()
        console.print(Align.center("[bold white]LUMINO[/][dim] INTELLIGENCE SYSTEM[/]"))
        console.print(Rule(style="dim grey23"))
        console.print()

        # CLEANUP MEMORY
        if self.model is not None:
            del self.model
            self.model = None
            gc.collect()
            time.sleep(1)

        tasks = [
            f"Initializing {self.active_config.name}...",
            "Verifying Environment...",
            "Loading Tensor Weights...",
            "Optimizing Context Window...",
            "System Ready."
        ]

        with Progress(
            SpinnerColumn("dots", style="bold cyan"), 
            TextColumn("[white]{task.description}"),
            BarColumn(bar_width=40, style="grey23", complete_style="cyan"), 
            console=console,
            transient=True 
        ) as progress:
            task = progress.add_task("Booting...", total=100)
            chunk = 100 / len(tasks)
            for desc in tasks:
                progress.update(task, description=desc)
                time.sleep(random.uniform(0.1, 0.3))
                progress.advance(task, chunk)

        self._print_specs()
        console.print()

        try:
            with console.status("[dim]Establishing secure connection to neural core...[/]", spinner="arc", spinner_style="cyan"):
                with SuppressFactory():
                    self.model = Llama(**self.active_config.init_params)
        except Exception as e:
            console.print(f"[bold red]Error:[/][white] {e}[/]")
            return 
        
        self._print_signature()
        time.sleep(2)

    def _print_signature(self):
        grid = Table.grid(padding=(0, 0), expand=True)
        grid.add_column(justify="center")
        status_line = Text.assemble(("● SYSTEM ONLINE", "bold green"),(" | Latency: 0ms", "dim white"))
        grid.add_row(status_line)
        grid.add_row(Text(" ", style="dim white"))
        creator_line = Text.assemble(("Architect: ", "dim white"),(" FADIL ", "bold white on cyan"))
        grid.add_row(creator_line)
        panel = Panel(Align.center(grid), box=box.ROUNDED, border_style="cyan", padding=(0, 2), width=60)
        console.print(Align.center(panel))
        console.print()

    def generate_response(self, user_input, stream=False):
        if not self.model: return "Error: Neural Core not active."

        # 1. Update History
        current_message = {"role": "user", "content": user_input}
        
        # 2. Prepare Messages for Chat Completion
        messages = list(self.history) # Copy existing history
        messages.append(current_message)
        self.history.append(current_message)

        # 3. Generate using create_chat_completion (High-level API)
        try:
            # Filter out parameters not supported by create_chat_completion (like 'echo')
            gen_params = self.active_config.gen_params.copy()
            if "echo" in gen_params:
                del gen_params["echo"]

            output = self.model.create_chat_completion(
                messages=messages,
                stream=stream,
                **gen_params
            )
            
            if stream:
                # Generator wrapper to capture full response for history
                full_response = ""
                for chunk in output:
                    delta = chunk['choices'][0]['delta']
                    if 'content' in delta:
                        text_chunk = delta['content']
                        full_response += text_chunk
                        yield text_chunk
                
                # Append assistant response to history after streaming is done
                self.history.append({"role": "assistant", "content": full_response})
                
            else:
                text_response = output['choices'][0]['message']['content']
                self.history.append({"role": "assistant", "content": text_response})
                return text_response

        except Exception as e:
            return f"Runtime Logic Error: {str(e)}"

engine = AIEngine()