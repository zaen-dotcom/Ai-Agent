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

# --- IMPORT KONFIGURASI ---
from backend import config as config_coding

# Config General (Llama)
try:
    from backend import config_llama as config_general
except ImportError:
    config_general = config_coding

# Config Reasoning (DeepSeek) - [BARU]
try:
    from backend import config_deepseek as config_reasoning
    has_reasoning = True
except ImportError:
    config_reasoning = None
    has_reasoning = False

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
        self.mode_name = ""
        self.model_label = ""
        
        # 1. Pilih Mode
        self._select_module_interactive()
        
        # 2. Load Model
        self.load_model()

    def switch_model(self):
        """Fungsi untuk Hot-Swap via command /model"""
        self._select_module_interactive()
        self.load_model()

    def _select_module_interactive(self):
        """Menu Interaktif 3 Pilihan (General, Coding, Reasoning)"""
        
        # 0=General, 1=Coding, 2=Reasoning
        selected_index = 1 
        
        # Hitung jumlah opsi (2 atau 3 tergantung ketersediaan DeepSeek)
        total_options = 3 if has_reasoning else 2

        while True:
            force_clear()
            console.print()
            
            console.print(Align.center("[bold white]LUMINO[/][dim] INTELLIGENCE SYSTEM[/]"))
            console.print(Rule(style="dim grey23"))
            console.print()

            # --- RENDER PILIHAN ---
            # Grid menyesuaikan jumlah kolom
            grid = Table.grid(expand=True, padding=(0, 1))
            for _ in range(total_options):
                grid.add_column(justify="center", ratio=1)

            # --- HELPER STYLE ---
            def get_style(idx, current_sel, color_name, icon_char):
                if idx == current_sel:
                    return f"bold white on {color_name}", f"bold {color_name}", "●", color_name
                return "dim white", "dim white", "○", "grey23"

            # 1. KOTAK GENERAL (Index 0)
            bg_gen, txt_gen, ico_gen, bor_gen = get_style(0, selected_index, "cyan", "●")
            panel_gen = Panel(
                Text.assemble((f"\n{ico_gen} GENERAL KNOWLEDGE\n", bg_gen), ("\nnXXXXXXX", txt_gen)),
                border_style=bor_gen, box=box.ROUNDED
            )

            # 2. KOTAK CODING (Index 1)
            bg_cod, txt_cod, ico_cod, bor_cod = get_style(1, selected_index, "green", "●")
            panel_cod = Panel(
                Text.assemble((f"\n{ico_cod} CODING, ALGORITHM\n", bg_cod), ("\nXXXXXXX", txt_cod)),
                border_style=bor_cod, box=box.ROUNDED
            )

            # Masukkan ke list baris
            row_panels = [panel_gen, panel_cod]

            # 3. KOTAK REASONING (Index 2) - Jika Ada
            if has_reasoning:
                bg_rea, txt_rea, ico_rea, bor_rea = get_style(2, selected_index, "magenta", "●")
                panel_rea = Panel(
                    Text.assemble((f"\n{ico_rea} REASONING, QUANTUM\n", bg_rea), ("\nXXXXXXX", txt_rea)),
                    border_style=bor_rea, box=box.ROUNDED
                )
                row_panels.append(panel_rea)

            # Tambahkan ke grid
            grid.add_row(*row_panels)

            # Panel Utama Pembungkus
            main_panel = Panel(
                grid,
                title="[bold white]SELECT NEURAL MODULE[/]",
                subtitle="[dim]Use ← Left / Right → to Switch, ENTER to Confirm[/]",
                border_style="white",
                box=box.ROUNDED,
                padding=(1, 2),
                width=90 if has_reasoning else 70 # Lebarkan jika ada 3 opsi
            )
            console.print(Align.center(main_panel))

            # --- INPUT HANDLING (Cyclic Navigation) ---
            key = msvcrt.getch()
            
            if key == b'\xe0': 
                key = msvcrt.getch()
                if key == b'K': # Kiri
                    selected_index = (selected_index - 1) % total_options
                elif key == b'M': # Kanan
                    selected_index = (selected_index + 1) % total_options
            elif key == b'\r': # Enter
                break 
        
        # SET CONFIG BERDASARKAN PILIHAN
        if selected_index == 0:
            self.active_config = config_general
            self.mode_name = "GENERAL KNOWLEDGE"
            self.model_label = "Llama 3.1 Instruct"
        elif selected_index == 1:
            self.active_config = config_coding
            self.mode_name = "CODING & ARCHITECTURE"
            self.model_label = "Qwen 2.5 Coder"
        elif selected_index == 2 and has_reasoning:
            self.active_config = config_reasoning
            self.mode_name = "DEEP LOGIC & REASONING"
            self.model_label = "DeepSeek R1 Distill"
            
        console.print(f"\n[dim]Module selected:[/][bold cyan] {self.mode_name}[/]")
        time.sleep(0.4)
        force_clear()

    def _print_specs(self):
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

    def generate_response(self, user_input):
        if not self.model: return "Error: Neural Core not active."

        if hasattr(self.active_config, 'MAKE_PROMPT'):
             full_prompt = self.active_config.MAKE_PROMPT(self.active_config.SYSTEM_PROMPT, user_input)
        else:
            full_prompt = f"<|im_start|>system\n{self.active_config.SYSTEM_PROMPT}<|im_end|>\n<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"

        try:
            output = self.model(full_prompt, **self.active_config.GENERATION_PARAMS)
            return output['choices'][0]['text']
        except Exception as e:
            return f"Runtime Logic Error: {str(e)}"

engine = AIEngine()