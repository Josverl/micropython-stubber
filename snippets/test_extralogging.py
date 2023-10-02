import logging

import pytest

pytest.skip("---===*** DEBUGGING ***===---", allow_module_level=True)

log = logging.getLogger()

msg = """snippets\\feat_micropython\\check_machine\\check_memNNN.py:12: Operator "+" not supported for types "int | bytes | str | Tuple[Unknown, ...]" and "int | bytes | str | Tuple[Unknown, ...]"""

lr = logging.LogRecord(
    "pyright",
    40,
    "snippets\\feat_micropython\\check_machine\\check_memNNN.py",
    12,
    """SNAFU""",
    None,
    None,
)


def test_func2(caplog):
    log.warn(msg)
    assert False


def test_logging(caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.INFO)
    log.error(msg)
    assert 0
