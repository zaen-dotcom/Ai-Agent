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
    from backend import config_qwen as config_reasoning
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
        """Menu Interaktif 3 Pilihan (Modern Card Style)"""
        
        # 0=General, 1=Coding, 2=Reasoning
        selected_index = 1 
        
        # Hitung jumlah opsi
        total_options = 3 if has_reasoning else 2

        while True:
            force_clear()
            console.print()
            
            # Header dengan Spacer
            console.print(Align.center("[bold white]LUMINO[/][dim] INTELLIGENCE SYSTEM[/]"))
            console.print(Rule(style="dim grey15"))
            console.print()
            console.print() # Tambah spasi biar lega

            # --- RENDER PILIHAN (GRID) ---
            grid = Table.grid(expand=True, padding=(0, 2)) # Tambah padding antar kotak
            for _ in range(total_options):
                grid.add_column(justify="center", ratio=1)

            # --- HELPER STYLE ---
            def get_card_content(idx, current_sel, title, subtitle, color, icon):
                if idx == current_sel:
                    # STATE AKTIF: Border Terang, Teks Tebal, Background Header
                    border_col = color
                    title_style = f"bold black on {color}"
                    sub_style = f"bold {color}"
                    box_type = box.ROUNDED
                else:
                    # STATE PASIF: Redup, Border Abu
                    border_col = "grey23"
                    title_style = "dim white on grey15"
                    sub_style = "dim white"
                    box_type = box.ROUNDED
                
                # Isi Kartu
                content = Text.assemble(
                    (f"\n {icon} {title} \n", title_style),
                    (f"\n{subtitle}", sub_style)
                )
                return Panel(content, border_style=border_col, box=box_type, width=30, padding=(0,0))

            # 1. KOTAK GENERAL (Index 0)
            card_gen = get_card_content(
                0, selected_index, 
                "GENERAL", 
                "Standard Chat", 
                "cyan", "●"
            )

            # 2. KOTAK CODING (Index 1)
            card_cod = get_card_content(
                1, selected_index, 
                "CODING", 
                "Dev Expert", 
                "spring_green1", "●" # Hijau Neon lebih segar
            )

            row_panels = [card_gen, card_cod]

            # 3. KOTAK REASONING (Index 2)
            if has_reasoning:
                card_rea = get_card_content(
                    2, selected_index, 
                    "LOGIC", 
                    "Deep Reasoning, Math", 
                    "magenta", "●"
                )
                row_panels.append(card_rea)

            # Tambahkan ke grid
            grid.add_row(*row_panels)

            # Panel Utama Pembungkus (Invisible Border agar bersih)
            main_panel = Panel(
                grid,
                title="[bold white]SELECT NEURAL MODULE[/]",
                subtitle="[dim]← Switch →   |   ENTER Confirm[/]",
                border_style="grey11", # Border sangat tipis/gelap
                box=box.HORIZONTALS,   # Cuma garis atas bawah biar minimalis
                padding=(2, 2),
                width=100 if has_reasoning else 70
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
            
        # Feedback visual
        console.print(f"\n[dim]Booting module:[/][bold cyan] {self.mode_name}[/]")
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