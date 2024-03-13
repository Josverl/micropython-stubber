import os
import sys
from pprint import pprint
from typing import Dict, List, Tuple, Union

import rich_click as click
from rich.console import Console

from mpflash.mpboard_id.api import known_mp_boards, known_mp_ports

sys.path.append(os.path.realpath("."))
import inquirer  # noqa


def port_choices(answers: dict) -> List[str]:
    # return ["stm32", "esp32", "esp8266", ("nRF", "nrf"), "rp2", "samd"]
    # TODO: remove ports we cannot flash?
    return known_mp_ports()


def board_choices(answers: dict) -> Union[List[str], List[Tuple[str, str]]]:
    return known_mp_boards(answers["port"])


action = "download"

questions = [
    inquirer.List(
        "port",
        message=f"What port do you want to {action}?",
        choices=port_choices,
        autocomplete=True,
    ),
    # inquirer.List(
    #     "board",
    #     message=f"What board do you want to {action}?",
    #     choices=board_choices,
    #     carousel=True,
    # ),
    inquirer.Checkbox(
        "board",
        message=f"What board do you want to {action}?",
        choices=board_choices,
        validate=lambda _, x: True if x else "Please select at least one board",  # type: ignore
    ),
]

from inquirer.themes import BlueComposure, load_theme_from_dict

mytheme = load_theme_from_dict(
    {
        "Question": {
            "mark_color": "yellow",
            "brackets_color": "orange",
            # ...
        },
        "List": {"selection_color": "bold_blue", "selection_cursor": "+=>"},
    }
)


console = Console()
theme = BlueComposure()

answers = inquirer.prompt(questions, theme=theme)
console.print(answers)
