import uos as os
import time


def countdown():
    for i in range(5, 0, -1):
        print("start stubbing in {}...".format(i))
        time.sleep(1)
    import createstubs


try:
    # only run import if no stubs yet
    os.listdir("stubs")
    print("stub folder was found, stubbing is not automatically started")

except OSError:
    countdown()
