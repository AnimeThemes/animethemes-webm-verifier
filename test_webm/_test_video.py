"""A collection of tests to verify the file against video encoding standards"""

from ._test_webm import TestWebm


class TestVideo(TestWebm):
    """A collection of tests to verify the file against video encoding standards"""

    # Videos must use the VP9 video codec.
    def test_video_codec(self):
        """Test if the video codec is VP9"""
        video_codec = self.webm_format.get_video_stream_entry('codec_name')
        self.assertEqual(video_codec, 'vp9', 'Incorrect video codec')

    # Videos must use the yuv420p pixel format.
    def test_pix_fmt(self):
        """Test if the pixel format is yuv420p"""
        pix_fmt = self.webm_format.get_video_stream_entry('pix_fmt')
        self.assertEqual(pix_fmt, 'yuv420p', 'Incorrect pixel format')

    # Videos must identify colorspace
    def test_color_space(self):
        """Test if the color space is an accepted value"""
        color_spaces = ['bt709', 'smpte170m', 'bt470bg']

        # Colorspace entries do not exist if not specified by the encoder
        color_space = self.webm_format.get_video_stream_entry('color_space')

        self.assertIn(color_space, color_spaces, 'Unexpected color_space')

    # Videos must identify colorspace
    def test_color_transfer(self):
        """Test if the color transfer is an accepted value"""
        color_transfers = ['bt709', 'smpte170m', 'bt470bg']

        # Colorspace entries do not exist if not specified by the encoder
        color_transfer = self.webm_format.get_video_stream_entry('color_transfer')

        self.assertIn(color_transfer, color_transfers, 'Unexpected color_transfer')

    # Videos must identify colorspace
    def test_color_primaries(self):
        """Test if the color primaries is an accepted value"""
        color_primaries = ['bt709', 'smpte170m', 'bt470bg']

        # Colorspace entries do not exist if not specified by the encoder
        color_primary = self.webm_format.get_video_stream_entry('color_primaries')

        self.assertIn(color_primary, color_primaries, 'Unexpected color_primaries')

    # Videos must be encoded at the same framerate as the source file.
    # Motion interpolated videos (60FPS converted) are not allowed.
    def test_framerate(self):
        """Test if the average framerate of the video stream is 23.976 or 29.997 FPS"""
        expected_frame_rates = [
            '24000/1001',
            '2997/125',
            '23976/1000',
            '24/1',
            '30000/1001',
            '19001/634',
            '1990/83',
            '2997/100',
            '30/1'
        ]

        avg_frame_rate = self.webm_format.get_video_stream_entry('avg_frame_rate')
        self.assertIn(avg_frame_rate, expected_frame_rates, 'Unexpected framerate')
