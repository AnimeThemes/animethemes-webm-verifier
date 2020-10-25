from ._test_webm import TestWebm
from ._utils import file_arg_type

import argparse
import logging
import os
import shutil
import sys
import unittest


def main():
    # Load/Validate Arguments
    parser = argparse.ArgumentParser(prog='test_webm',
                                     description='Verify WebM(s) Against /r/AnimeThemes Encoding Standards',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file',
                        nargs='*',
                        default=[f for f in os.listdir('.') if f.endswith('.webm')],
                        type=file_arg_type,
                        help='The WebM(s) to verify')
    parser.add_argument('--loglevel',
                        nargs='?',
                        default='info',
                        choices=['debug', 'info', 'error'],
                        help='Set logging level')
    args = parser.parse_args()

    # Logging Config
    logging.basicConfig(stream=sys.stdout,
                        level=logging.getLevelName(args.loglevel.upper()),
                        format='%(levelname)s: %(message)s')

    # Env Check: Check that dependencies are installed
    if shutil.which('ffmpeg') is None:
        logging.error('FFmpeg is required')
        sys.exit()

    if shutil.which('ffprobe') is None:
        logging.error('FFprobe is required')
        sys.exit()

    if not args.file:
        logging.error('No WebMs to verify')
        sys.exit()

    logging.info('Verifying files...')

    for file in args.file:
        logging.info(f'Using file \'{file}\'...')

        # Source 1: WebM Streams/Formats
        logging.info('Retrieving WebmM stream/format data...')
        webm_format = TestWebm.get_webm_format(file)

        # Source 2: Extracted audio stream, needed for verifying audio bitrate
        logging.info('Retrieving extracted audio stream/format data...')
        audio_format = TestWebm.get_audio_format(file)

        # Source 3: Loudness stats
        logging.info('Retrieving loudness data...')
        loudness_stats = TestWebm.get_loudness_stats(file)

        # Source 4: Index of streams by codec type
        video_index = TestWebm.get_stream_index(webm_format, 'video')
        audio_index = TestWebm.get_stream_index(webm_format, 'audio')

        if logging.root.isEnabledFor(logging.DEBUG):
            logging.debug('Dumping test data...')
            logging.debug(f'video_index: \'{video_index}\'')
            logging.debug(f'audio_index: \'{audio_index}\'')
            logging.debug(f'webm_format[streams][0][codec_type]: \'{webm_format["streams"][0]["codec_type"]}\'')
            logging.debug(f'webm_format[streams][1][codec_type]: \'{webm_format["streams"][1]["codec_type"]}\'')
            logging.debug(f'len(webm_format[streams]): \'{len(webm_format["streams"])}\'')
            logging.debug(f'webm_format[format][format_name]: \'{webm_format["format"]["format_name"]}\'')
            logging.debug(f'webm_format[format][bit_rate]): \'{webm_format["format"]["bit_rate"]}\'')
            logging.debug(f'webm_format[streams][video_index][height]: '
                          f'\'{webm_format["streams"][video_index]["height"]}\'')
            logging.debug(f'webm_format[chapters]: \'{webm_format["chapters"]}\'')
            logging.debug(f'webm_format[streams][video_index][codec_name]: '
                          f'\'{webm_format["streams"][video_index]["codec_name"]}\'')
            logging.debug(f'webm_format[streams][video_index][pix_fmt]: '
                          f'\'{webm_format["streams"][video_index]["pix_fmt"]}\'')
            logging.debug(f'webm_format[streams][video_index].get(color_space): '
                          f'\'{webm_format["streams"][video_index].get("color_space")}\'')
            logging.debug(f'webm_format[streams][video_index].get(color_transfer): '
                          f'\'{webm_format["streams"][video_index].get("color_transfer")}\'')
            logging.debug(f'webm_format[streams][video_index].get(color_primaries): '
                          f'\'{webm_format["streams"][video_index].get("color_primaries")}\'')
            logging.debug(f'webm_format[streams][video_index][avg_frame_rate]: '
                          f'\'{webm_format["streams"][video_index]["avg_frame_rate"]}\'')
            logging.debug(f'webm_format[streams][audio_index][codec_name]: '
                          f'\'{webm_format["streams"][audio_index]["codec_name"]}\'')
            logging.debug(f'[loudness_stats] input_i: '
                          f'\'{loudness_stats["input_i"]}\', '
                          f'input_lra: \'{loudness_stats["input_lra"]}\', '
                          f'input_tp: \'{loudness_stats["input_tp"]}\', '
                          f'input_thresh: \'{loudness_stats["input_thresh"]}\', '
                          f'target_offset: \'{loudness_stats["target_offset"]}\'')
            logging.debug(f'audio_format[format][bitrate]: \'{audio_format["format"]["bit_rate"]}\'')
            logging.debug(f'webm_format[streams][audio_index][sample_rate]: '
                          f'\'{webm_format["streams"][audio_index]["sample_rate"]}\'')
            logging.debug(f'webm_format[streams][audio_index][channels]: '
                          f'\'{webm_format["streams"][audio_index]["channels"]}\'')
            logging.debug(f'webm_format[streams][audio_index][channel_layout]: '
                          f'\'{webm_format["streams"][audio_index]["channel_layout"]}\'')

        logging.info('Running Tests...')
        test_loader = unittest.TestLoader()
        test_names = test_loader.getTestCaseNames(TestWebm)

        suite = unittest.TestSuite()
        for test_name in test_names:
            suite.addTest(TestWebm(test_name, webm_format, audio_format, loudness_stats, video_index, audio_index))

        unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.error('Exiting after keyboard interrupt')
