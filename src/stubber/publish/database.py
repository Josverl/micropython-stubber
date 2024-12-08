"""basic interface to the json database"""

import sqlite3
from pathlib import Path
from typing import Union

from pysondb import PysonDB


def get_database(publish_path: Path, production: bool = False) -> sqlite3.Connection:
    """
    Open the sqlite database at the given path.

    The database should be located in a subfolder `/data` of the root path.
    The database name is determined by the production flag as `all_packages[_test].db`
    """

    publish_path = Path(publish_path)
    db_path = publish_path / f"all_packages{'' if production else '_test'}.db"
    if not db_path.exists():
        raise FileNotFoundError("Database file not found")

    conn = sqlite3.connect(db_path)
    return conn


