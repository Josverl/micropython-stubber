"""Download input handling for mpflash."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union

from mpflash.common import micropython_versions
from mpflash.mpboard_id.api import known_mp_boards, known_mp_ports


@dataclass
class Params:
    ports: List[str] = field(default_factory=list)
    boards: List[str] = field(default_factory=list)
    versions: List[str] = field(default_factory=list)
    preview: bool = False
    force: bool = False


@dataclass
class DownloadParams(Params):
    destination: Path = Path()
    clean: bool = False


@dataclass
class FlashParams(Params):
    serial: Path = Path()

ParamType = Union[DownloadParams, FlashParams]
def ask_missing_params(params: ParamType) -> ParamType:
    # import only when needed to reduce load time
    import inquirer

    # from inquirer.themes import BlueComposure, load_theme_from_dict
    # theme = BlueComposure()

    params.versions = list(params.versions)
    params.preview = "preview" in params.versions
    params.versions = [v for v in params.versions if v != "preview"]
    questions = []
    if not params.versions or "?" in params.versions:
        ask_versions(questions)

    if not params.boards or "?" in params.boards:
        ask_port_board(questions)

    answers = inquirer.prompt(questions)
    if not answers:
        return params
    # print(repr(answers))
    if "port" in answers:
        params.ports = [answers["port"]]
    if "boards" in answers:
        params.boards = answers["boards"]
    if "versions" in answers:
        params.versions = answers["versions"]

    print(repr(params))

    return params


def ask_port_board(questions: list, *, action: str = "download"):
    # import only when needed to reduce load time
    import inquirer

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
                choices=lambda answers: known_mp_boards(answers["port"], answers["versions"]),
                validate=lambda _, x: True if x else "Please select at least one board",  # type: ignore
            ),
        )
    )


def ask_versions(questions: list, *, action: str = "download"):
    # import only when needed to reduce load time
    import inquirer

    input_ux = inquirer.Checkbox if action == "download" else inquirer.List
    mp_versions: List[str] = micropython_versions()
    mp_versions = [v for v in mp_versions if "preview" not in v]
    mp_versions.append("preview")
    mp_versions.reverse()  # newest first
    questions.append(
        input_ux(
            "versions",
            message=f"What version(s) do you want to {action}?",
            choices=mp_versions,
            autocomplete=True,
            validate=lambda _, x: True if x else "Please select at least one version",  # type: ignore
        )
    )
