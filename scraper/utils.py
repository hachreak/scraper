
"""Utils."""

import json

from selenium.common.exceptions import StaleElementReferenceException
from time import sleep

from .exc import UnknowObject


def try_again(fun, exc=StaleElementReferenceException, times=5, sleep_time=1):
    for _ in range(times):
        try:
            return fun()
        except exc:
            sleep(sleep_time)

    raise UnknowObject()


def load_json(filename):
    """Load json file."""
    content = None
    with open(filename, 'r') as f:
        content = json.load(f)
    return content


def count_lines(filename):
    """Count file lines."""
    return sum(1 for i in open(filename, 'rb'))
