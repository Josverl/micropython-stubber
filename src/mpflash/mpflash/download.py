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
from bs4 import BeautifulSoup
from loguru import logger as log
from rich.progress import track

from .common import PORT_FWTYPES, clean_version

MICROPYTHON_ORG_URL = "https://micropython.org/"

# Regexes to remove dates and hashes in the filename that just get in the way
RE_DATE = r"(-\d{8}-)"
RE_HASH = r"(.g[0-9a-f]+\.)"
# regex to extract the version from the firmware filename
RE_VERSION_PREVIEW = r"(\d+\.\d+(\.\d+)?(-\w+.\d+)?)"


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
def get_boards(ports: List[str], boards: List[str], clean: bool) -> List[FirmwareInfo]:
    board_urls: List[FirmwareInfo] = []
    for port in ports:
        download_page_url = f"{MICROPYTHON_ORG_URL}download/?port={port}"
        _urls = get_board_urls(download_page_url)
        # filter out boards we don't care about
        _urls = [board for board in _urls if board["board"] in boards]
        # add the port to the board urls
        for board in _urls:
            board["port"] = port

        for board in track(_urls, description=f"Checking {port} download pages", transient=True):
            # add a board to the list for each firmware found
            firmwares = []
            for ext in PORT_FWTYPES[port]:
                firmwares += firmware_list(board["url"], MICROPYTHON_ORG_URL, ext)

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
                board["ext"] = Path(board["firmware"]).suffix
                board["variant"] = board["filename"].split("-v")[0] if "-v" in board["filename"] else ""
                board_urls.append(board.copy())
    return board_urls


def key_fw_ver_pre_ext_bld(x: FirmwareInfo):
    "sorting key for the retrieved board urls"
    return x["variant"], x["version"], x["preview"], x["ext"], x["build"]


def key_fw_var_pre_ext(x: FirmwareInfo):
    "Grouping key for the retrieved board urls"
    return x["variant"], x["preview"], x["ext"]


def download_firmwares(
    firmware_folder: Path,
    ports: List[str],
    boards: List[str],
    versions: Optional[List[str]] = None,
    *,
    preview: bool = False,
    force: bool = False,
    clean: bool = True,
):
    skipped = downloaded = 0
    if versions is None:
        versions = []
    unique_boards = get_firmware_list(ports, boards, versions, preview, clean)

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
            log.info(f"Downloading {board['firmware']}")
            log.info(f"         to {filename}")
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


def get_firmware_list(ports: List[str], boards: List[str], versions: List[str], preview: bool, clean: bool):
    log.trace("Checking MicroPython download pages")

    board_urls = sorted(get_boards(ports, boards, clean), key=key_fw_ver_pre_ext_bld)

    log.debug(f"Total {len(board_urls)} firmwares")
    relevant = [
        board
        for board in board_urls
        if board["board"] in boards and (board["version"] in versions or board["preview"] and preview)
        # and b["port"] in ["esp32", "rp2"]
    ]
    log.debug(f"Matching firmwares: {len(relevant)}")
    # select the unique boards
    unique_boards: List[FirmwareInfo] = []
    for _, g in itertools.groupby(relevant, key=key_fw_var_pre_ext):
        # list is aleady sorted by build so we can just get the last item
        sub_list = list(g)
        unique_boards.append(sub_list[-1])
    log.debug(f"Last preview only: {len(unique_boards)}")
    return unique_boards


def download(
    destination: Path,
    ports: List[str],
    boards: List[str],
    versions: List[str],
    force: bool,
    clean: bool,
    preview: bool,
):
    if not boards:
        log.critical("No boards found, please connect a board or specify boards to download firmware for.")
        exit(1)
    versions = [clean_version(v, drop_v=True) for v in versions]  # remove leading v from version
    try:
        destination.mkdir(exist_ok=True, parents=True)
    except (PermissionError, FileNotFoundError) as e:
        log.critical(f"Could not create folder {destination}\n{e}")
        exit(1)
    download_firmwares(destination, ports, boards, versions, preview=preview, force=force, clean=clean)
