"""
Module to run mpremote commands, and retry on failure or timeout
"""

import sys
from pathlib import Path
from typing import List, Optional, Union

import serial.tools.list_ports
from loguru import logger as log
from tenacity import retry, stop_after_attempt, wait_fixed

from mpflash.mpboard_id.board_id import find_board_designator
from .runner import run

###############################################################################################
# TODO : make this a bit nicer
HERE = Path(__file__).parent

OK = 0
ERROR = -1
RETRIES = 3
###############################################################################################


class MPRemoteBoard:
    """Class to run mpremote commands"""

    def __init__(self, serialport: str = ""):
        self.serialport = serialport
        # self.board = ""
        self.firmware = {}

        self.connected = False
        self.path: Optional[Path] = None
        self.family = "unknown"
        self.description = ""
        self.version = ""
        self.port = ""
        self.board = ""
        self.cpu = ""
        self.arch = ""
        self.mpy = ""
        self.build = ""

    def __str__(self):
        return f"MPRemoteBoard({self.serialport}, {self.family} {self.port}, {self.board}, {self.version})"

    @staticmethod
    def connected_boards():
        """Get a list of connected boards"""
        devices = [p.device for p in serial.tools.list_ports.comports()]
        return sorted(devices)

    @retry(stop=stop_after_attempt(RETRIES), wait=wait_fixed(1), retry_error_cls=ConnectionError)  # type: ignore
    def get_mcu_info(self, timeout: int = 6):
        rc, result = self.run_command(
            ["run", str(HERE / "mpy_fw_info.py")],
            no_info=True,
            timeout=timeout,
        )
        if rc != OK:
            raise ConnectionError(f"Failed to get mcu_info for {self.serialport}")
        # Ok we have the info, now parse it
        s = result[0].strip()
        if s.startswith("{") and s.endswith("}"):
            info = eval(s)
            self.family = info["family"]
            self.version = info["version"]
            self.build = info["build"]
            self.port = info["port"]
            self.cpu = info["cpu"]
            self.arch = info["arch"]
            self.mpy = info["mpy"]
            self.description = descr = info["board"]
            pos = descr.rfind(" with")
            if pos != -1:
                short_descr = descr[:pos].strip()
            else:
                short_descr = ""
            if board_name := find_board_designator(descr, short_descr):
                self.board = board_name
            else:
                self.board = "UNKNOWN"

    def disconnect(self) -> bool:
        """Disconnect from a board"""
        if not self.connected:
            return True
        if not self.serialport:
            log.error("No port connected")
            self.connected = False
            return False
        log.info(f"Disconnecting from {self.serialport}")
        result = self.run_command(["disconnect"])[0] == OK
        self.connected = False
        return result

    @retry(stop=stop_after_attempt(RETRIES), wait=wait_fixed(2))
    def run_command(
        self,
        cmd: Union[str, List[str]],
        *,
        log_errors: bool = True,
        no_info: bool = False,
        timeout: int = 60,
        **kwargs,
    ):
        """Run mpremote with the given command
        Parameters
        ----------
        cmd : Union[str,List[str]]
            The command to run, either a string or a list of strings
        check : bool, optional
            If True, raise an exception if the command fails, by default False
        Returns
        -------
        bool
            True if the command succeeded, False otherwise
        """
        if isinstance(cmd, str):
            cmd = cmd.split(" ")
        prefix = [sys.executable, "-m", "mpremote", "connect", self.serialport] if self.serialport else ["mpremote"]
        # if connected add resume to keep state between commands
        if self.connected:
            prefix += ["resume"]
        cmd = prefix + cmd
        log.debug(" ".join(cmd))
        result = run(cmd, timeout, log_errors, no_info, **kwargs)
        self.connected = result[0] == OK
        return result

    @retry(stop=stop_after_attempt(RETRIES), wait=wait_fixed(1))
    def mip_install(self, name: str) -> bool:
        """Install a micropython package"""
        # install createstubs to the board
        cmd = ["mip", "install", name]
        result = self.run_command(cmd)[0] == OK
        self.connected = True
        return result
