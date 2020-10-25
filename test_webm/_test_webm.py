from distutils.version import LooseVersion

import json
import os
import re
import subprocess
import unittest


class TestWebm(unittest.TestCase):
    format_args = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', '-show_format', '-show_chapters']

    def __init__(self, testname, webm_format, audio_format, loudness_stats, video_index, audio_index):
        super(TestWebm, self).__init__(testname)
        self.webm_format = webm_format
        self.audio_format = audio_format
        self.loudness_stats = loudness_stats
        self.video_index = video_index
        self.audio_index = audio_index

    # Source 1: WebM Streams/Formats
    @staticmethod
    def get_webm_format(file):
        webm_args = TestWebm.format_args + [file]
        webm_format = subprocess.check_output(webm_args).decode('utf-8')
        return json.loads(webm_format)

    # Source 2: Extracted audio stream, needed for verifying audio bitrate
    @staticmethod
    def get_audio_format(file):
        ogg_file = f'{file}.ogg'
        ogg_args = ['ffmpeg', '-v', 'quiet', '-i', file, '-vn', '-acodec', 'copy', '-f', 'ogg', '-y', ogg_file]
        subprocess.call(ogg_args)

        audio_args = TestWebm.format_args + [ogg_file]
        audio_format = subprocess.check_output(audio_args).decode('utf-8')
        audio_format = json.loads(audio_format)

        os.remove(ogg_file)

        return audio_format

    # Source 3: Loudness stats
    # Implementation: https://gist.github.com/SoThatsPrettyBrutal/85cbbfc42fea03c6954d08db28c2626b
    @staticmethod
    def get_loudness_stats(file):
        loudness_args = ['ffmpeg', '-i', file, '-hide_banner', '-nostats', '-vn', '-sn', '-dn', '-af',
                         'loudnorm=I=-16:LRA=20:TP=-1:dual_mono=true:linear=true:print_format=json', '-f', 'null',
                         'NUL']
        loudness_output = subprocess.check_output(loudness_args, stderr=subprocess.STDOUT).decode('utf-8').strip()
        loudness_stats = re.search('^{[^}]*}$', loudness_output, re.MULTILINE)
        return json.loads(loudness_stats.group(0))

    # We expect video at index 0 and audio at index 1, but we still want to inspect streams regardless
    @staticmethod
    def get_stream_index(webm_format, target_codec_type):
        for i in range(len(webm_format['streams'])):
            codec_type = webm_format['streams'][i]['codec_type']
            if codec_type == target_codec_type:
                return i
        return 0

    # Expectation 1: Index 0 stream is video
    def test_video_stream(self):
        self.assertEqual(self.webm_format['streams'][0]['codec_type'], 'video', 'First stream is not video')

    # Expectation 2: Index 1 stream is audio
    def test_audio_stream(self):
        self.assertEqual(self.webm_format['streams'][1]['codec_type'], 'audio', 'Second stream is not audio')

    # Expectation 3: There exists 1 video stream and 1 audio stream
    def test_stream_count(self):
        self.assertEqual(len(self.webm_format['streams']), 2, 'Unexpected number of streams')

    # Files must use the latest release version of FFmpeg.
    def test_encoder_name(self):
        for tag_key in self.webm_format['format']['tags']:
            if tag_key.lower() == 'encoder':
                self.assertTrue(self.webm_format['format']['tags'][tag_key].startswith('Lavf'), 'Incorrect Encoder')

    # Files must use the latest release version of FFmpeg.
    def test_encoder_version(self):
        for tag_key in self.webm_format['format']['tags']:
            if tag_key.lower() == 'encoder':
                # FFmpeg versioning doesn't comply with PEP 440 so we can't use packaging.version
                self.assertTrue(
                    LooseVersion(self.webm_format['format']['tags'][tag_key]) >= LooseVersion('Lavf58.45.100'),
                    'Build is out of date')

    # Files must use the WebM container.
    def test_file_format(self):
        self.assertEqual(self.webm_format['format']['format_name'], 'matroska,webm', 'Incorrect file format')

    # Files must adhere to our size restrictions.
    def test_filesize(self):
        bit_rate = int(self.webm_format['format']['bit_rate'])
        resolution = int(self.webm_format['streams'][self.video_index]['height'])
        # Linear fit approximation, we just want to flag egregious overall bitrates here
        self.assertTrue(bit_rate < resolution * 5000 + 683300, 'File size restriction violated')

    # Files must erase source metadata using -map_metadata -1.
    def test_metadata(self):
        found_source_metadata = False

        for stream in self.webm_format['streams']:
            # Tag entry isn't guaranteed to exist, examples found in VP8 encodes
            for tag_key in stream.get('tags', []):
                if tag_key.lower() != 'encoder' and tag_key.lower() != 'duration':
                    found_source_metadata = True

        # Tag entry is expected to exist here, haven't found examples where that isn't true
        for tag_key in self.webm_format['format']['tags']:
            if tag_key.lower() != 'encoder':
                found_source_metadata = True

        self.assertFalse(found_source_metadata, 'Extraneous source file metadata')

    # Files must erase source menu data using -map_chapters -1.
    def test_chapters(self):
        self.assertTrue(not self.webm_format['chapters'], 'Extraneous menu data')

    # Videos must use the VP9 video codec.
    def test_video_codec(self):
        self.assertEqual(self.webm_format['streams'][self.video_index]['codec_name'], 'vp9', 'Incorrect video codec')

    # Videos must use the yuv420p pixel format.
    def test_pix_fmt(self):
        self.assertEqual(self.webm_format['streams'][self.video_index]['pix_fmt'], 'yuv420p', 'Incorrect pixel format')

    # Videos must identify colorspace
    def test_colorspace(self):
        colorspaces = [('bt709', 'bt709', 'bt709'), ('smpte170m', 'smpte170m', 'smpte170m'),
                       ('bt470bg', 'bt470bg', 'bt470bg')]

        # Colorspace entries do not exist if not specified by the encoder
        color_space = self.webm_format['streams'][self.video_index].get('color_space', '')
        color_transfer = self.webm_format['streams'][self.video_index].get('color_transfer', '')
        color_primaries = self.webm_format['streams'][self.video_index].get('color_primaries', '')

        self.assertIn((color_space, color_transfer, color_primaries), colorspaces, 'Unexpected colorspace')

    # Videos must be encoded at the same framerate as the source file.
    # Motion interpolated videos (60FPS converted) are not allowed.
    def test_framerate(self):
        expected_frame_rates = ['24000/1001', '2997/125', '23976/1000', '24/1', '30000/1001', '19001/634', '1990/83',
                                '2997/100', '30/1']
        avg_frame_rate = self.webm_format['streams'][self.video_index]['avg_frame_rate']
        self.assertIn(avg_frame_rate, expected_frame_rates, 'Unexpected framerate')

    # Audio must use the Opus format.
    def test_audio_codec(self):
        self.assertEqual(self.webm_format['streams'][self.audio_index]['codec_name'], 'opus', 'Incorrect audio codec')

    # Audio must be normalized as described by the AES Streaming Loudness Recommendation.
    def test_loudness_i(self):
        input_i = float(self.loudness_stats['input_i'])
        self.assertTrue(-16.25 <= input_i <= -15.75, 'Unexpected target loudness')

    # Audio must be normalized as described by the AES Streaming Loudness Recommendation.
    def test_loudness_tp(self):
        input_tp = float(self.loudness_stats['input_tp'])
        self.assertTrue(input_tp <= -0.5, 'Unexpected true peak')

    # Audio must use a default bitrate of 192 kbps.
    # Audio must use a bitrate of 320 kbps if the source is a DVD or BD release and the source bitrate is > 320 kbps.
    def test_audio_bitrate(self):
        # Note: libopus defaults to VBR mode so we will allow for variance
        audio_bitrate = int(self.audio_format['format']['bit_rate'])
        self.assertTrue(167000 <= audio_bitrate <= 217000 or 295000 <= audio_bitrate <= 345000,
                        'Unexpected audio bitrate')

    # Audio must use a sampling rate of 48k.
    def test_sample_rate(self):
        self.assertEqual(int(self.webm_format['streams'][self.audio_index]['sample_rate']), 48000,
                         'Incorrect sample rate')

    # Audio must use a two channel stereo mix.
    def test_channels(self):
        self.assertEqual(int(self.webm_format['streams'][self.audio_index]['channels']), 2, 'Incorrect audio channels')

    # Audio must use a two channel stereo mix.
    def test_layout(self):
        self.assertEqual(self.webm_format['streams'][self.audio_index]['channel_layout'], 'stereo',
                         'Incorrect audio layout')
