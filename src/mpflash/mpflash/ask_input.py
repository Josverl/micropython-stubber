"""
Interactive input for mpflash.

Note: The prompts can use "{version}" and "{action}" to insert the version and action in the prompt without needing an f-string.
The values are provided from the answers dictionary.
"""

from typing import List, Sequence, Tuple, Union

from loguru import logger as log

from .common import DownloadParams, FlashParams, ParamType
from .config import config
from .mpboard_id import (get_known_boards_for_port, get_known_ports,
                         known_stored_boards)
from .mpremoteboard import MPRemoteBoard
from .versions import micropython_versions


def ask_missing_params(
    params: ParamType,
) -> ParamType:
    """
    Asks the user for parameters that have not been supplied on the commandline and returns the updated params.

    Args:
        params (ParamType): The parameters to be updated.

    Returns:
        ParamType: The updated parameters.
    """
    if not config.interactive:
        # no interactivity allowed
        log.info("Interactive mode disabled. Skipping ask for user input.")
        return params

    import inquirer

    log.trace(f"ask_missing_params: {params}")

    # if action flash,  single input
    # if action download, multiple input
    multi_select = isinstance(params, DownloadParams)
    action = "download" if isinstance(params, DownloadParams) else "flash"

    questions = []
    answers: dict[str, Union[str, List]] = {"action": action}
    if not multi_select:
        if not params.serial or "?" in params.serial:
            questions.append(ask_serialport(multi_select=False, bluetooth=False))
        else:
            answers["serial"] = params.serial

    if params.versions == [] or "?" in params.versions:
        questions.append(ask_mp_version(multi_select=multi_select, action=action))
    else:
        # versions is used to show only the boards for the selected versions
        answers["versions"] = params.versions  # type: ignore

    if not params.boards or "?" in params.boards:
        questions.extend(ask_port_board(multi_select=multi_select, action=action))
    if questions:
        answers = inquirer.prompt(questions, answers=answers)  # type: ignore
    if not answers:
        # input cancelled by user
        return []  # type: ignore
    log.trace(f"answers: {answers}")
    if isinstance(params, FlashParams) and "serial" in answers:
        if isinstance(answers["serial"], str):
            answers["serial"] = [answers["serial"]]
        params.serial = [s.split()[0] for s in answers["serial"]]  # split to remove the description
    if "port" in answers:
        #  params.ports = [p for p in params.ports if p != "?"]  # remove the "?" if present
        if isinstance(answers["port"], str):
            params.ports.append(answers["port"])
        elif isinstance(answers["port"], list): # type: ignore
            params.ports.extend(answers["port"])
        else:
            raise ValueError(f"Unexpected type for answers['port']: {type(answers['port'])}")
        
    if "boards" in answers:
        params.boards = [b for b in params.boards if b != "?"]  # remove the "?" if present
        params.boards.extend(answers["boards"] if isinstance(answers["boards"], list) else [answers["boards"]])
    if "versions" in answers:
        params.versions = [v for v in params.versions if v != "?"]  # remove the "?" if present
        # make sure it is a list
        if isinstance(answers["versions"], (list, tuple)):
            params.versions.extend(answers["versions"])
        else:
            params.versions.append(answers["versions"])
    # remove duplicates
    params.ports = list(set(params.ports))
    params.boards = list(set(params.boards))
    params.versions = list(set(params.versions))
    log.trace(f"ask_missing_params returns: {params}")

    return params


def filter_matching_boards(answers: dict) -> Sequence[Tuple[str, str]]:
    """
    Filters the known boards based on the selected versions and returns the filtered boards.

    Args:
        answers (dict): The user's answers.

    Returns:
        Sequence[Tuple[str, str]]: The filtered boards.
    """
    versions = None
    # if version is not asked ; then need to get the version from the inputs
    if "versions" in answers:
        versions = list(answers["versions"])
        if "stable" in versions:
            versions.remove("stable")
            versions.append(micropython_versions()[-2])  # latest stable
        elif "preview" in versions:
            versions.remove("preview")
            versions.extend((micropython_versions()[-1], micropython_versions()[-2]))  # latest preview and stable

    some_boards = known_stored_boards(answers["port"], versions)  #    or known_mp_boards(answers["port"])

    if some_boards:
        # Create a dictionary where the keys are the second elements of the tuples
        # This will automatically remove duplicates because dictionaries cannot have duplicate keys
        unique_dict = {item[1]: item for item in some_boards}
        # Get the values of the dictionary, which are the unique items from the original list
        some_boards = list(unique_dict.values())
    else:
        some_boards = [(f"No {answers['port']} boards found for version(s) {versions}", "")]
    return some_boards


def ask_port_board(*, multi_select: bool, action: str):
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

    # if action flash,  single input
    # if action download, multiple input
    inquirer_ux = inquirer.Checkbox if multi_select else inquirer.List
    return [
        inquirer.List(
            "port",
            message="Which port do you want to {action} " + "to {serial} ?" if action == "flash" else "?",
            choices=get_known_ports(),
            # autocomplete=True,
        ),
        inquirer_ux(
            "boards",
            message=(
                "Which {port} board firmware do you want to {action} " + "to {serial} ?" if action == "flash" else "?"
            ),
            choices=filter_matching_boards,
            validate=at_least_one_validation,  # type: ignore
            # validate=lambda _, x: True if x else "Please select at least one board",  # type: ignore
        ),
    ]

def at_least_one_validation(answers, current) -> bool:
    import inquirer.errors
    if not current:
        raise inquirer.errors.ValidationError("", reason="Please select at least one item.")
    if isinstance(current, list) and not any(current):
        raise inquirer.errors.ValidationError("", reason="Please select at least one item.")
    return True

def ask_mp_version(multi_select: bool, action: str):
    """
    Asks the user for the version selection.

    Args:
        questions (list): The list of questions to be asked.
        action (str): The action to be performed.

    Returns:

    """
    # import only when needed to reduce load time
    import inquirer
    import inquirer.errors

    input_ux = inquirer.Checkbox if multi_select else inquirer.List

    mp_versions: List[str] = micropython_versions()
    mp_versions.reverse()  # newest first

    # remove the versions for which there are no known boards in the board_info.json
    # todo: this may be a little slow
    mp_versions = [v for v in mp_versions if "preview" in v or get_known_boards_for_port("stm32", [v])]

    message = "Which version(s) do you want to {action} " + ("to {serial} ?" if action == "flash" else "?")
    q = input_ux(
        # inquirer.List(
        "versions",
        message=message,
        # Hints would be nice , but needs a hint for each and every option
        # hints=["Use space to select multiple options"],
        choices=mp_versions,
        autocomplete=True,
        validate=at_least_one_validation,  # type: ignore
    )
    return q


def ask_serialport(*, multi_select: bool = False, bluetooth: bool = False):
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

    comports = MPRemoteBoard.connected_boards(bluetooth=bluetooth, description=True)
    return inquirer.List(
        "serial",
        message="Which serial port do you want to {action} ?",
        choices=comports,
        other=True,
        validate=lambda _, x: True if x else "Please select or enter a serial port",  # type: ignore
    )
