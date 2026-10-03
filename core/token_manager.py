"""
Token Manager — store, switch, and manage multiple Discord user tokens.

Tokens are obfuscated with Fernet symmetric encryption using a machine-derived key.
Storage file: tokens.json (gitignored).
"""

import base64
import hashlib
import json
import os
import platform
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt

_TOKENS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tokens.json")
_console = Console()


def _derive_key() -> bytes:
    """Derive a machine-specific key for token obfuscation."""
    # Combine machine identifiers for a stable per-machine key
    seed = f"{platform.node()}-{os.getlogin()}-selfbot-key-v1"
    raw = hashlib.sha256(seed.encode()).digest()
    return base64.urlsafe_b64encode(raw)


def _encrypt(token: str) -> str:
    """Encrypt a token string."""
    try:
        from cryptography.fernet import Fernet
        f = Fernet(_derive_key())
        return f.encrypt(token.encode()).decode()
    except ImportError:
        # Fallback: base64 obfuscation (not secure, but hides plaintext)
        return base64.urlsafe_b64encode(token.encode()).decode()


def _decrypt(data: str) -> str:
    """Decrypt a token string."""
    try:
        from cryptography.fernet import Fernet
        f = Fernet(_derive_key())
        return f.decrypt(data.encode()).decode()
    except ImportError:
        return base64.urlsafe_b64decode(data.encode()).decode()


def _mask_token(token: str) -> str:
    """Show first 6 and last 4 chars, mask the rest."""
    if len(token) < 15:
        return "****"
    return token[:6] + "*" * (len(token) - 10) + token[-4:]


def _load_accounts() -> list[dict]:
    """Load saved accounts from tokens.json."""
    if not os.path.exists(_TOKENS_FILE):
        return []
    try:
        with open(_TOKENS_FILE, "r") as f:
            data = json.load(f)
        return data.get("accounts", [])
    except Exception:
        return []


def _save_accounts(accounts: list[dict]) -> None:
    """Save accounts to tokens.json."""
    with open(_TOKENS_FILE, "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)


def _add_account(name: str, token: str) -> None:
    """Add or update an account."""
    accounts = _load_accounts()
    # Check if name exists, update if so
    for acc in accounts:
        if acc["name"].lower() == name.lower():
            acc["token"] = _encrypt(token)
            _save_accounts(accounts)
            return
    accounts.append({"name": name, "token": _encrypt(token)})
    _save_accounts(accounts)


def _remove_account(index: int) -> bool:
    """Remove account by index (0-based)."""
    accounts = _load_accounts()
    if 0 <= index < len(accounts):
        accounts.pop(index)
        _save_accounts(accounts)
        return True
    return False


def _import_from_env() -> Optional[str]:
    """Check if .env has a token that can be imported."""
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("DISCORD_TOKEN")


def select_token() -> Optional[str]:
    """Interactive token selector. Returns chosen token string or None to exit."""
    accounts = _load_accounts()

    # Auto-import from .env if no accounts saved yet
    if not accounts:
        env_token = _import_from_env()
        if env_token:
            _console.print("[dim]Found token in .env — importing as 'default'...[/]")
            _add_account("default", env_token)
            accounts = _load_accounts()

    while True:
        _console.print()

        # Build account table
        table = Table(
            title="Account Manager",
            border_style="cyan",
            show_lines=False,
        )
        table.add_column("#", style="bold white", justify="right", width=3)
        table.add_column("Name", style="bold green")
        table.add_column("Token", style="dim")

        for i, acc in enumerate(accounts, 1):
            try:
                decrypted = _decrypt(acc["token"])
                masked = _mask_token(decrypted)
            except Exception:
                masked = "[red]corrupted[/]"
            table.add_row(str(i), acc["name"], masked)

        if accounts:
            _console.print(table)

        # Options
        options = []
        if accounts:
            options.append("[cyan]1-{0}[/] Select account".format(len(accounts)))
        options.append("[green]N[/]  Add new account")
        if accounts:
            options.append("[red]D[/]  Delete account")
        options.append("[yellow]Q[/]  Quit")

        _console.print(Panel(
            "\n".join(options),
            title="[bold]Options[/]",
            border_style="blue",
            expand=False,
        ))

        choice = Prompt.ask("[bold]Choice[/]").strip().lower()

        # Quit
        if choice == "q":
            return None

        # Add new
        if choice == "n":
            name = Prompt.ask("[green]Account name[/]").strip()
            if not name:
                _console.print("[red]Name cannot be empty.[/]")
                continue
            token = Prompt.ask("[green]Token[/]", password=True).strip()
            if not token:
                _console.print("[red]Token cannot be empty.[/]")
                continue
            _add_account(name, token)
            accounts = _load_accounts()
            _console.print(f"[green]Account '{name}' saved.[/]")
            continue

        # Delete
        if choice == "d":
            if not accounts:
                _console.print("[red]No accounts to delete.[/]")
                continue
            idx = IntPrompt.ask(
                f"[red]Delete which account (1-{len(accounts)})[/]",
                default=0,
            )
            if 1 <= idx <= len(accounts):
                removed_name = accounts[idx - 1]["name"]
                _remove_account(idx - 1)
                accounts = _load_accounts()
                _console.print(f"[red]Deleted '{removed_name}'.[/]")
            else:
                _console.print("[red]Invalid selection.[/]")
            continue

        # Select by number
        try:
            idx = int(choice)
            if 1 <= idx <= len(accounts):
                try:
                    token = _decrypt(accounts[idx - 1]["token"])
                    _console.print(
                        f"[green]Selected:[/] [bold]{accounts[idx - 1]['name']}[/]"
                    )
                    return token
                except Exception:
                    _console.print("[red]Failed to decrypt token. Re-add this account.[/]")
            else:
                _console.print("[red]Invalid selection.[/]")
        except ValueError:
            _console.print("[red]Invalid input.[/]")
