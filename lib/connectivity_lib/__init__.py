
"""
My local Python connectivity library for Splunk.
"""

from exceptions import *
from constants import *

__version_info__ = (0, 0, 3)
__version__ = ".".join(map(str, __version_info__))

__all__ = ["pinger", "webtest", "connect_test"]

