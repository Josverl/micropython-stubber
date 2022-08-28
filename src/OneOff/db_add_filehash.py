"""
update all databases in the project with a new key "stubhash"
"""
from pathlib import Path

from pysondb.db import PysonDB
from stubber.publish.database import get_database


def update_db(source: Path, production: bool):
    db = get_database(source, production=False)
    # check if key is already in the database
    db_keys = db._load_file()["keys"]

    assert isinstance(db_keys, list)
    if len(db_keys) == 0:
        raise Exception(f"no keys in database, or empty database '{db.filename}'")
    if not "stubhash" in db_keys:
        db.add_new_key("stubhash", "")

    db = get_database(source, production=False)
    db_keys = db._load_file()["keys"]
    print(db_keys)
    assert isinstance(db_keys, list)
    assert "stubhash" in db_keys


# test - test-PyPi
update_db(Path("./tests/publish/data"), False)

# publish - test-PyPi
update_db(Path("./"), False)
# publish - PyPi
update_db(Path("./"), True)