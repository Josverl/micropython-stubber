"""Manual bootloader mode entry for various MCUs."""

from click.exceptions import Abort
from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.panel import Panel
from rich.prompt import Confirm
from rich.theme import Theme

# from mpflash.logger import console, log
from mpflash.mpremoteboard import MPRemoteBoard


class MCUHighlighter(RegexHighlighter):
    """Apply style to things that should stand out."""

    base_style = "mcu."
    highlights = [
        r"(?P<bold>Method[\s\d\:]*)",
        r"(?P<bold> \d.)",  # numbered items
        r"(?P<bold> - )",  # bullets
        # mcu things
        r"(?P<pad>GPIO[\d]*)",
        r"(?P<pad>GPI[\d]*)",
        r"(?P<pad>IO[\d]*)",
        r"(?P<pad>RUN)",
        r"(?P<pad>GND)",
        r"(?P<pad>VCC)",
        r"(?P<pad>3.3V)",
        r"(?P<pad>5V)",
        # buttons
        r"(?P<button>BOOTSEL)",
        r"(?P<button>RESET)",
        r"(?P<button>reset)",
        # other
        r"(?P<cable>USB)",
        r"(?P<cable>USB-C)",
        r"(?P<cable>Serial)",
    ]


# https://rich.readthedocs.io/en/stable/appendix/colors.html?highlight=colors#standard-colors
# use 3 colors to keep things simple but clear
mcu_theme = Theme(
    {
        "mcu.bold": "orange3",  # readers guidance
        "mcu.button": "bold green",  # things to press
        "mcu.pad": "dodger_blue2",  # things to connect
        "mcu.cable": "dodger_blue2",  # things to connect
    }
)


def enter_bootloader_manual(mcu: MPRemoteBoard, timeout: int = 10):

    message: str
    if mcu.port == "rp2":
        message = f"""\
Please put your {" ".join([mcu.port,mcu.board])} device into bootloader mode by either:
Method 1:
  1. Unplug the USB cable, 
  2. Press and hold the BOOTSEL button on the device, 
  3. Plug the USB cable back in.
  4. Release the BOOTSEL button.
    
Method 2:
  1. Press and hold the BOOTSEL button on the device, 
  2. Reset the device by either: 
    - pressing the RESET button on the device 
    - by power-cycling the device,
    - by briefly connecting the RUN pin to GND
  3. Release the BOOTSEL button.
"""
    elif mcu.port == "samd":
        message = f"""\
Please put your {mcu.port.upper()} device into bootloader mode by:
  - Pressing or sliding the RESET button twice in fast succession
"""
    else:
        message = f"""\
Please put your {mcu.port.upper()} device into bootloader mode by:
  - Pressing the RESET button on the device
"""

    # todo: would be nice to re-use the console instance from logger
    console = Console(highlighter=MCUHighlighter(), theme=mcu_theme)  # type: ignore
    message += "\nIf you are unsure how to enter bootloader mode, please refer to the device documentation."
    console.print(
        Panel(
            message,
            highlight=True,
            title="Manual Bootloader",
            title_align="left",
            expand=False,
        )
    )
    try:
        answer = Confirm.ask("Press Enter to continue", default="y")
    except Abort:
        return False
    return answer in ["y", "Y", True]
