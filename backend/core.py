import time
import sys
import os
import random
import msvcrt  # Library khusus Windows untuk input keyboard

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

# --- IMPORT KEDUA KONFIGURASI ---
from backend import config as config_coding
try:
    from backend import config_llama as config_general
except ImportError:
    config_general = config_coding 

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
    # Coba perintah Rich dulu
    console.clear()
    # Paksa perintah OS (Windows 'cls', Linux/Mac 'clear')
    os.system('cls' if os.name == 'nt' else 'clear')

class AIEngine:
    def __init__(self):
        self.model = None
        self.active_config = None
        self.mode_name = ""
        self.model_label = ""
        
        # 1. Pilih Mode
        self._select_module_interactive()
        
        # 2. Load Model
        self.load_model()

    def _select_module_interactive(self):
        """Menu Interaktif dengan Navigasi Panah"""
        
        selected_index = 1 
        
        while True:
            # Gunakan force_clear di sini agar tidak menumpuk saat refresh
            force_clear()
            console.print()
            
            # Header
            console.print(Align.center("[bold white]LUMINO[/][dim] INTELLIGENCE SYSTEM[/]"))
            console.print(Rule(style="dim grey23"))
            console.print()

            # --- RENDER PILIHAN ---
            grid = Table.grid(expand=True, padding=(1, 2))
            grid.add_column(justify="center", ratio=1)
            grid.add_column(justify="center", ratio=1)

            # --- STYLE LOGIC ---
            if selected_index == 0:
                style_gen_box = "bold white on cyan"
                style_gen_text = "bold cyan"
                icon_gen = "●"
                border_gen = "cyan"
            else:
                style_gen_box = "dim white"
                style_gen_text = "dim white"
                icon_gen = "○"
                border_gen = "grey23"

            if selected_index == 1:
                style_cod_box = "bold white on green"
                style_cod_text = "bold green"
                icon_cod = "●"
                border_cod = "green"
            else:
                style_cod_box = "dim white"
                style_cod_text = "dim white"
                icon_cod = "○"
                border_cod = "grey23"

            # Konten Panel Kiri
            txt_gen = Text.assemble(
                (f"\n{icon_gen} GENERAL KNOWLEDGE\n", style_gen_box),
                ("\nXXXXXXXXXXX", style_gen_text)
            )
            panel_gen = Panel(txt_gen, border_style=border_gen, box=box.ROUNDED)

            # Konten Panel Kanan
            txt_cod = Text.assemble(
                (f"\n{icon_cod} CODING, ALGORITHM, LOGIC\n", style_cod_box),
                ("\nXXXXXXXXXXX", style_cod_text)
            )
            panel_cod = Panel(txt_cod, border_style=border_cod, box=box.ROUNDED)

            grid.add_row(panel_gen, panel_cod)

            # Panel Utama Pembungkus
            main_panel = Panel(
                grid,
                title="[bold white]SELECT NEURAL MODULE[/]",
                subtitle="[dim]Use ← Left / Right → to Switch, ENTER to Confirm[/]",
                border_style="white",
                box=box.ROUNDED,
                padding=(1, 2),
                width=80
            )
            console.print(Align.center(main_panel))

            # --- INPUT HANDLING ---
            key = msvcrt.getch()
            
            if key == b'\xe0': 
                key = msvcrt.getch()
                if key == b'K': 
                    selected_index = 0
                elif key == b'M': 
                    selected_index = 1
            elif key == b'\r': 
                break 
        
        # SET CONFIG
        if selected_index == 0:
            self.active_config = config_general
            self.mode_name = "GENERAL KNOWLEDGE"
            self.model_label = "Llama 3.1 Instruct"
        else:
            self.active_config = config_coding
            self.mode_name = "CODING & ARCHITECTURE"
            self.model_label = "Qwen 2.5 Coder"
            
        # Feedback singkat
        console.print(f"\n[dim]Module selected:[/][bold cyan] {self.mode_name}[/]")
        time.sleep(0.4)

        # --- BERSIHKAN LAYAR TOTAL SEBELUM MASUK LOADING ---
        force_clear()

    def _print_specs(self):
        """Tabel Spesifikasi"""
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="right")
        
        grid.add_row("[dim]Active Module[/]", f"[bold cyan]{self.mode_name}[/]") 
        grid.add_row("[dim]Model Architecture[/]", "[bold cyan]XXXXXXXXXX[/]") 
        grid.add_row("[dim]Quantization[/]", "[bold cyan]XXXXXXXXXX[/]")
        
        grid.add_row("[dim]Core Integrity[/]", "[dim white]••••••••••[/]") 
        grid.add_row("[dim]Thread Allocation[/]", f"[white]{self.active_config.MODEL_INIT_PARAMS['n_threads']} Threads[/]")
        grid.add_row("[dim]VRAM Usage[/]", f"[white]{self.active_config.MODEL_INIT_PARAMS['n_gpu_layers']} Layers[/]")

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
        # Double check pembersihan layar di awal load
        force_clear()
        console.print()
        
        console.print(Align.center("[bold white]LUMINO[/][dim] INTELLIGENCE SYSTEM[/]"))
        console.print(Rule(style="dim grey23"))
        console.print()

        # Loading Animation
        tasks = [
            f"Initializing {self.model_label}...",
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
                    self.model = Llama(**self.active_config.MODEL_INIT_PARAMS)
        except Exception as e:
            console.print(f"[bold red]Error:[/][white] {e}[/]")
            sys.exit(1)

        self._print_signature()
        time.sleep(2)

    def _print_signature(self):
        grid = Table.grid(padding=(0, 0), expand=True)
        grid.add_column(justify="center")

        status_line = Text.assemble(
            ("● SYSTEM ONLINE", "bold green"),
            (" | Latency: 0ms", "dim white")
        )
        grid.add_row(status_line)
        grid.add_row(Rule(style="dim white", characters="—"))

        creator_line = Text.assemble(
            ("Architect: ", "dim white"),
            (" FADIL ", "bold white on cyan"), 
        )
        grid.add_row(creator_line)

        panel = Panel(
            Align.center(grid),
            box=box.ROUNDED,
            border_style="cyan",
            padding=(1, 4),
            width=70
        )
        console.print(Align.center(panel))
        console.print()

    def generate_response(self, user_input):
        if not self.model:
            return "Error: Neural Core not active."

        if hasattr(self.active_config, 'MAKE_PROMPT'):
             full_prompt = self.active_config.MAKE_PROMPT(
                self.active_config.SYSTEM_PROMPT, 
                user_input
            )
        else:
            full_prompt = (
                f"<|im_start|>system\n{self.active_config.SYSTEM_PROMPT}<|im_end|>\n"
                f"<|im_start|>user\n{user_input}<|im_end|>\n"
                f"<|im_start|>assistant\n"
            )

        try:
            output = self.model(full_prompt, **self.active_config.GENERATION_PARAMS)
            return output['choices'][0]['text']
        except Exception as e:
            return f"Runtime Logic Error: {str(e)}"

engine = AIEngine()