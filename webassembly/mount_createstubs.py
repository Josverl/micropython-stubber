import os
import sys

from pyscript import fs


def create_stubs():
    import createstubs

    return


# May ask for permission from the user, and select the local target.
await fs.mount("/stubs")

print(sys.path)
print(f"{sys.implementation.name} {sys.implementation.version}")

print("cwd:", os.getcwd())
# ------------------------------------
# create_stubbies()
create_stubs()
# ------------------------------------
# synchronize the changes to the local file system
print("Please wait 🕧🕐🕜🕑🕝🕒🕛")
await fs.sync("/stubs")

print("✅✅✅✅✅✅✅✅ Synced /stubs")

# await fs.unmount("/stubs")
# print("Unmounted /stubs")

while True:
    await asyncio.sleep(1)
