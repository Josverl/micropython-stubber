"""
Module to download MicroPython firmware for specific boards and versions.
Uses the micropython.org website to get the available versions and locations to download firmware files.
"""

import functools
import itertools
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
import rich_click as click
from bs4 import BeautifulSoup
from loguru import logger as log
from rich.progress import track

from .cli_group import cli
from .common import DEFAULT_FW_PATH, PORT_FWTYPES, clean_version

MICROPYTHON_ORG_URL = "https://micropython.org/"

# Regexes to remove dates and hashes in the filename that just get in the way
RE_DATE = r"(-\d{8}-)"
RE_HASH = r"(.g[0-9a-f]+\.)"
# regex to extract the version from the firmware filename
RE_VERSION_PREVIEW = r"(\d+\.\d+(\.\d+)?(-\w+.\d+)?)"

# boards we are interested in ( this avoids getting a lot of boards that are not relevant)
DEFAULT_BOARDS = [
    "PYBV11",
    "ESP8266_GENERIC",
    "ESP32_GENERIC",
    "ESP32_GENERIC_S3",
    "RPI_PICO",
    "RPI_PICO_W",
    "ADAFRUIT_QTPY_RP2040",
    "ARDUINO_NANO_RP2040_CONNECT",
    "PIMORONI_PICOLIPO_16MB",
    "SEEED_WIO_TERMINAL",
    "PARTICLE_XENON",
]


# use functools.lru_cache to avoid needing to download pages multiple times
@functools.lru_cache(maxsize=500)
def get_page(page_url: str) -> str:
    """Get the HTML of a page and return it as a string."""
    response = requests.get(page_url)
    return response.content.decode()


@functools.lru_cache(maxsize=500)
def get_board_urls(page_url: str) -> List[Dict[str, str]]:
    """
    Get the urls to all the board pages listed on this page.
    Assumes that all links to firmware  have "class": "board-card"
    """
    downloads_html = get_page(page_url)
    soup = BeautifulSoup(downloads_html, "html.parser")
    tags = soup.findAll("a", recursive=True, attrs={"class": "board-card"})
    # assumes that all links are relative to the page url
    boards = [tag.get("href") for tag in tags]
    if "?" in page_url:
        page_url = page_url.split("?")[0]
    return [{"board": board, "url": page_url + board} for board in boards]


def firmware_list(board_url: str, base_url: str, ext: str) -> List[str]:
    """Get the urls to all the firmware files for a board."""
    html = get_page(board_url)
    soup = BeautifulSoup(html, "html.parser")
    # get all the a tags:
    #  1. that have a url that starts with `/resources/firmware/`
    #  2. end with a matching extension for this port.
    tags = soup.findAll(
        "a",
        recursive=True,
        attrs={"href": re.compile(r"^/resources/firmware/.*\." + ext.lstrip(".") + "$")},
    )
    if "?" in base_url:
        base_url = base_url.split("?")[0]
    links: List = [urljoin(base_url, tag.get("href")) for tag in tags]
    return links


# type alias for the firmware info
FirmwareInfo = Dict[str, str]


# boards we are interested in ( this avoids getting a lot of boards we don't care about)
# The first run takes ~60 seconds to run for 4 ports , all boards
# so it makes sense to cache the results and skip boards as soon as possible
def get_boards(fw_types: Dict[str, str], board_list: List[str], clean: bool) -> List[FirmwareInfo]:
    board_urls: List[FirmwareInfo] = []
    for port in fw_types:
        download_page_url = f"{MICROPYTHON_ORG_URL}download/?port={port}"
        _urls = get_board_urls(download_page_url)
        # filter out boards we don't care about
        _urls = [board for board in _urls if board["board"] in board_list]
        # add the port to the board urls
        for board in _urls:
            board["port"] = port

        for board in track(_urls, description=f"Checking {port} download pages", transient=True):
            # add a board to the list for each firmware found
            firmwares = firmware_list(board["url"], MICROPYTHON_ORG_URL, fw_types[port])
            for _url in firmwares:
                board["firmware"] = _url
                board["preview"] = "preview" in _url  # type: ignore
                if ver_match := re.search(RE_VERSION_PREVIEW, _url):
                    board["version"] = ver_match[1]
                else:
                    board["version"] = ""
                if "preview." in board["version"]:
                    board["build"] = board["version"].split("preview.")[-1]
                else:
                    board["build"] = "0"
                fname = Path(board["firmware"]).name
                if clean:
                    # remove date from firmware name
                    fname = re.sub(RE_DATE, "-", fname)
                    # remove hash from firmware name
                    fname = re.sub(RE_HASH, ".", fname)
                board["filename"] = fname
                board["variant"] = board["filename"].split("-v")[0] if "-v" in board["filename"] else ""
                board_urls.append(board.copy())
    return board_urls


