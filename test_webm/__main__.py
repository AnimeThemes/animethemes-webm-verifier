"""Verify WebM(s) Against /r/AnimeThemes Encoding Standards"""

import argparse
import logging
import os
import shutil
import sys
import unittest

from ._test_group import TestGroup
from ._utils import file_arg_type
from ._webm_format import WebmFormat


def main():
    """Verify WebM(s) Against /r/AnimeThemes Encoding Standards"""
    # Load/Validate Arguments
    parser = argparse.ArgumentParser(
        prog="test_webm",
        description="Verify WebM(s) Against /r/AnimeThemes Encoding Standards",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "file",
        nargs="*",
        default=[f for f in os.listdir(".") if f.endswith(".webm")],
        type=file_arg_type,
        help="The WebM(s) to verify",
    )

    parser.add_argument(
        "--loglevel",
        nargs="?",
        default="info",
        choices=["debug", "info", "error"],
        help="Set logging level",
    )

    parser.add_argument(
        "--groups",
        nargs="*",
        default=[group.value for group in TestGroup],
        choices=[group.value for group in TestGroup],
        help="Select groups of tests to run",
    )

    args = parser.parse_args()

    # Logging Config
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.getLevelName(args.loglevel.upper()),
        format="%(levelname)s: %(message)s",
    )

    # Env Check: Check that dependencies are installed
    if shutil.which("ffmpeg") is None:
        logging.error("FFmpeg is required")
        sys.exit()

    if shutil.which("ffprobe") is None:
        logging.error("FFprobe is required")
        sys.exit()

    if not args.file:
        logging.error("No WebMs to verify")
        sys.exit()

    logging.info("Verifying files...")

    for file in args.file:
        logging.info("Using file '%s'...", file)

        webm_format = WebmFormat(file)

        # dump formats and stream information on debug
        if logging.root.isEnabledFor(logging.DEBUG):
            webm_format.debug_dump()

        logging.info("Running Tests...")
        test_loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        for group in args.groups:
            test_group = TestGroup.value_of(group)
            test_class = test_group.test_class
            test_names = test_loader.getTestCaseNames(test_class)

            for test_name in test_names:
                suite.addTest(test_class(test_name, webm_format))

        unittest.TextTestRunner().run(suite)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.error("Exiting after keyboard interrupt")
