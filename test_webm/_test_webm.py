"""A collection of tests to verify the file against encoding standards"""

from unittest import TestCase


class TestWebm(TestCase):
    """A collection of tests to verify the file against encoding standards

    :param testname: the name of the test to run
    :type testname: str

    :param webm_format: the file being tested
    :type webm_format: WebmFormat
    """

    def __init__(self, testname, webm_format):
        super().__init__(testname)
        self.webm_format = webm_format
