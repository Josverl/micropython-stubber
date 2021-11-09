import logging
import machine
import random
import btree

_log = logging.getLogger("stubber")
was_running = False

def print_db():
    with open("modulelist.db", "r+b") as f:
        db = btree.open(f)
        for key in db.keys():
            print("{0:<32} {1}".format(key, db[key]))      
        db.close()

def esp8266():
    try:
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.DEBUG)
    except NameError:
        pass

    try:
        f = open("modulelist.db", "r+b")
        was_running = True
        _log.info("Opened existing db")
    except OSError:
        f = open("modulelist.db", "w+b")
        _log.info("created new db")
        was_running = False
        # load modulelist into database
    # Now open a database
    db = btree.open(f)
    # if started with no or empty database
    if not was_running or len(list(db.keys())) == 0:
        # load textfile into DB
        _log.info("load modulelist into db")
        for line in open("modulelist.txt"):
            line = line.strip()
            if len(line) and line[0] != "#":
                db[line] = b"todo"
        db.flush()

    n = 0
    for key in db.keys():
        print("{0:<32} {1}".format(key, db[key]))
        if db[key] != b"todo":
            continue

        # sometimes things fail
        X = random.getrandbits(4)
        if X == 6:

            machine.reset()
        result = "done {} - {}".format(X, n)
        _log.info(result)
        db[key] = result
        n += 1
        db.flush()
    # Finished processing
    for key in db.keys():
        print("{0:<32} {1}".format(key, db[key]))

    db.close()
    f.close()


esp8266()
