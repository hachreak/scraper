
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


def save_json(filename, data):
    """Save json file."""
    with open(filename, 'w') as f:
        json.dump(data, f)


def count_lines(filename):
    """Count file lines."""
    return sum(1 for i in open(filename, 'rb'))


def fill_buffer(fun, size):
    """Call function passing a buffer filled of `size` elements."""
    def f(input_buffer):
        """Extend buffer with the list of values."""
        out = {}
        for elements in input_buffer:
            out.update(fun(elements))
            if size != -1 and len(out) >= size:
                yield out
                out = {}
        if len(out) > 0:
            yield out
    return f
