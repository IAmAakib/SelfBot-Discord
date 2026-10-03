import logging
import os
import platform
import time
from collections import defaultdict
from typing import Any, Dict, Optional

import discord
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

class RichLogHandler(logging.Handler):
    """Custom logging handler using Rich for beautiful terminal output."""
    def __init__(self) -> None:
        super().__init__()
        self.console = Console()
        self.level_colors = {
            logging.DEBUG: "dim",
            logging.INFO: "green",
            logging.WARNING: "yellow",
            logging.ERROR: "red",
            logging.CRITICAL: "bold red"
        }

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
            color = self.level_colors.get(record.levelno, "white")
            
            text = Text()
            text.append(f"[{timestamp}] ", style="cyan")
            text.append(f"[{record.levelname}] ", style=color)
            text.append(msg)
            
            self.console.print(text)
        except Exception:
            self.handleError(record)


class Dashboard:
    """Rich-based Terminal UI for Discord SelfBot."""
    def __init__(self) -> None:
        self.console = Console()
        self.command_counts: Dict[str, int] = defaultdict(int)
        
    def _get_os_info(self) -> str:
        os_name = platform.system()
        try:
            with open("/etc/os-release", "r") as f:
                content = f.read()
                if "cachyos" in content.lower():
                    os_name = "CachyOS Linux"
                else:
                    for line in content.splitlines():
                        if line.startswith("PRETTY_NAME="):
                            os_name = line.split("=")[1].strip('"')
                            break
        except Exception:
            pass
        return os_name

    def _get_cpu_info(self) -> str:
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("model name"):
                        return line.split(":")[1].strip()
        except Exception:
            pass
        return platform.processor() or "Unknown CPU"

    def _get_ram_info(self) -> str:
        try:
            with open("/proc/meminfo", "r") as f:
                mem_total = 0
                mem_free = 0
                buffers = 0
                cached = 0
                for line in f:
                    if line.startswith("MemTotal:"):
                        mem_total = int(line.split()[1])
                    elif line.startswith("MemFree:"):
                        mem_free = int(line.split()[1])
                    elif line.startswith("Buffers:"):
                        buffers = int(line.split()[1])
                    elif line.startswith("Cached:"):
                        cached = int(line.split()[1])
                used = mem_total - mem_free - buffers - cached
                return f"{used / 1024 / 1024:.2f} GB / {mem_total / 1024 / 1024:.2f} GB"
        except Exception:
            pass
        return "Unknown RAM"

    def show_banner(self, prefix: str = "!", version: str = "1.0.0") -> None:
        """Displays the startup ASCII banner and system information."""
        banner = r"""
  ____       _  __ ____        _   
 / ___|  ___| |/ _| __ )  ___| |_ 
 \___ \ / _ \ | |_|  _ \ / _ \ __|
  ___) |  __/ |  _| |_) | (_) | |_ 
 |____/ \___|_|_| |____/ \___/ \__|
        """
        
        info_text = Text()
        info_text.append("Version: ", style="bold cyan")
        info_text.append(f"{version}\n", style="white")
        
        info_text.append("Python: ", style="bold cyan")
        info_text.append(f"{platform.python_version()}\n", style="white")
        
        info_text.append("OS: ", style="bold cyan")
        info_text.append(f"{self._get_os_info()} (Kernel: {platform.release()})\n", style="white")
        
        info_text.append("Discord.py-self: ", style="bold cyan")
        info_text.append(f"{discord.__version__}\n", style="white")
        
        info_text.append("Prefix: ", style="bold cyan")
        info_text.append(f"{prefix}", style="white")
        
        panel = Panel(
            Text(banner.strip('\n'), style="bold blue") + Text("\n\n") + info_text,
            title="[bold green]SelfBot Initializing[/]",
            expand=False,
            border_style="blue"
        )
        self.console.print(panel)

    def show_ready(self, bot: Any) -> None:
        """Displays bot status on ready."""
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold cyan")
        table.add_column("Value", style="white")
        
        # User details
        if hasattr(bot, "user") and bot.user:
            # handle difference between modern and older dpy
            user_str = str(bot.user)
            table.add_row("User", user_str)
            table.add_row("ID", str(bot.user.id))
        else:
            table.add_row("User", "Unknown")
            table.add_row("ID", "Unknown")
            
        table.add_row("Guilds", str(len(bot.guilds)) if hasattr(bot, "guilds") else "0")
        
        # Cogs and Commands
        cogs = list(bot.cogs.keys()) if hasattr(bot, "cogs") else []
        table.add_row("Loaded Cogs", ", ".join(cogs) if cogs else "None")
        
        cmd_count = len(bot.commands) if hasattr(bot, "commands") else 0
        table.add_row("Commands", str(cmd_count))
        
        latency = f"{bot.latency * 1000:.2f} ms" if hasattr(bot, "latency") else "Unknown"
        table.add_row("Latency", latency)
        
        # System info
        table.add_row("OS", self._get_os_info())
        table.add_row("CPU", f"{self._get_cpu_info()} ({os.cpu_count()} threads)")
        table.add_row("RAM", self._get_ram_info())
        
        panel = Panel(table, title="[bold green]Bot is Ready![/]", expand=False, border_style="green")
        self.console.print(panel)

    def show_cog_load(self, name: str, success: bool, error: Optional[Exception] = None) -> None:
        """Displays status of cog loading."""
        if success:
            self.console.print(f"[green]✓[/] Loaded cog: [bold cyan]{name}[/]")
        else:
            self.console.print(f"[red]✗[/] Failed to load cog: [bold cyan]{name}[/] - [red]{error}[/]")

    def log_command(self, ctx: Any) -> None:
        """Logs command usage."""
        cmd_name = ctx.command.name if hasattr(ctx, "command") and ctx.command else "Unknown"
        self.command_counts[cmd_name] += 1
        
        channel_name = getattr(getattr(ctx, "channel", None), "name", "DM")
        guild_name = getattr(getattr(ctx, "guild", None), "name", "Direct Message")
        author = str(getattr(ctx, "author", "Unknown User"))
        
        self.console.print(
            f"[dim]{time.strftime('%H:%M:%S')}[/] "
            f"[bold magenta]CMD[/] "
            f"[cyan]{cmd_name}[/] used by [green]{author}[/] "
            f"in [yellow]{channel_name}[/] ({guild_name})"
        )

    def show_stats(self) -> None:
        """Displays command usage statistics."""
        if not self.command_counts:
            self.console.print("[yellow]No commands used yet.[/]")
            return
            
        table = Table(title="Command Usage Statistics", border_style="magenta")
        table.add_column("Command", style="cyan")
        table.add_column("Uses", style="green", justify="right")
        
        for cmd, count in sorted(self.command_counts.items(), key=lambda x: x[1], reverse=True):
            table.add_row(cmd, str(count))
            
        self.console.print(table)

# Module-level singleton instance
dashboard = Dashboard()
