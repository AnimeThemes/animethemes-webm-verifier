"""A collection of utility functions"""

import argparse
import os


def file_arg_type(arg_value):
    """Test if the file is readable and is a WebM"""
    if not os.access(arg_value, os.R_OK):
        raise argparse.ArgumentTypeError(f"File '{arg_value}' does not exist")
    if not arg_value.endswith(".webm"):
        raise argparse.ArgumentTypeError(f"File '{arg_value}' is not WebM")
    return arg_value
