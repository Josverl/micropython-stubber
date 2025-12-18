import os
import sys
import time

from pyscript import fs


def create_stubs():
    # create file no_auto_stubber.txt
    with open("no_auto_stubber.txt", "w") as f:
        f.write("This file prevents automatic stub generation on next start.\n")
        f.write("You can delete this file to enable automatic stub generation again.\n")

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
    time.sleep(1)
