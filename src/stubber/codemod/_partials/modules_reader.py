"""partial used to read the modulelist.txt file"""
###PARTIAL###
# Read stubs from modulelist in the current folder or in /libs
# fall back to default modules
stubber.modules = ["micropython"]
for p in ["", "/libs"]:
    try:
        with open(p + "modulelist" + ".txt") as f:
            # not optimal , but works on mpremote and eps8266
            stubber.modules = [l.strip() for l in f.read().split("\n") if len(l.strip()) and l.strip()[0] != "#"]
            break
    except OSError:
        pass
###PARTIALEND###