def key_fw_variant_ver(x: FirmwareInfo):
    "sorting key for the retrieved board urls"
    return x["variant"], x["version"], x["preview"], x["build"]


def key_fw_variant(x: FirmwareInfo):
    "Grouping key for the retrieved board urls"
    return x["variant"], x["preview"]


def download_firmwares(
    firmware_folder: Path,
    board_list: List[str],
    version_list: Optional[List[str]] = None,
    *,
    preview: bool = False,
    force: bool = False,
    clean: bool = True,
):
    skipped = downloaded = 0
    if version_list is None:
        version_list = []
    unique_boards = get_firmware_list(board_list, version_list, preview, clean)

    for b in unique_boards:
        log.debug(b["filename"])
    # relevant

    log.info(f"Found {len(unique_boards)} relevant unique firmwares")

    firmware_folder.mkdir(exist_ok=True)

    with open(firmware_folder / "firmware.jsonl", "a", encoding="utf-8", buffering=1) as f_jsonl:
        for board in unique_boards:
            filename = firmware_folder / board["port"] / board["filename"]
            filename.parent.mkdir(exist_ok=True)
            if filename.exists() and not force:
                skipped += 1
                log.debug(f" {filename} already exists, skip download")
                continue
            log.info(f"Downloading {board['firmware']} to {filename}")
            try:
                r = requests.get(board["firmware"], allow_redirects=True)
                with open(filename, "wb") as fw:
                    fw.write(r.content)
                board["filename"] = str(filename.relative_to(firmware_folder))
            except requests.RequestException as e:
                log.exception(e)
                continue
            # add the firmware to the jsonl file
            json_str = json.dumps(board) + "\n"
            f_jsonl.write(json_str)
            downloaded += 1
    log.info(f"Downloaded {downloaded} firmwares, skipped {skipped} existing files.")


def get_firmware_list(board_list: List[str], version_list: List[str], preview: bool, clean: bool):
    log.trace("Checking MicroPython download pages")

    board_urls = sorted(get_boards(PORT_FWTYPES, board_list, clean), key=key_fw_variant_ver)

    log.debug(f"Total {len(board_urls)} firmwares")
    relevant = [
        board
        for board in board_urls
        if board["board"] in board_list and (board["version"] in version_list or board["preview"] and preview)
        # and b["port"] in ["esp32", "rp2"]
    ]
    log.debug(f"Matching firmwares: {len(relevant)}")
    # select the unique boards
    unique_boards: List[FirmwareInfo] = []
    for _, g in itertools.groupby(relevant, key=key_fw_variant):
        # list is aleady sorted by build so we can just get the last item
        sub_list = list(g)
        unique_boards.append(sub_list[-1])
    log.debug(f"Last preview only: {len(unique_boards)}")
    return unique_boards


@cli.command(
    "download",
    help="Download MicroPython firmware for specific ports, boards and versions.",
)
@click.option(
    "--destination",
    "-d",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=DEFAULT_FW_PATH,
    show_default=True,
    help="The folder to download the firmware to.",
)
@click.option(
    "--version",
    "-v",
    "versions",
    multiple=True,
    help="The version of MicroPython to to download. Use 'preview' to include preview versions.",
    show_default=True,
    default=["stable"],
)
@click.option(
    "--board",
    "-b",
    "boards",
    multiple=True,
    show_default=True,
    help="The board(s) to download the firmware for.",  # Use '--board all' to download all boards.",
)
@click.option(
    "--clean/--no-clean",
    default=True,
    show_default=True,
    help="""Remove dates and hashes from the downloaded firmware filenames.""",
)
@click.option(
    "--force",
    default=False,
    is_flag=True,
    help="""Force download of firmware even if it already exists.""",
    show_default=True,
)
def download(destination: Path, boards: List[str], versions: List[str], force: bool, clean: bool):
    versions = list(versions)
    # preview is not a version, it is an option to include preview versions
    preview = "preview" in versions
    versions = [v for v in versions if v != "preview"]

    boards = list(boards) or DEFAULT_BOARDS
    versions = [clean_version(v, drop_v=True) for v in versions]  # remove leading v from version
    try:
        destination.mkdir(exist_ok=True, parents=True)
    except (PermissionError, FileNotFoundError) as e:
        log.critical(f"Could not create folder {destination}\n{e}")
        exit(1)
    download_firmwares(destination, boards, versions, preview=preview, force=force, clean=clean)
