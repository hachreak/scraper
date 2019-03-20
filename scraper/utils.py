
"""Utils."""

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
