import os
import sys

from pyscript import fs  # type: ignore


def create_stubs():
    import createstubs  # type: ignore

    # Just importing runs the stub creation
    return


# May ask for permission from the user, and select the local target.
path = "/stubs"

try:
    await fs.mount(path)
except AttributeError:
    # PyScript 2026.x: stale IDB entry (from an older PyScript session) causes
    # _check_permission() to fail with 'JsProxy has no attribute handler'.
    # Revoke the stored handle so the next mount() starts fresh.
    print("Stale filesystem handle detected — revoking and re-mounting...")
    await fs.revoke(path)
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
