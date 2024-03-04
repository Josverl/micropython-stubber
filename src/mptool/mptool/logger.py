import sys

from loguru import logger as log
from rich.console import Console

console = Console()


def _log_formatter(record: dict) -> str:
    """Log message formatter"""
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
        "[not bold green]{time:HH:mm:ss}[/not bold green] | {level.icon}"
        + f"  - [{lvl_color}]{{message}}[/{lvl_color}]"
    )


def set_loglevel(loglevel: str):
    """Set the log level for the logger"""
    try:
        log.remove()
    except ValueError:
        pass
    log.add(
        console.print, level=loglevel.upper(), colorize=False, format=_log_formatter
    )

    # log.add(
    #     console.print,
    #     level=loglevel.upper(),
    #     format=_log_formatter,
    #     colorize=True,
    # )
