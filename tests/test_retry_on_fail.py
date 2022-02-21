import pytest

from gtfs_validator_api import retry_on_fail


def test_retry_on_fail():
    n = 0

    def raises():
        nonlocal n
        if n == 0:
            n += 1
            raise Exception("failed")

    retry_on_fail(lambda: raises(), 1)


def test_retry_on_fail_stops():
    n = 0

    def raises():
        nonlocal n

        if n == 1:
            raise Exception("failed")
        else:
            n += 1

    with pytest.raises(Exception):
        retry_on_fail(lambda: raises(), 1)
