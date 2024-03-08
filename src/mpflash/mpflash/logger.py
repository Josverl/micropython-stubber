"""Logging."""

from loguru import logger as log
from rich.console import Console

from .config import config

console = Console()


def _log_formatter(record: dict) -> str:
    """Log message formatter to combine loguru and rich formatting."""
    color_map = {
        "TRACE": "dim blue",
        "DEBUG": "cyan",
        "INFO": "bold",
        "SUCCESS": "bold green",
        "WARNING": "yellow",
        "ERROR": "bold red",
        "CRITICAL": "bold white on red",
    }
    lvl_color = color_map.get(record["level"].name, "cyan")
    return (
        "[not bold green]{time:HH:mm:ss}[/not bold green] | {level.icon} " + f"[{lvl_color}]{{message}}[/{lvl_color}]"
    )


def set_loglevel(loglevel: str):
    """Set the log level for the logger"""
    try:
        log.remove()
    except ValueError:
        pass
    log.add(console.print, level=loglevel.upper(), colorize=False, format=_log_formatter)  # type: ignore


def make_quiet():
    """Make the logger quiet"""
    config.quiet = True
    console.quiet = True
    set_loglevel("CRITICAL")
