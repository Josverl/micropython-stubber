"""
Run a command and return the output and return code as a tuple
"""

import subprocess
from dataclasses import dataclass
from threading import Timer
from typing import List, Optional, Tuple

from loguru import logger as log

LogTagList = List[str]


@dataclass
class LogTags:
    reset_tags: LogTagList
    error_tags: LogTagList
    warning_tags: LogTagList
    success_tags: LogTagList
    ignore_tags: LogTagList


DEFAULT_RESET_TAGS = [
    # ESP32 reset causes
    "rst cause:1, boot mode:",  # 1 -> hardware watch dog reset
    "rst cause:2, boot mode:",  # 2 -> software watch dog reset (From an exception)
    "rst cause:3, boot mode:",  # 3 -> software watch dog reset system_restart (Possibly unfed watchdog got angry)
    "rst cause:4, boot mode:",  # 4 -> soft restart (Possibly with a restart command)
    "boot.esp32: PRO CPU has been reset by WDT.",
    "rst:0x10 (RTCWDT_RTC_RESET)",
]


def run(
    cmd: List[str],
    timeout: int = 60,
    log_errors: bool = True,
    no_info: bool = False,
    *,
    log_warnings: bool = False,
    reset_tags: Optional[LogTagList] = None,
    error_tags: Optional[LogTagList] = None,
    warning_tags: Optional[LogTagList] = None,
    success_tags: Optional[LogTagList] = None,
    ignore_tags: Optional[LogTagList] = None,
) -> Tuple[int, List[str]]:
    # sourcery skip: no-long-functions
    """
    Run a command and return the output and return code as a tuple
    Parameters
    ----------
    cmd : List[str]
        The command to run
    timeout : int, optional
        The timeout in seconds, by default 60
    log_errors : bool, optional
        If False, don't log errors, Default: true
    no_info : bool, optional
        If True, don't log info, by default False
    error_tags : Optional[LogTagList], optional
        A list of strings to look for in the output to log as errors, by default None
    warning_tags : Optional[LogTagList], optional
        A list of strings to look for in the output to log as warnings, by default None
    Returns
    -------
    Tuple[int, List[str]]
        The return code and the output as a list of strings
    """
    if not reset_tags:
        reset_tags = DEFAULT_RESET_TAGS
    if not error_tags:
        error_tags = ["Traceback ", "Error: ", "Exception: ", "ERROR :", "CRIT  :"]
    if not warning_tags:
        warning_tags = ["WARN  :", "TRACE :"]
    if not success_tags:
        success_tags = []
    if not ignore_tags:
        ignore_tags = ['  File "<stdin>",']

    replace_tags = ["\x1b[1A"]

    output = []
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding="utf-8",
        )
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Failed to start {cmd[0]}") from e

    def timed_out():
        proc.kill()
        if log_warnings:
            log.warning(f"Command {cmd} timed out after {timeout} seconds")

    timer = Timer(timeout, timed_out)
    try:
        timer.start()
        # stdout has most of the output, assign log categories based on text tags
        if proc.stdout:
            for line in proc.stdout:
                if not line or not line.strip():
                    continue
                for tag in replace_tags:
                    line = line.replace(tag, "")
                output.append(line)  # full output, no trimming
                if any(tag in line for tag in reset_tags):
                    raise RuntimeError("Board reset detected")

                line = line.rstrip("\n")
                # if any of the error tags in the line
                if any(tag in line for tag in error_tags):
                    if not log_errors:
                        continue
                    log.error(line)
                elif any(tag in line for tag in warning_tags):
                    log.warning(line)
                elif any(tag in line for tag in success_tags):
                    log.success(line)
                elif any(tag in line for tag in ignore_tags):
                    continue
                else:
                    if not no_info:
                        if line.startswith(("INFO  : ", "WARN  : ", "ERROR : ")):
                            line = line[8:].lstrip()
                        log.info(line)
        if proc.stderr and log_errors:
            for line in proc.stderr:
                log.warning(line)
    except UnicodeDecodeError as e:
        log.error(f"Failed to decode output: {e}")
    finally:
        timer.cancel()

    proc.wait(timeout=1)
    return proc.returncode or 0, output
