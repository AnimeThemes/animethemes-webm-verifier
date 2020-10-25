import argparse
import os


# Validate Arguments: check that file is readable and is a WebM
def file_arg_type(arg_value):
    if not os.access(arg_value, os.R_OK):
        raise argparse.ArgumentTypeError(f'File \'{arg_value}\' does not exist')
    if not arg_value.endswith('.webm'):
        raise argparse.ArgumentTypeError(f'File \'{arg_value}\' is not WebM')
    return arg_value
