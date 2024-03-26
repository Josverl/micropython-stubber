"""Download input handling for mpflash."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence, Tuple, Union

from loguru import logger as log

from mpflash.common import micropython_versions
from mpflash.config import config
from mpflash.mpboard_id.api import known_mp_boards, known_mp_ports
from mpflash.mpremoteboard import MPRemoteBoard


@dataclass
class Params:
    ports: List[str] = field(default_factory=list)
    boards: List[str] = field(default_factory=list)
    versions: List[str] = field(default_factory=list)
    fw_folder: Path = Path()


@dataclass
class DownloadParams(Params):
    clean: bool = False
    force: bool = False


@dataclass
class FlashParams(Params):
    # TODO: Should Serial port be a list?
    serial: str = ""
    erase: bool = True
    bootloader: bool = True
    cpu: str = ""


ParamType = Union[DownloadParams, FlashParams]


def ask_missing_params(
    params: ParamType,
    action: str = "download",
) -> ParamType:
    if not config.interactive:
        # no interactivity allowed
        return params
    # import only when needed to reduce load time
    import inquirer

    questions = []
    if isinstance(params, FlashParams) and (not params.serial or "?" in params.versions):
        ask_serialport(questions, action=action)

    if not params.versions or "?" in params.versions:
        ask_versions(questions, action=action)

    if not params.boards or "?" in params.boards:
        ask_port_board(questions, action=action)

    answers = inquirer.prompt(questions)
    if not answers:
        return params
    # print(repr(answers))
    if isinstance(params, FlashParams) and "serial" in answers:
        params.serial = answers["serial"]
    if "port" in answers:
        params.ports = [answers["port"]]
    if "boards" in answers:
        params.boards = answers["boards"]
    if "versions" in answers:
        # make sure it is a list
        params.versions = answers["versions"] if isinstance(answers["versions"], list) else [answers["versions"]]

    log.debug(repr(params))

    return params


def some_boards(answers: dict) -> Sequence[Tuple[str, str]]:
    if "versions" in answers:
        _versions = list(answers["versions"])
        if "stable" in _versions:
            _versions.remove("stable")
            _versions.append(micropython_versions()[-2])
        if "preview" in _versions:
            _versions.remove("preview")
            _versions.append(micropython_versions()[-1])
            _versions.append(micropython_versions()[-2])

        some_boards = known_mp_boards(answers["port"], _versions)  #    or known_mp_boards(answers["port"])
    else:
        some_boards = known_mp_boards(answers["port"])

    if some_boards:
        # Create a dictionary where the keys are the second elements of the tuples
        # This will automatically remove duplicates because dictionaries cannot have duplicate keys
        unique_dict = {item[1]: item for item in some_boards}
        # Get the values of the dictionary, which are the unique items from the original list
        some_boards = list(unique_dict.values())
    else:
        some_boards = [("No boards found", "")]
    return some_boards


def ask_port_board(questions: list, *, action: str):
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
                choices=some_boards,
                validate=lambda _, x: True if x else "Please select at least one board",  # type: ignore
            ),
        )
    )


def ask_versions(questions: list, *, action: str):
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


def ask_serialport(questions: list, *, action: str):
    # import only when needed to reduce load time
    import inquirer

    serialports = MPRemoteBoard.connected_boards()
    questions.append(
        inquirer.List(
            "serial",
            message="What serial port do you want use ?",
            validate=lambda _, x: True if x else "Please enter a serial port",  # type: ignore
            choices=serialports,
            other=True,
        )
    )

    return questions
