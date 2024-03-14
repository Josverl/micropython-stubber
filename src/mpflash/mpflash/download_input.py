"""Download input handling for mpflash."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from mpflash.mpboard_id.api import known_mp_boards, known_mp_ports


@dataclass
class DownloadParams:
    destination: Path
    ports: List[str] = field(default_factory=list)
    boards: List[str] = field(default_factory=list)
    versions: List[str] = field(default_factory=list)
    force: bool = False
    clean: bool = False
    preview: bool = False


def ask_missing_params(params: DownloadParams) -> DownloadParams:
    # import only when needed to reduce load time
    import inquirer

    # from inquirer.themes import BlueComposure, load_theme_from_dict
    # theme = BlueComposure()

    params.versions = list(params.versions)
    params.preview = "preview" in params.versions
    params.versions = [v for v in params.versions if v != "preview"]
    questions = []
    if not params.boards:
        ask_port_board(questions)

    answers = inquirer.prompt(questions)
    assert answers is not None
    # print(repr(answers))
    if "port" in answers:
        params.ports = [answers["port"]]
    if "boards" in answers:
        params.boards = answers["boards"]
    # print(repr(inputs))

    return params


# TODO Rename this here and in `complete_dl_inputs`
def ask_port_board(questions: list):
    # import only when needed to reduce load time
    import inquirer

    action = "download"
    questions.extend(
        (
            inquirer.List(
                "port",
                message=f"What port do you want to {action}?",
                choices=known_mp_ports(),
                autocomplete=True,
            ),
            inquirer.Checkbox(
                "boards",
                message=f"What board do you want to {action}?",
                choices=lambda answers: known_mp_boards(answers["port"]),
                validate=lambda _, x: True if x else "Please select at least one board",  # type: ignore
            ),
        )
    )
