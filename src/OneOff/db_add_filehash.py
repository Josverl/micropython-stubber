"""
update all databases in the project with a new key "stubhash"
"""
from pathlib import Path

from stubber.publish.database import get_database
from stubber.utils.config import CONFIG


def update_db(source: Path, production: bool):
    db = get_database(source, production=False)
    # check if key is already in the database
    db_keys = db._load_file()["keys"]  # type: ignore

    assert isinstance(db_keys, list)
    if len(db_keys) == 0:
        raise IndexError(f"no keys in database, or empty database '{db.filename}'")
    if "stub_hash" not in db_keys:
        db.add_new_key("stub_hash", "")

    db = get_database(source, production=False)
    db_keys = db._load_file()["keys"]  # type: ignore
    print(db_keys)
    assert isinstance(db_keys, list)
    assert "stub_hash" in db_keys


# # test - test-PyPi
# update_db(Path("./tests/publish/data"), False)

# # publish - test-PyPi
# update_db(Path("./repos/micropython-stubs/publish"), False)
# # publish - PyPi
# update_db(Path("./repos/micropython-stubs/publish"), True)

# publish - test-PyPi
update_db(CONFIG.publish_path, production=False)
# publish - PyPi
update_db(CONFIG.publish_path, production=True)
