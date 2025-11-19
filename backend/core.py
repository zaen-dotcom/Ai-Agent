import time
import sys
import os
import random
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich import box

from llama_cpp import Llama
from backend import config

# --- CLASS PEREDAM SUARA ---
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

class AIEngine:
    def __init__(self):
        self.model = None
        self.load_model()

    def _print_system_specs(self):
        """
        Menampilkan tabel spesifikasi dengan LEBAR 85 (Sama dengan bawah).
        """
        # expand=True akan memaksa tabel mengisi lebar panel (85)
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="right")
        
        # --- ISI DATA (SENSOR BLINK) ---
        grid.add_row("[dim]Architecture[/]", "[bold red blink]XXXXXXXXXX[/]") 
        grid.add_row("[dim]Precision[/]", "[bold red blink]XXXXXXXXXX[/]")
        grid.add_row("[dim]Neural Threads[/]", f"[bold white]{config.MODEL_INIT_PARAMS['n_threads']} Cores[/]")
        grid.add_row("[dim]VRAM Layering[/]", f"[bold white]{config.MODEL_INIT_PARAMS['n_gpu_layers']} Layers[/]")

        panel = Panel(
            grid,
            title="[bold yellow]⚡ HARDWARE DIAGNOSTIC[/]",
            title_align="left",
            border_style="bright_black",
            padding=(0, 2),
            width=85  # <--- KITA KUNCI LEBARNYA DISINI
        )
        # Gunakan Align.center agar panelnya berada di tengah layar
        console.print(Align.center(panel))

    def load_model(self):
        console.clear()
        console.print()
        console.print(Align.center("[bold cyan]SYSTEM BOOT SEQUENCE INITIATED[/]"))
        console.print(Rule(style="dim cyan"))

        # --- PHASE 1: BOOT TASKS ---
        boot_tasks = [
            "Calibrating Quantum Tensors...",
            "Rearranging Electrons in GPU Core...",
            "Bypassing Bio-Digital Security...",
            "Optimizing Synaptic Pathways...",
            "Harmonizing Matrix Frequencies...",
            "Establishing Neural Uplink..."
        ]

        with Progress(
            SpinnerColumn(style="bold magenta"),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(bar_width=30, style="dim blue", complete_style="bold cyan"),
            TextColumn("[bold white]{task.percentage:>3.0f}%"),
            console=console,
            transient=True
        ) as progress:
            main_task = progress.add_task("[bold white]Initializing Core...", total=100)
            chunk = 100 / len(boot_tasks)
            for desc in boot_tasks:
                progress.update(main_task, description=desc)
                time.sleep(random.uniform(0.05, 0.15)) 
                progress.advance(main_task, chunk)

        # --- PHASE 2: SPECS (SYMMETRIC WIDTH) ---
        self._print_system_specs()
        console.print()

        # --- PHASE 3: HEAVY LIFTING ---
        loading_phrases = [
            "Awakening the Digital Soul...",
            "Loading Knowledge Base...",
            "Constructing Cognitive Model...",
        ]
        chosen_phrase = random.choice(loading_phrases)

        try:
            with console.status(f"[bold white]{chosen_phrase}[/]", spinner="dots12", spinner_style="bold green"):
                with SuppressFactory(): 
                    self.model = Llama(**config.MODEL_INIT_PARAMS)
            
            # --- PHASE 4: SIGNATURE (SYMMETRIC WIDTH) ---
            self._print_signature()

            # --- PHASE 5: DELAY 5 DETIK ---
            with console.status("[bold dim]System Standby...[/]", spinner="point", spinner_style="cyan"):
                time.sleep(5)

        except Exception as e:
            console.print(Panel(f"[bold red]SYSTEM FAILURE:[/]\n{e}", title="CRITICAL ERROR", border_style="red"))
            sys.exit(1)

    def _print_signature(self):
        status_text = Text("● SYSTEM ONLINE", style="bold green blink")
        desc_text = Text("\nArtificial Intelligence Unit ready for complex task execution.\nLatency: 0.0ms | Integrity: 100%", style="dim white", justify="center")
        signature = Text.assemble(
            ("\nForged in the Code-Foundry of ", "italic cyan"),
            ("FADIL", "bold underline white"),
            ("\nMaster Architect & System Creator", "dim cyan")
        )
        final_content = Align.center(status_text + desc_text + signature)

        console.print()
        # Panel Bawah
        panel = Panel(
            final_content,
            box=box.DOUBLE_EDGE,
            border_style="cyan",
            padding=(1, 4),
            title="[bold black on cyan] LUMINO PROTOCOL [/]",
            subtitle="[bold black on cyan] ACCESS GRANTED [/]",
            width=85  # <--- KITA KUNCI LEBARNYA DISINI JUGA (SAMA DENGAN ATAS)
        )
        # Gunakan Align.center agar panelnya berada di tengah layar
        console.print(Align.center(panel))
        console.print()

    def generate_response(self, user_input):
        if not self.model:
            return "Error: Neural Core not active."

        full_prompt = (
            f"<|im_start|>system\n{config.SYSTEM_PROMPT}<|im_end|>\n"
            f"<|im_start|>user\n{user_input}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        try:
            output = self.model(full_prompt, **config.GENERATION_PARAMS)
            return output['choices'][0]['text']
        except Exception as e:
            return f"Runtime Logic Error: {str(e)}"

engine = AIEngine()