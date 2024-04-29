"""
Interactive input for mpflash.

Note: The prompts can use "{version}" and "{action}" to insert the version and action in the prompt without needing an f-string.
The values are provided from the answers dictionary.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence, Tuple, Union

from loguru import logger as log

from mpflash.config import config
from mpflash.mpboard_id import get_stored_boards_for_port, known_stored_boards, local_mp_ports
from mpflash.mpremoteboard import MPRemoteBoard
from mpflash.vendor.versions import micropython_versions


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
    """
    Asks the user for parameters that have not been supplied on the commandline and returns the updated params.

    Args:
        params (ParamType): The parameters to be updated.
        action (str, optional): The action to be performed. Defaults to "download".

    Returns:
        ParamType: The updated parameters.
    """
    if not config.interactive:
        # no interactivity allowed
        return params
    # import only when needed to reduce load time
    import inquirer

    questions = []
    answers = {"action": action}
    if isinstance(params, FlashParams):
        if not params.serial or "?" in params.serial:
            ask_serialport(questions, action=action)
        else:
            answers["serial"] = params.serial

    if not params.versions or "?" in params.versions:
        ask_versions(questions, action=action)
    else:
        # versions is used to show only the boards for the selected versions
        answers["versions"] = params.versions  # type: ignore

    if not params.boards or "?" in params.boards:
        ask_port_board(questions, action=action)

    answers = inquirer.prompt(questions, answers=answers)
    if not answers:
        # input cancelled by user
        return []  # type: ignore
    # print(repr(answers))
    if isinstance(params, FlashParams) and "serial" in answers:
        params.serial = answers["serial"]
    if "port" in answers:
        params.ports = [answers["port"]]
    if "boards" in answers:
        params.boards = answers["boards"] if isinstance(answers["boards"], list) else [answers["boards"]]
    if "versions" in answers:
        # make sure it is a list
        params.versions = answers["versions"] if isinstance(answers["versions"], list) else [answers["versions"]]

    log.debug(repr(params))

    return params


def filter_matching_boards(answers: dict) -> Sequence[Tuple[str, str]]:
    """
    Filters the known boards based on the selected versions and returns the filtered boards.

    Args:
        answers (dict): The user's answers.

    Returns:
        Sequence[Tuple[str, str]]: The filtered boards.
    """
    # if version is not asked ; then need to get the version from the inputs
    if "versions" in answers:
        _versions = list(answers["versions"])
        if "stable" in _versions:
            _versions.remove("stable")
            _versions.append(micropython_versions()[-2])  # latest stable
        if "preview" in _versions:
            _versions.remove("preview")
            _versions.extend((micropython_versions()[-1], micropython_versions()[-2]))  # latest preview and stable

        some_boards = known_stored_boards(answers["port"], _versions)  #    or known_mp_boards(answers["port"])
    else:
        some_boards = known_stored_boards(answers["port"])

    if some_boards:
        # Create a dictionary where the keys are the second elements of the tuples
        # This will automatically remove duplicates because dictionaries cannot have duplicate keys
        unique_dict = {item[1]: item for item in some_boards}
        # Get the values of the dictionary, which are the unique items from the original list
        some_boards = list(unique_dict.values())
    else:
        some_boards = [(f"No {answers['port']} boards found for version(s) {_versions}", "")]
    return some_boards


def ask_port_board(questions: list, *, action: str):
    """
    Asks the user for the port and board selection.

    Args:
        questions (list): The list of questions to be asked.
        action (str): The action to be performed.

    Returns:
        None
    """
    # import only when needed to reduce load time
    import inquirer

    # TODO: if action = flash, Use Inquirer.List for boards
    inquirer_ux = inquirer.Checkbox if action == "download" else inquirer.List
    questions.extend(
        (
            inquirer.List(
                "port",
                message="Which port do you want to {action} " + "to {serial} ?" if action == "flash" else "?",
                choices=local_mp_ports(),
                autocomplete=True,
            ),
            inquirer_ux(
                "boards",
                message=(
                    "Which {port} board firmware do you want to {action} " + "to {serial} ?"
                    if action == "flash"
                    else "?"
                ),
                choices=filter_matching_boards,
                validate=lambda _, x: True if x else "Please select at least one board",  # type: ignore
            ),
        )
    )


def ask_versions(questions: list, *, action: str):
    """
    Asks the user for the version selection.

    Args:
        questions (list): The list of questions to be asked.
        action (str): The action to be performed.

    Returns:
        None
    """
    # import only when needed to reduce load time
    import inquirer
    import inquirer.errors

    input_ux = inquirer.Checkbox if action == "download" else inquirer.List
    mp_versions: List[str] = micropython_versions()
    mp_versions = [v for v in mp_versions if "preview" not in v]

    # remove the versions for which there are no known boards in the board_info.json
    # todo: this may be a little slow
    mp_versions = [v for v in mp_versions if get_stored_boards_for_port("stm32", [v])]

    mp_versions.append("preview")
    mp_versions.reverse()  # newest first

    def at_least_one_validation(answers, current) -> bool:
        if not current:
            raise inquirer.errors.ValidationError("", reason="Please select at least one version")
        if isinstance(current, list):
            if not any(current):
                raise inquirer.errors.ValidationError("", reason="Please select at least one version")
        return True

    questions.append(
        input_ux(
            # inquirer.List(
            "versions",
            message="Which version(s) do you want to {action} " + ("to {serial} ?" if action == "flash" else "?"),
            # Hints would be nice , but needs a hint for each and every option
            # hints=["Use space to select multiple options"],
            choices=mp_versions,
            autocomplete=True,
            validate=at_least_one_validation,
        )
    )


def ask_serialport(questions: list, *, action: str):
    """
    Asks the user for the serial port selection.

    Args:
        questions (list): The list of questions to be asked.
        action (str): The action to be performed.

    Returns:
        None
    """
    # import only when needed to reduce load time
    import inquirer

    serialports = MPRemoteBoard.connected_boards()
    questions.append(
        inquirer.List(
            "serial",
            message="Which serial port do you want to {action} ?",
            choices=serialports,
            other=True,
            validate=lambda _, x: True if x else "Please select or enter a serial port",  # type: ignore
        )
    )

    return questions
