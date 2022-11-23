from pathlib import Path
from typing import Union

from pysondb import PysonDB


def get_database(publish_path: Union[Path, str], production: bool = False) -> PysonDB:
    """
    Open the json database at the given path.

    The database should be located in a subfolder `/publish` of the root path.
    The database name is determined by the production flag as `package_data[_test].jsondb`
    """
    publish_path = Path(publish_path)
    db_path = publish_path / f"package_data{'' if production else '_test'}.jsondb"
    return PysonDB(db_path.as_posix())
