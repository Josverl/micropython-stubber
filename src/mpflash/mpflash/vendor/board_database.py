"""
The micropython git repo contains many 'board.json' files.

This is an example:
ports/stm32/boards/PYBV11/board.json

{
    "deploy": [
        "../PYBV10/deploy.md"
    ],
    "docs": "",
    "features": [],
    "images": [
        "PYBv1_1.jpg",
        "PYBv1_1-C.jpg",
        "PYBv1_1-E.jpg"
    ],
    "mcu": "stm32f4",
    "product": "Pyboard v1.1",
    "thumbnail": "",
    "url": "https://store.micropython.org/product/PYBv1.1",
    "variants": {
        "DP": "Double-precision float",
        "DP_THREAD": "Double precision float + Threads",
        "NETWORK": "Wiznet 5200 Driver",
        "THREAD": "Threading"
    },
    "vendor": "George Robotics"
}

This module implements `class Database` which reads all 'board.json' files and
provides a way to browse it's data.
"""

from __future__ import annotations

from pathlib import Path
import json
from dataclasses import dataclass, field
from glob import glob


@dataclass(order=True)
class Variant:
    name: str
    """
    Example: "DP_THREAD"
    """
    text: str
    """
    Example: "Double precision float + Threads"
    """
    board: Board = field(repr=False)


@dataclass(order=True)
class Board:
    name: str
    """
    Example: "PYBV11"
    """
    variants: list[Variant]
    """
    List of variants available for this board.
    Variants are sorted. May be an empty list if no variants are available.
    Example key: "DP_THREAD"
    """
    url: str
    """
    Primary URL to link to this board.
    """
    mcu: str
    """
    Example: "stm32f4"
    """
    product: str
    """
    Example: "Pyboard v1.1"
    """
    vendor: str
    """
    Example: "George Robotics"
    """
    images: list[str]
    """
    Images of this board, stored in the micropython-media repository.
    Example: ["PYBv1_1.jpg", "PYBv1_1-C.jpg", "PYBv1_1-E.jpg"]
    """
    deploy: list[str]
    """
    Files that explain how to deploy for this board:
    Example: ["../PYBV10/deploy.md"]
    """
    port: Port | None= field(default=None, compare=False)

    @staticmethod
    def factory(filename_json: Path) -> Board:
        with filename_json.open() as f:
            board_json = json.load(f)

        board = Board(
            name=filename_json.parent.name,
            variants=[],
            url=board_json["url"],
            mcu=board_json["mcu"],
            product=board_json["product"],
            vendor=board_json["vendor"],
            images=board_json["images"],
            deploy=board_json["deploy"],
        )
        board.variants.extend(
            sorted([Variant(*v, board) for v in board_json.get("variants", {}).items()])
        )
        return board


@dataclass(order=True)
class Port:
    name: str
    """
    Example: "stm32"
    """
    boards: dict[str, Board] = field(default_factory=dict, repr=False)
    """
    Example key: "PYBV11"
    """


@dataclass
class Database:
    """
    This database contains all information retrieved from all 'board.json' files.
    """

    mpy_root_directory: Path = field(repr=False)
    port_filter: str = field(default="", repr=False)

    ports: dict[str, Port] = field(default_factory=dict)
    boards: dict[str, Board] = field(default_factory=dict)

    def __post_init__(self) -> None:
        mpy_dir = self.mpy_root_directory
        # Take care to avoid using Path.glob! Performance was 15x slower.
        for p in glob(f"{mpy_dir}/ports/**/boards/**/board.json"):
            filename_json = Path(p)
            port_name = filename_json.parent.parent.parent.name
            if self.port_filter and self.port_filter != port_name:
                continue

            # Create a port
            port = self.ports.get(port_name, None)
            if port is None:
                port = Port(port_name)
                self.ports[port_name] = port

            # Load board.json and attach it to the board
            board = Board.factory(filename_json)
            board.port = port

            port.boards[board.name] = board
            self.boards[board.name] = board

        # Add 'special' ports, that don't have boards
        # TODO(mst) Tidy up later (variant descriptions etc)
        for special_port_name in ["unix", "webassembly", "windows"]:
            if self.port_filter and self.port_filter != special_port_name:
                continue
            path = Path(mpy_dir, "ports", special_port_name)
            variant_names = [
                var.name for var in path.glob("variants/*") if var.is_dir()
            ]
            board = Board(
                special_port_name,
                [],
                f"https://github.com/micropython/micropython/blob/master/ports/{special_port_name}/README.md",
                "",
                "",
                "",
                [],
                [],
            )
            board.variants = [Variant(v, "", board) for v in variant_names]
            port = Port(special_port_name, {special_port_name: board})
            board.port = port

            self.ports[special_port_name] = port
            self.boards[board.name] = board
