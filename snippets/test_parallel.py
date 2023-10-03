import time

import fasteners
import pytest


# create a test than can be run in parrallel
@pytest.mark.parametrize("x", [1, 2, 3, 4, 5])
def test_parallel(x):
    id = x % 2
    lock = fasteners.InterProcessLock(f"path/to/lock_{id}.file")
    with lock:
        time.sleep(x)
        ...  # exclusive access


# create a test than can be run in parrallel
@pytest.mark.parametrize("x", [1, 2, 3, 4, 5])
def test_slow(x):
    id = x % 2
    lock = fasteners.InterProcessLock(f"path/to/lock_{id}.file")
    with lock:
        time.sleep(x + 3)
        ...  # exclusive access
