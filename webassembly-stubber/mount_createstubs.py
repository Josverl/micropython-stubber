import os
import sys

from pyscript import fs  # type: ignore


def create_stubs():
    import createstubs  # type: ignore

    # Just importing runs the stub creation
    return


# May ask for permission from the user, and select the local target.
path = "/stubs"

async def _revoke_mount(path):
    """Remove the stored IDB handle for path, works across PyScript versions."""
    if hasattr(fs, "revoke"):
        await fs.revoke(path)
    else:
        # Older PyScript: delete just the entry for this path from the IDB store.
        # deleteDatabase is blocked because PyScript keeps the connection open,
        # so we open the DB ourselves and delete only the /stubs key instead.
        import js

        await js.eval(f"""
            new Promise((resolve, reject) => {{
                const req = indexedDB.open('IDBMap/@pyscript.fs', 1);
                req.onsuccess = (e) => {{
                    const db = e.target.result;
                    const tx = db.transaction('entries', 'readwrite');
                    const delReq = tx.objectStore('entries').delete({path!r});
                    delReq.onsuccess = () => {{ db.close(); resolve('entry deleted'); }};
                    delReq.onerror  = (e) => {{ db.close(); resolve('delete error: ' + e.target.error); }};
                }};
                req.onerror = (e) => resolve('open failed: ' + e.target.error);
            }})
        """)


try:
    await fs.mount(path)
except (AttributeError, Exception) as e:
    # Stale IDB entry can surface as either:
    #   AttributeError  – PyScript 2026.x _check_permission 'handler' missing
    #   JsException     – "Expected argument 'fileSystemHandle' to be a FileSystemDirectoryHandle"
    print(f"Filesystem handle error ({type(e).__name__}: {e}) — revoking and re-mounting...")
    await _revoke_mount(path)
    await fs.mount(path)

# recreate the ID / cookies prompt

print(sys.path)
print(f"{sys.implementation.name} {sys.implementation.version}")

print("cwd:", os.getcwd())
# ------------------------------------
create_stubs()
# ------------------------------------
print("synchronize the changes to the local file system")
print("Please wait...🕧🕐🕜🕑🕝🕒🕛")
await fs.sync("/stubs")
print("Synced /stubs ✅✅✅✅✅✅✅")


# await fs.unmount("/stubs")
# print("Unmounted /stubs")
import asyncio

while True:
    await asyncio.sleep(1)
