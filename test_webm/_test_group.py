"""An enumeration of test groups"""

from enum import Enum
from ._test_audio import TestAudio
from ._test_format import TestFormat
from ._test_video import TestVideo


# The enumeration of test groups
class TestGroup(Enum):
    """An enumeration of test groups"""
    def __new__(cls, value, test_class):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.test_class = test_class
        return obj

    FORMAT = ('format', TestFormat)
    VIDEO = ('video', TestVideo)
    AUDIO = ('audio', TestAudio)
