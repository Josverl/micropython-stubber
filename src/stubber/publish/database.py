"""Interface to the database which stores the package information"""

import sqlite3
from pathlib import Path


def get_database(db_path: Path, production: bool = False) -> sqlite3.Connection:
    """
    Open the sqlite database at the given path.

    The database should be located in a subfolder `/data` of the root path.
    The database name is determined by the production flag as `all_packages[_test].db`
    """
    db_path = Path(db_path)
    if db_path.stem == "publish":
        db_path = db_path / ".." / "data"  # go up one level to find the database

    db_path = db_path / f"all_packages{'' if production else '_test'}.db"
    if db_path.exists():
        conn = sqlite3.connect(db_path)

    else:
        print(FileNotFoundError(f"Database file not found in path: {db_path}"))
        conn = create_database(db_path)

    conn.row_factory = sqlite3.Row  # return rows as dicts
    return conn


def create_database(db_path: Path) -> sqlite3.Connection:
    """
    Create a new database at the given path.

    The database should be located in a subfolder `/data` of the root path.
    """
    db_path = Path(db_path)
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True)
    conn = sqlite3.connect(db_path)
    SCHEMA = """
    CREATE TABLE "packages" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            mpy_version TEXT,
            pkg_version TEXT,
            publish BOOLEAN,
            stub_sources TEXT, -- json string
            path TEXT,
            hash TEXT,
            stub_hash TEXT,
            port TEXT DEFAULT "",
            board TEXT DEFAULT "",
            variant TEXT DEFAULT ""
        )
    """
    conn.execute(SCHEMA)
    conn.commit
    return conn
